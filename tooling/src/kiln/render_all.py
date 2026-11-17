from kiln.discover import discover_kinds
from kiln.project import Project
from kiln.render import observed_fixtures, render


def render_all(project: Project, validate: bool = True) -> int:
    """Render every kind cold (nothing observed), then once per render-fixtures/<kind>/observed-*.yaml."""
    failures = []
    for kind in discover_kinds(project.kcl_scripts_dir):
        stages = [(kind, None)] + [(f"{kind} ({f.name})", f) for f in observed_fixtures(project, kind)]
        for label, observed in stages:
            result = render(project, kind, observed_resources=observed, validate=validate)
            if result.returncode == 0:
                print(f"✓ {label}")
            else:
                print(f"✗ {label}")
                print(result.stderr)
                failures.append(label)

    return 1 if failures else 0
