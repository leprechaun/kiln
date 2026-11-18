import json
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path

import yaml

from kiln.generate import build_combined_kcl_source, generate_composition, generate_xrd, source_contributors
from kiln.curate import split_blocks, without_docstring
from kiln.kcl import KclError, run_kcl
from kiln.normalize import normalize_openapi_schema
from kiln.project import Project


@dataclass(frozen=True)
class GenerateResult:
    """What generating a kind produced besides its files: warnings for the caller to show the user."""

    warnings: list[str]


def _run_kcl_doc_generate(kcl_dir: Path) -> dict:
    # kcl writes its output under --target, so run it in a scratch directory and leave kcl_dir untouched.
    with tempfile.TemporaryDirectory() as work_dir:
        out = Path(work_dir) / "out"
        out.mkdir()
        run_kcl(
            ["doc", "generate", "--file-path", str(kcl_dir.resolve()), "--format", "openapi", "--target", str(out)],
            work_dir=Path(work_dir),
        )
        docs = sorted((out / "docs").glob("*.json"))
        if len(docs) != 1:
            names = ", ".join(d.name for d in docs)
            raise KclError(
                f"kcl doc generate produced {len(docs)} docs in {out}/docs, expected 1" + (f": {names}" if docs else "")
            )
        return json.loads(docs[0].read_text())


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


# kubectl's client-side apply stores the whole object, as JSON, in one annotation, and Kubernetes
# caps all of an object's annotations together at this many bytes.
ANNOTATION_LIMIT = 262144
SIZE_WARNING_THRESHOLD = 0.8


_ANY_INDEX_SIGNATURE = re.compile(r"^[ \t]+\[(?:\w+\s*:\s*)?str\]\s*:\s*any\s*$", re.MULTILINE)


def _index_signature_warning(compositions_source: str, spec_schema: str) -> str | None:
    block = split_blocks(compositions_source)[1].get(spec_schema, "")
    if not _ANY_INDEX_SIGNATURE.search(without_docstring(block)):
        return None
    return (
        f"kiln: {spec_schema} ends in `[str]: any`, which is no longer needed: the Composition passes the "
        f"compose function only declared spec fields, and the XRD ignores it. Remove it so a misspelt "
        f"spec field fails in `kcl test`. If your kiln skill says to keep it, the installed skill is out "
        f"of date: run `kiln install-skills --force`."
    )


def _size_warning(kind: str, composition: dict) -> str | None:
    size = len(json.dumps(composition, separators=(",", ":")).encode())
    if size < ANNOTATION_LIMIT * SIZE_WARNING_THRESHOLD:
        return None
    [step] = [s for s in composition["spec"]["pipeline"] if s["step"] == "compose"]
    contributors = "\n".join(
        f"  {size_kb:>7.1f} KB  {name}"
        for name, size_kb in ((n, b / 1024) for n, b in source_contributors(step["input"]["spec"]["source"]))
    )
    return (
        f"kiln: {kind} composition is {size / 1024:.0f} KB, close to or over the {ANNOTATION_LIMIT // 1024} KB "
        f"Kubernetes annotation limit (kubectl apply would fail with \"metadata.annotations: Too long\").\n"
        f"Largest parts of the generated KCL source:\n{contributors}\n"
        f"Unused provider schemas are already pruned; do not trim imported schemas by hand. Reduce what the "
        f"function references, split the kind, or apply with server-side apply (kubectl apply --server-side)."
    )


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
    compose_file: Path,
    output_format: str = "yaml",
    scope: str = "Namespaced",
    provider_config: dict[str, str] | None = None,
) -> GenerateResult:
    compose_source = compose_file.read_text()
    providers_source = (kcl_dir / "schemas_providers.k").read_text()
    compositions_source = (kcl_dir / "schemas_compositions.k").read_text()

    combined_source = build_combined_kcl_source(
        {"schemas_providers": providers_source, "schemas_compositions": compositions_source}, compose_source
    )
    doc = _run_kcl_doc_generate(kcl_dir)
    schema = normalize_openapi_schema(doc, spec_schema)
    composition = generate_composition(
        kind=kind,
        group=group,
        combined_source=combined_source,
        provider_config=provider_config,
        spec_fields=list(schema.get("properties", {})),
    )
    size_warning = _size_warning(kind, composition)
    index_signature_warning = _index_signature_warning(compositions_source, spec_schema)
    status_name = f"{kind}Status"
    status_schema = normalize_openapi_schema(doc, status_name) if status_name in doc["components"]["schemas"] else None
    xrd = generate_xrd(kind=kind, group=group, plural=plural, spec_schema=schema, status_schema=status_schema, scope=scope)

    output_dir.mkdir(parents=True, exist_ok=True)
    previous_scope = _existing_scope(output_dir / "xrd.yaml")
    _write_composition(composition, output_format, output_dir)
    (output_dir / "xrd.yaml").write_text(yaml.dump(xrd, sort_keys=False))
    warnings = []
    if previous_scope and previous_scope != scope:
        warnings.append(
            f"kiln: {kind} scope changed from {previous_scope} to {scope}. An XRD's scope is immutable: "
            f"delete the XRD (and its XRs) on the cluster before applying this one."
        )
    if size_warning:
        warnings.append(size_warning)
    if index_signature_warning:
        warnings.append(index_signature_warning)
    return GenerateResult(warnings=warnings)


def generate_kind(
    project: Project, name: str, spec_schema: str | None = None, plural: str | None = None, scope: str | None = None
) -> GenerateResult:
    """Generate the manifests for the kind called `name`, with every convention taken from the project."""
    kind = project.kind(name, spec_schema=spec_schema, plural=plural, scope=scope)
    if not kind.source_file.is_file():
        raise ValueError(
            f"no compose function found for {kind.name}: expected {kind.source_file} to define "
            f"`compose{kind.name} = lambda oxr, ocds -> ...`"
        )
    return generate_manifests_for(
        kind=kind.name,
        spec_schema=kind.spec_schema,
        group=project.group,
        plural=kind.plural,
        kcl_dir=project.kcl_scripts_dir,
        output_dir=kind.output_dir,
        output_format=project.format,
        scope=kind.scope,
        provider_config=kind.provider_config,
        compose_file=kind.source_file,
    )
