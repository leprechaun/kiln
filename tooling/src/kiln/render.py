import os
import subprocess

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


def render(project: Project, kind: str, *extra_args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    env = {**os.environ, **(env or {})}
    env.setdefault("DOCKER_HOST", docker_host())

    return subprocess.run(
        [
            "crossplane",
            "composition",
            "render",
            str(project.render_fixtures_dir / kind.lower() / "xr.yaml"),
            str(project.compositions_dir / kind.lower() / "composition.yaml"),
            str(project.functions_file),
            *extra_args,
        ],
        capture_output=True,
        text=True,
        env=env,
    )
