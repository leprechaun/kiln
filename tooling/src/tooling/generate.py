import re

_LOCAL_IMPORT = re.compile(r"^import \.\w+\s*$\n?", re.MULTILINE)


def _strip_local_imports(source: str) -> str:
    return _LOCAL_IMPORT.sub("", source)


def build_combined_kcl_source(schema_modules: dict[str, str], compose_source: str) -> str:
    parts = [_strip_local_imports(s) for s in schema_modules.values()]
    parts.append(_strip_local_imports(compose_source))
    combined = "\n".join(parts)

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


def generate_xrd(kind: str, group: str, plural: str, spec_schema: dict) -> dict:
    return {
        "apiVersion": "apiextensions.crossplane.io/v1",
        "kind": "CompositeResourceDefinition",
        "metadata": {"name": f"{plural}.{group}"},
        "spec": {
            "group": group,
            "names": {"kind": kind, "plural": plural},
            "scope": "Namespaced",
            "versions": [
                {
                    "name": "v1alpha1",
                    "served": True,
                    "referenceable": True,
                    "schema": {
                        "openAPIV3Schema": {
                            "type": "object",
                            "properties": {"spec": spec_schema},
                        }
                    },
                }
            ],
        },
    }
