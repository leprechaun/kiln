import os
import subprocess
import tempfile
from pathlib import Path

from kiln.project import Project


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


def render(project: Project, kind: str, *extra_args: str, env: dict | None = None) -> subprocess.CompletedProcess:
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

        return subprocess.run(
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
