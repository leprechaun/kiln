import subprocess

from kiln.project import Project


def pull_crds(project: Project) -> int:
    return subprocess.run(
        ["crossplane", "xpkg", "get-crds", str(project.providers_dir), "--output-dir", str(project.crds_dir)]
    ).returncode
