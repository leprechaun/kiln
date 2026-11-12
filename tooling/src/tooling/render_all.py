import sys

from tooling.discover import discover_kinds
from tooling.paths import kcl_scripts_dir
from tooling.render import render


def main() -> None:
    failures = []
    for kind in discover_kinds(kcl_scripts_dir()):
        result = render(kind)
        if result.returncode == 0:
            print(f"✓ {kind}")
        else:
            print(f"✗ {kind}")
            print(result.stderr)
            failures.append(kind)

    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
