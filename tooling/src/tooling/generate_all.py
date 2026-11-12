import sys

from tooling.discover import discover_kinds
from tooling.generate_manifests import generate_manifests_for
from tooling.paths import compositions_dir, kcl_scripts_dir

DEFAULT_GROUP = "platform.kcl-first.io"


def main() -> None:
    kcl_dir = kcl_scripts_dir()
    failures = []
    for kind in discover_kinds(kcl_dir):
        try:
            generate_manifests_for(
                kind=kind,
                spec_schema=f"{kind}Spec",
                group=DEFAULT_GROUP,
                plural=f"{kind.lower()}s",
                kcl_dir=kcl_dir,
                output_dir=compositions_dir() / kind.lower(),
            )
            print(f"✓ {kind}")
        except Exception as e:
            print(f"✗ {kind}: {e}")
            failures.append(kind)

    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
