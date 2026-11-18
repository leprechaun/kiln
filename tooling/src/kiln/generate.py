import json
import re

from kiln.curate import split_blocks

_LOCAL_IMPORT = re.compile(r"^import \.\w+\s*$\n?", re.MULTILINE)


def _strip_local_imports(source: str) -> str:
    return _LOCAL_IMPORT.sub("", source)


_DOCSTRING_LINE = re.compile(r'^[ \t]+r?""".*?"""[ \t]*\n', re.MULTILINE | re.DOTALL)
_BLANK_RUNS = re.compile(r"\n{3,}")


def _split_tail(block: str) -> tuple[str, str]:
    """Split a schema block into the schema itself and any top-level text that follows it."""
    lines = block.splitlines(keepends=True)
    end = 1
    while end < len(lines) and (not lines[end].strip() or lines[end][0] in " \t"):
        end += 1
    while end > 1 and not lines[end - 1].strip():
        end -= 1  # blank lines belong to the tail, so a dropped schema leaves no gap behind
    return "".join(lines[:end]), "".join(lines[end:])


def _compact(schema: str) -> str:
    """The schema without the blank lines between its attributes (kcl import separates each documented
    attribute with one; once docstrings are gone they are about half of the generated source).
    A schema holding a multi-line string is left alone, since its blank lines may be part of the string."""
    if '"""' in schema or "'''" in schema:
        return schema
    return "".join(line for line in schema.splitlines(keepends=True) if line.strip())


def _references(text: str, names: set[str]) -> set[str]:
    return {name for name in names if re.search(rf"\b{re.escape(name)}\b", text)}


def _shake_schemas(modules: list[str], compose_source: str) -> list[str]:
    """Drop docstrings, and every schema the compose function cannot reach, from the schema modules.

    Docstrings are for people reading the schema files; the generated source only has to compile.
    Anything that is not a schema (imports are already gone; aliases, lambdas, comments) is kept.
    """
    parsed = []  # per module: (preamble, [(name, schema text, tail)])
    for module in modules:
        preamble, blocks = split_blocks(_DOCSTRING_LINE.sub("", module))
        parsed.append((preamble, [(name, *_split_tail(block)) for name, block in blocks.items()]))

    schemas = {name: text for _, blocks in parsed for name, text, _ in blocks}
    always_kept = compose_source + "".join(preamble + tail for preamble, blocks in parsed for _, _, tail in blocks)

    keep = _references(always_kept, set(schemas))
    frontier = set(keep)
    while frontier:
        for reached in _references(schemas[frontier.pop()], set(schemas) - keep):
            keep.add(reached)
            frontier.add(reached)

    return [
        _BLANK_RUNS.sub("\n\n", preamble + "".join((_compact(text) if name in keep else "") + tail for name, text, tail in blocks))
        for preamble, blocks in parsed
    ]


def build_combined_kcl_source(schema_modules: dict[str, str], compose_source: str) -> str:
    modules = [_strip_local_imports(s) for s in schema_modules.values()]
    compose = _strip_local_imports(compose_source)
    parts = [*_shake_schemas(modules, compose), compose]
    combined = _BLANK_RUNS.sub("\n\n", "\n".join(parts)).lstrip("\n")

    for module_name in schema_modules:
        combined = re.sub(rf"\b{re.escape(module_name)}\.", "", combined)

    return combined


def enforce_naming_convention(kind: str, compose_source: str) -> None:
    expected = f"compose{kind}"
    pattern = re.compile(rf"^{re.escape(expected)}\s*=\s*lambda\s+oxr\s*,\s*ocds\b", re.MULTILINE)
    if not pattern.search(compose_source):
        raise ValueError(
            f"Expected a `{expected} = lambda oxr, ocds -> ...` function in the compose source, found none"
        )


