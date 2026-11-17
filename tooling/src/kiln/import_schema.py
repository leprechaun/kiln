import subprocess
import sys
import tempfile
from pathlib import Path

from kiln.curate import curate_provider_schema, merge_schemas, split_blocks
from kiln.schema_names import read_crd_identity, schema_prefixes, to_group_prefixed_names
from kiln.project import Project


def _kcl_import(crd_file: Path, work_dir: Path) -> str:
    subprocess.run(
        ["kcl", "import", "-m", "crd", str(crd_file)],
        cwd=work_dir,
        check=True,
        capture_output=True,
    )
    # kcl 0.12 wrote every schema into one file; 0.13 writes one file per schema. Either way the
    # schemas share a namespace, so keep each file's schemas and drop its header and imports.
    generated = sorted(work_dir.glob("models/*/*.k"))
    if not generated:
        raise RuntimeError("kcl import produced no schema files under models/*/*.k")
    return "".join("".join(split_blocks(f.read_text())[1].values()) for f in generated)


def import_schema(project: Project, crd_file: Path, print_only: bool = False, schemas_file: Path | None = None) -> int:
    crd = read_crd_identity(crd_file)
    with tempfile.TemporaryDirectory() as work_dir:
        generated = _kcl_import(crd_file.resolve(), Path(work_dir))
    # Curate before renaming so a name collision only matters between schemas we actually keep.
    curated = to_group_prefixed_names(curate_provider_schema(generated), crd)

    if print_only:
        sys.stdout.write(curated)
        return 0

    schemas_file = schemas_file or (project.kcl_scripts_dir / "schemas_providers.k")
    existing = schemas_file.read_text() if schemas_file.exists() else ""
    schemas_file.write_text(merge_schemas(existing, curated, schema_prefixes(crd)))

    print(f"Updated curated schemas in {schemas_file}")
    return 0
