import argparse
import json
import shutil
import subprocess
from pathlib import Path

import yaml

from tooling.generate import build_combined_kcl_source, generate_composition, generate_xrd
from tooling.normalize import normalize_openapi_schema


def _run_kcl_doc_generate(kcl_dir: Path) -> dict:
    docs_dir = kcl_dir / "docs"
    subprocess.run(
        ["kcl", "doc", "generate", "--format", "openapi"],
        cwd=kcl_dir,
        check=True,
        capture_output=True,
    )
    try:
        [doc_file] = docs_dir.glob("*.json")
        return json.loads(doc_file.read_text())
    finally:
        shutil.rmtree(docs_dir, ignore_errors=True)


def generate_manifests_for(
    kind: str, spec_schema: str, group: str, plural: str, kcl_dir: Path, output_dir: Path
) -> None:
    compose_source = (kcl_dir / f"{kind.lower()}.k").read_text()
    providers_source = (kcl_dir / "schemas_providers.k").read_text()
    compositions_source = (kcl_dir / "schemas_compositions.k").read_text()

    combined_source = build_combined_kcl_source(
        {"schemas_providers": providers_source, "schemas_compositions": compositions_source}, compose_source
    )
    composition = generate_composition(kind=kind, group=group, combined_source=combined_source)

    doc = _run_kcl_doc_generate(kcl_dir)
    schema = normalize_openapi_schema(doc, spec_schema)
    xrd = generate_xrd(kind=kind, group=group, plural=plural, spec_schema=schema)

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "composition.yaml").write_text(yaml.dump(composition, sort_keys=False))
    (output_dir / "xrd.yaml").write_text(yaml.dump(xrd, sort_keys=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a Composition and XRD from a kcl-scripts package.")
    parser.add_argument("--kind", required=True, help="Composite kind, e.g. IAMRole")
    parser.add_argument("--spec-schema", required=True, help="Name of the composition spec schema, e.g. IAMRoleSpec")
    parser.add_argument("--group", required=True, help="API group, e.g. platform.kcl-first.io")
    parser.add_argument("--plural", required=True, help="Plural resource name, e.g. iamroles")
    parser.add_argument("--kcl-dir", required=True, type=Path, help="Path to the kcl-scripts directory")
    parser.add_argument("--output-dir", required=True, type=Path, help="Where to write composition.yaml and xrd.yaml")
    args = parser.parse_args()

    generate_manifests_for(
        kind=args.kind,
        spec_schema=args.spec_schema,
        group=args.group,
        plural=args.plural,
        kcl_dir=args.kcl_dir,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()