def _provider_config_wrapper(group: str, provider_config: dict[str, str]) -> str:
    """KCL that gives a default providerConfigRef to every composed managed resource without one.

    A managed resource is anything with `spec.forProvider` outside the project's own API group, so
    the XR (returned to report status), child XRs and plain Kubernetes objects are left alone.
    A missing dict key is Undefined rather than None in KCL, so the tests use truthiness.
    """
    return (
        f'_kilnProviderConfigRef = {{kind = "{provider_config["kind"]}", name = "{provider_config["name"]}"}}\n'
        "_kilnIsManaged = lambda r: any -> bool {\n"
        f'    "forProvider" in (r?.spec or {{}}) and not (r?.apiVersion or "").startswith("{group}/")\n'
        "}\n"
        "_kilnWithProviderConfig = lambda r: any -> any {\n"
        "    r | {spec.providerConfigRef = _kilnProviderConfigRef} "
        "if _kilnIsManaged(r) and not r?.spec?.providerConfigRef else r\n"
        "}\n"
    )


def _declared_spec_wrapper(spec_fields: list[str]) -> str:
    """KCL that gives the compose function the observed XR with only its declared spec fields.

    A real XR's spec also carries fields Crossplane adds (`spec.crossplane`, and on legacy XRs
    `compositionRef`, `resourceRefs`, ...). Dropping them here lets spec schemas stay closed.
    """
    return (
        f"_kilnSpecFields = {json.dumps(spec_fields)}\n"
        '_kilnObservedXr = option("params").oxr\n'
        "_kilnOxr = _kilnObservedXr | {spec = {k: v for k, v in _kilnObservedXr.spec if k in _kilnSpecFields}} "
        "if _kilnObservedXr?.spec else _kilnObservedXr\n"
    )


def generate_composition(
    kind: str,
    group: str,
    combined_source: str,
    provider_config: dict[str, str] | None = None,
    spec_fields: list[str] | None = None,
) -> dict:
    """The Composition for `kind`. With `spec_fields` (the spec schema's declared fields), the compose
    function sees only those fields of the observed XR's spec."""
    enforce_naming_convention(kind, combined_source)
    compose_fn = f"compose{kind}"
    source = combined_source + "\n"
    if spec_fields is not None:
        source += _declared_spec_wrapper(spec_fields)
        call = f'{compose_fn}(_kilnOxr, option("params").ocds)'
    else:
        call = f'{compose_fn}(option("params").oxr, option("params").ocds)'
    if provider_config:
        source += (
            _provider_config_wrapper(group, provider_config)
            + f"items = [_kilnWithProviderConfig(r) for r in {call}]\n"
        )
    else:
        source += f"items = {call}\n"

    return {
        "apiVersion": "apiextensions.crossplane.io/v1",
        "kind": "Composition",
        "metadata": {"name": f"{kind.lower()}-kcl-first"},
        "spec": {
            "compositeTypeRef": {"apiVersion": f"{group}/v1alpha1", "kind": kind},
            "mode": "Pipeline",
            "pipeline": [
                {
                    "step": "compose",
                    "functionRef": {"name": "function-kcl"},
                    "input": {
                        "apiVersion": "krm.kcl.dev/v1alpha1",
                        "kind": "KCLInput",
                        "spec": {"source": source},
                    },
                },
                {"step": "auto-ready", "functionRef": {"name": "function-auto-ready"}},
            ],
        },
    }


def generate_xrd(
    kind: str, group: str, plural: str, spec_schema: dict, status_schema: dict | None = None, scope: str = "Namespaced"
) -> dict:
    properties = {"spec": spec_schema}
    if status_schema is not None:
        properties["status"] = status_schema
    return {
        "apiVersion": "apiextensions.crossplane.io/v2",
        "kind": "CompositeResourceDefinition",
        "metadata": {"name": f"{plural}.{group}"},
        "spec": {
            "group": group,
            "names": {"kind": kind, "plural": plural},
            "scope": scope,
            "versions": [
                {
                    "name": "v1alpha1",
                    "served": True,
                    "referenceable": True,
                    "schema": {
                        "openAPIV3Schema": {
                            "type": "object",
                            "properties": properties,
                        }
                    },
                }
            ],
        },
    }


def source_contributors(source: str, top: int = 5) -> list[tuple[str, int]]:
    """The largest parts of a generated KCL source, by size in bytes: each schema, and everything else."""
    _, blocks = split_blocks(source)
    parts = [(f"schema {name}", len(_split_tail(block)[0].encode())) for name, block in blocks.items()]
    schemas_total = sum(size for _, size in parts)
    parts.append(("compose function and other code", len(source.encode()) - schemas_total))
    return sorted(parts, key=lambda p: p[1], reverse=True)[:top]
