import json
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

from kiln.generate import build_combined_kcl_source, generate_composition, generate_xrd
from kiln.normalize import normalize_openapi_schema


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


class _LiteralStr(str):
    """A string YAML should write as a `|` block, so embedded KCL stays readable."""


class _ReadableDumper(yaml.SafeDumper):
    pass


_ReadableDumper.add_representer(
    _LiteralStr, lambda dumper, data: dumper.represent_scalar("tag:yaml.org,2002:str", str(data), style="|")
)


def _existing_scope(xrd_file: Path) -> str | None:
    if not xrd_file.is_file():
        return None
    return (yaml.safe_load(xrd_file.read_text()) or {}).get("spec", {}).get("scope")


_SOURCE_PLACEHOLDER = "__KILN_KCL_SOURCE__"
COMPOSITION_KCL = "composition.k"


def _write_composition(composition: dict, output_format: str, output_dir: Path) -> None:
    if output_format == "yaml":
        [step] = [s for s in composition["spec"]["pipeline"] if s["step"] == "compose"]
        step["input"]["spec"]["source"] = _LiteralStr(step["input"]["spec"]["source"])
        (output_dir / "composition.yaml").write_text(yaml.dump(composition, Dumper=_ReadableDumper, sort_keys=False))
        return

    if output_format != "jsonnet":
        raise ValueError(f"unknown output format {output_format!r}")

    [step] = [s for s in composition["spec"]["pipeline"] if s["step"] == "compose"]
    source = step["input"]["spec"]["source"]
    step["input"]["spec"]["source"] = _SOURCE_PLACEHOLDER
    jsonnet = json.dumps(composition, indent=2).replace(
        json.dumps(_SOURCE_PLACEHOLDER), f"importstr '{COMPOSITION_KCL}'"
    )
    (output_dir / COMPOSITION_KCL).write_text(source)
    (output_dir / "composition.jsonnet").write_text(jsonnet + "\n")


def generate_manifests_for(
    kind: str,
    spec_schema: str,
    group: str,
    plural: str,
    kcl_dir: Path,
    output_dir: Path,
    output_format: str = "yaml",
    scope: str = "Namespaced",
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
    status_name = f"{kind}Status"
    status_schema = normalize_openapi_schema(doc, status_name) if status_name in doc["components"]["schemas"] else None
    xrd = generate_xrd(kind=kind, group=group, plural=plural, spec_schema=schema, status_schema=status_schema, scope=scope)

    output_dir.mkdir(parents=True, exist_ok=True)
    previous_scope = _existing_scope(output_dir / "xrd.yaml")
    _write_composition(composition, output_format, output_dir)
    (output_dir / "xrd.yaml").write_text(yaml.dump(xrd, sort_keys=False))
    if previous_scope and previous_scope != scope:
        print(
            f"kiln: {kind} scope changed from {previous_scope} to {scope}. An XRD's scope is immutable: "
            f"delete the XRD (and its XRs) on the cluster before applying this one.",
            file=sys.stderr,
        )
