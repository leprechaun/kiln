from kiln.discover import discover_kinds
from kiln.project import Project
from kiln.render import expected_error, invalid_fixtures, observed_fixtures, render


def _check_invalid(project: Project, kind: str, fixture, validate: bool) -> str | None:
    """Why the invalid fixture did not fail as expected, or None when it did."""
    expected = expected_error(fixture)
    if expected is None:
        return f"{fixture.name} has no `# expect-error: <text>` comment saying which error it must fail with"
    result = render(project, kind, validate=validate, xr=fixture)
    if result.returncode == 0:
        return f"rendered without error; expected one containing {expected!r}"
    output = result.stderr + result.stdout
    if expected not in output:
        return f"failed, but not with {expected!r}:\n{result.stderr}"
    return None


def render_all(project: Project, validate: bool = True) -> int:
    """Render every kind cold (nothing observed), then once per render-fixtures/<kind>/observed-*.yaml,
    then check that each render-fixtures/<kind>/invalid-*.yaml fails with the error it names."""
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

        for fixture in invalid_fixtures(project, kind):
            label = f"{kind} ({fixture.name} is rejected)"
            problem = _check_invalid(project, kind, fixture, validate)
            if problem is None:
                print(f"✓ {label}")
            else:
                print(f"✗ {label}")
                print(f"  {problem}")
                failures.append(label)

    return 1 if failures else 0
