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
        _BLANK_RUNS.sub("\n\n", preamble + "".join((text if name in keep else "") + tail for name, text, tail in blocks))
        for preamble, blocks in parsed
    ]


def build_combined_kcl_source(schema_modules: dict[str, str], compose_source: str) -> str:
    modules = [_strip_local_imports(s) for s in schema_modules.values()]
    compose = _strip_local_imports(compose_source)
    parts = [*_shake_schemas(modules, compose), compose]
    combined = _BLANK_RUNS.sub("\n\n", "\n".join(parts))

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


def generate_composition(kind: str, group: str, combined_source: str) -> dict:
    enforce_naming_convention(kind, combined_source)
    compose_fn = f"compose{kind}"
    source = combined_source + f'\nitems = {compose_fn}(option("params").oxr, option("params").ocds)\n'

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
