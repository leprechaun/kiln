import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

from tooling.curate import curate_provider_schema
from tooling.paths import kcl_scripts_dir


def _kcl_import(crd_file: Path, work_dir: Path) -> Path:
    subprocess.run(
        ["kcl", "import", "-m", "crd", str(crd_file)],
        cwd=work_dir,
        check=True,
        capture_output=True,
    )
    candidates = [p for p in work_dir.glob("models/*/*.k")]
    if len(candidates) != 1:
        raise RuntimeError(
            f"Expected exactly one generated schema file under models/*/*.k, found {len(candidates)}: {candidates}"
        )
    return candidates[0]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import a provider CRD and curate it down to just SpecForProvider and its dependencies."
    )
    parser.add_argument("crd_file", type=Path, help="Path to a raw CRD YAML file, e.g. from crds/")
    parser.add_argument(
        "--print", dest="print_only", action="store_true", help="Print the curated schema instead of appending it"
    )
    parser.add_argument(
        "--schemas-file",
        type=Path,
        default=None,
        help="File to append the curated schema to (default: kcl-scripts/schemas_providers.k)",
    )
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as work_dir:
        generated = _kcl_import(args.crd_file.resolve(), Path(work_dir))
        curated = curate_provider_schema(generated.read_text())

    if args.print_only:
        sys.stdout.write(curated)
        return

    schemas_file = args.schemas_file or (kcl_scripts_dir() / "schemas_providers.k")
    with schemas_file.open("a") as f:
        f.write("\n")
        f.write(curated)

    print(f"Appended curated schema to {schemas_file}")


if __name__ == "__main__":
    main()
