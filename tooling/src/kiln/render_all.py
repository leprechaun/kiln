from kiln.discover import discover_kinds
from kiln.project import Project
from kiln.render import render


def render_all(project: Project) -> int:
    failures = []
    for kind in discover_kinds(project.kcl_scripts_dir):
        result = render(project, kind)
        if result.returncode == 0:
            print(f"✓ {kind}")
        else:
            print(f"✗ {kind}")
            print(result.stderr)
            failures.append(kind)

    return 1 if failures else 0
