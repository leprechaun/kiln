from kiln.discover import discover_kinds
from kiln.generate_manifests import generate_manifests_for
from kiln.project import Project


def generate_all(project: Project) -> int:
    failures = []
    for kind in discover_kinds(project.kcl_scripts_dir):
        try:
            generate_manifests_for(
                kind=kind,
                spec_schema=f"{kind}Spec",
                group=project.group,
                plural=f"{kind.lower()}s",
                kcl_dir=project.kcl_scripts_dir,
                output_dir=project.compositions_dir / kind.lower(),
                output_format=project.format,
                scope=project.scope_for(kind),
                provider_config=project.provider_config_for(kind),
            )
            print(f"✓ {kind}")
        except Exception as e:
            print(f"✗ {kind}: {e}")
            failures.append(kind)

    return 1 if failures else 0
