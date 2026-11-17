import os
import subprocess
import tempfile
from pathlib import Path

import yaml

from kiln.project import Project
from kiln.validate import KindIndex, check_rendered


def docker_host() -> str:
    host = os.environ.get("DOCKER_HOST")
    if host:
        return host
    result = subprocess.run(
        ["docker", "context", "inspect", "--format", "{{.Endpoints.docker.Host}}"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _failure(message: str, returncode: int = 1) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout="", stderr=message + "\n")


def _evaluate_jsonnet(composition: Path, into: Path) -> tuple[Path | None, subprocess.CompletedProcess | None]:
    try:
        result = subprocess.run(["jsonnet", str(composition)], capture_output=True, text=True)
    except FileNotFoundError:
        return None, _failure(
            "kiln: format = \"jsonnet\" needs the `jsonnet` binary on PATH to render (go-jsonnet or C++ jsonnet)", 127
        )
    if result.returncode != 0:
        return None, result
    evaluated = into / "composition.yaml"
    evaluated.write_text(result.stdout)  # JSON is valid YAML
    return evaluated, None


def observed_fixtures(project: Project, kind: str) -> list[Path]:
    """The observed-state fixtures `render-all` renders, one render each: render-fixtures/<kind>/observed-*.yaml."""
    return sorted(
        p for p in (project.render_fixtures_dir / kind.lower()).glob("observed-*") if p.suffix in (".yaml", ".yml")
    )


def _observed_file(observed: Path, into: Path) -> tuple[Path | None, subprocess.CompletedProcess | None]:
    """A single multi-document file holding the observed resources at `observed` (a file or a directory)."""
    if observed.is_file():
        return observed, None
    if not observed.is_dir():
        return None, _failure(f"kiln: --observed-resources {observed}: no such file or directory")
    files = sorted(p for p in observed.iterdir() if p.is_file() and p.suffix in (".yaml", ".yml"))
    if not files:
        return None, _failure(f"kiln: --observed-resources {observed}: the directory has no .yaml or .yml files")
    combined = into / "observed.yaml"
    combined.write_text("\n---\n".join(f.read_text().strip("\n") for f in files) + "\n")
    return combined, None


def xr_scope(project: Project, kind: str) -> str:
    """The scope the kind's XRD was generated with (what gets deployed), else the one kiln.toml sets."""
    xrd = project.compositions_dir / kind.lower() / "xrd.yaml"
    if xrd.is_file():
        scope = ((yaml.safe_load(xrd.read_text()) or {}).get("spec") or {}).get("scope")
        if scope:
            return scope
    return project.scope_for(kind)


def _validated(project: Project, kind: str, result: subprocess.CompletedProcess) -> subprocess.CompletedProcess:
    try:
        documents = [d for d in yaml.safe_load_all(result.stdout) if isinstance(d, dict)]
    except yaml.YAMLError as e:
        return _failure(f"kiln: could not parse the render output to validate it: {e}")
    errors = check_rendered(documents, KindIndex.load(project), xr_scope(project, kind))
    if not errors:
        return result
    report = "\n".join(f"  {e}" for e in errors)
    return subprocess.CompletedProcess(
        args=result.args,
        returncode=1,
        stdout=result.stdout,
        stderr=result.stderr
        + f"kiln: {len(errors)} problem(s) in the rendered resources; the cluster would reject them:\n{report}\n",
    )


def render(
    project: Project,
    kind: str,
    observed_resources: Path | None = None,
    validate: bool = True,
    env: dict | None = None,
) -> subprocess.CompletedProcess:
    env = {**os.environ, **(env or {})}
    env.setdefault("DOCKER_HOST", docker_host())
    kind_dir = project.compositions_dir / kind.lower()

    with tempfile.TemporaryDirectory() as scratch:
        if project.format == "jsonnet":
            composition, failure = _evaluate_jsonnet(kind_dir / "composition.jsonnet", Path(scratch))
            if failure:
                return failure
        else:
            composition = kind_dir / "composition.yaml"

        extra_args = []
        if observed_resources is not None:
            observed, failure = _observed_file(Path(observed_resources), Path(scratch))
            if failure:
                return failure
            extra_args = ["--observed-resources", str(observed)]

        result = subprocess.run(
            [
                "crossplane",
                "composition",
                "render",
                str(project.render_fixtures_dir / kind.lower() / "xr.yaml"),
                str(composition),
                str(project.functions_file),
                *extra_args,
            ],
            capture_output=True,
            text=True,
            env=env,
        )

    if result.returncode != 0 or not validate:
        return result
    return _validated(project, kind, result)
