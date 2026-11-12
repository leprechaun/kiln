import argparse
import os
import subprocess
import sys

from tooling.paths import compositions_dir, functions_file, render_fixtures_dir


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


def render(kind: str, *extra_args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    env = {**os.environ, **(env or {})}
    env.setdefault("DOCKER_HOST", docker_host())

    return subprocess.run(
        [
            "crossplane",
            "composition",
            "render",
            str(render_fixtures_dir() / kind.lower() / "xr.yaml"),
            str(compositions_dir() / kind.lower() / "composition.yaml"),
            str(functions_file()),
            *extra_args,
        ],
        capture_output=True,
        text=True,
        env=env,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a kind's generated Composition against a sample XR.")
    parser.add_argument("kind", help="Kind directory name under render-fixtures/ and manifests/crossplane-compositions/, e.g. iamrole")
    parser.add_argument("--observed-resources", help="Path to mocked observed resources, passed through to crossplane")
    args = parser.parse_args()

    extra_args = []
    if args.observed_resources:
        extra_args = ["--observed-resources", args.observed_resources]

    result = render(args.kind, *extra_args)
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
