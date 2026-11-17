"""Check rendered composed resources against the CRDs in crds/ and the project's own XRDs.

Crossplane render runs the composition but checks nothing about what it emits, so a resource of
the wrong scope or shape renders cleanly and only fails when the cluster applies it.
"""

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from kiln.project import Project

RESOURCE_NAME_ANNOTATION = "crossplane.io/composition-resource-name"

# Upbound providers express most required parameters as CEL rules with this message, not in `required`.
_REQUIRED_PARAMETER = re.compile(r"^spec\.forProvider\.([\w]+) is a required parameter$")
# Management policies that make the provider create or update the external resource.
_WRITING_POLICIES = {"*", "Create", "Update"}


@dataclass(frozen=True)
class KindInfo:
    group: str
    version: str
    kind: str
    scope: str
    schema: dict  # openAPIV3Schema
    source: Path

    @property
    def api_version(self) -> str:
        return f"{self.group}/{self.version}"


# CRDs are large; libyaml's loader reads them several times faster than the pure-Python one.
_Loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


def _read_yaml_docs(path: Path) -> list[dict]:
    try:
        return [d for d in yaml.load_all(path.read_text(), Loader=_Loader) if isinstance(d, dict)]
    except yaml.YAMLError:
        return []


def _infos(doc: dict, path: Path) -> list[KindInfo]:
    spec = doc.get("spec") or {}
    if doc.get("kind") == "CustomResourceDefinition":
        kind = spec.get("names", {}).get("kind")
    elif doc.get("kind") == "CompositeResourceDefinition":
        kind = spec.get("names", {}).get("kind")
    else:
        return []
    return [
        KindInfo(
            group=spec.get("group", ""),
            version=v["name"],
            kind=kind,
            # A CRD always states its scope; a v2 XRD without one is Namespaced. "" means unknown.
            scope=spec.get("scope", "" if doc["kind"] == "CustomResourceDefinition" else "Namespaced"),
            schema=(v.get("schema") or {}).get("openAPIV3Schema") or {},
            source=path,
        )
        for v in spec.get("versions", [])
        if kind and "name" in v
    ]


class KindIndex:
    """Every kind Kiln knows the scope and schema of: provider CRDs and the project's generated XRDs."""

    def __init__(self, infos: list[KindInfo]):
        self._by_api = {(i.api_version, i.kind): i for i in infos}

    @classmethod
    def load(cls, project: Project) -> "KindIndex":
        infos = []
        for path in sorted(project.crds_dir.glob("**/*.y*ml")):
            for doc in _read_yaml_docs(path):
                infos.extend(_infos(doc, path))
        for path in sorted(project.compositions_dir.glob("*/xrd.yaml")):
            for doc in _read_yaml_docs(path):
                infos.extend(_infos(doc, path))
        return cls(infos)

    def get(self, api_version: str, kind: str) -> KindInfo | None:
        return self._by_api.get((api_version, kind))

    def namespaced_alternatives(self, info: KindInfo) -> list[KindInfo]:
        """Namespaced kinds of the same name, preferring the `.m.` twin of a legacy provider group."""
        same_kind = [i for i in self._by_api.values() if i.kind == info.kind and i.scope == "Namespaced"]
        twins = [i for i in same_kind if i.group.replace(".m.", ".") == info.group]
        return sorted(twins or same_kind, key=lambda i: i.api_version)

    def __len__(self) -> int:
        return len(self._by_api)


def _type_name(value) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def _type_matches(value, expected: str) -> bool:
    actual = _type_name(value)
    return actual == expected or (expected == "number" and actual == "integer")


def validate_value(value, schema: dict, path: str) -> list[str]:
    """Errors for `value` against a structural OpenAPI v3 schema (the subset Kubernetes CRDs use)."""
    if value is None or not schema:
        return []  # null means "unset" in an apply; an empty schema accepts anything
    errors = []
    expected = schema.get("type")
    if expected and not _type_matches(value, expected):
        hint = ""
        if expected == "object" and isinstance(value, list):
            hint = " (this API takes a single object here, not a one-item list)"
        elif expected == "array" and isinstance(value, dict):
            hint = " (this API takes a list here)"
        elif expected == "string" and isinstance(value, (dict, list)):
            hint = " (if this is a JSON document, serialize it, e.g. with json.encode)"
        return [f"{path}: expected {expected}, got {_type_name(value)}{hint}"]

    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} is not one of {schema['enum']}")

    if isinstance(value, dict):
        properties = schema.get("properties")
        additional = schema.get("additionalProperties")
        for name in schema.get("required", []):
            if value.get(name) is None:
                errors.append(f"{path}.{name}: required field is missing")
        for name, child in value.items():
            child_path = f"{path}.{name}"
            if properties is not None and name in properties:
                errors.extend(validate_value(child, properties[name], child_path))
            elif isinstance(additional, dict):
                errors.extend(validate_value(child, additional, child_path))
            elif properties is not None and additional is not True and not schema.get(
                "x-kubernetes-preserve-unknown-fields"
            ):
                errors.append(f"{child_path}: field not declared in schema")
    elif isinstance(value, list) and "items" in schema:
        for i, item in enumerate(value):
            errors.extend(validate_value(item, schema["items"], f"{path}[{i}]"))
    return errors


def _required_parameters(spec_schema: dict, spec: dict) -> list[str]:
    """Errors for Upbound's CEL-expressed required parameters (`spec.forProvider.X is a required parameter`)."""
    policies = spec.get("managementPolicies") or ["*"]
    if not _WRITING_POLICIES.intersection(policies):
        return []  # observe-only resources need no parameters
    errors = []
    for rule in spec_schema.get("x-kubernetes-validations", []):
        match = _REQUIRED_PARAMETER.match(rule.get("message", ""))
        if not match:
            continue
        field = match.group(1)
        if (spec.get("forProvider") or {}).get(field) is None and (spec.get("initProvider") or {}).get(field) is None:
            errors.append(f".spec.forProvider.{field}: required parameter is missing (set it in forProvider or initProvider)")
    return errors


def validate_resource(resource: dict, info: KindInfo) -> list[str]:
    """Schema errors in a composed resource's spec. Only spec is checked: apiVersion, kind and
    metadata are standard, and Crossplane ignores status on composed resources."""
    properties = info.schema.get("properties") or {}
    spec_schema = properties.get("spec")
    spec = resource.get("spec")
    if spec_schema is None:
        return []
    if spec is None:
        return [".spec: required field is missing"] if "spec" in info.schema.get("required", []) else []
    errors = validate_value(spec, spec_schema, ".spec")
    if isinstance(spec, dict):
        errors.extend(_required_parameters(spec_schema, spec))
    return errors


def _label(resource: dict) -> str:
    name = ((resource.get("metadata") or {}).get("annotations") or {}).get(RESOURCE_NAME_ANNOTATION, "?")
    return f"{resource.get('kind', '?')}/{name}"


def _scope_error(info: KindInfo, index: KindIndex) -> str:
    message = (
        f"{info.api_version} {info.kind} is cluster-scoped, but this XR is namespaced; a namespaced XR "
        f"can only compose namespaced resources (the cluster rejects it with \"cannot apply cluster scoped "
        f"composed resource\")."
    )
    alternatives = index.namespaced_alternatives(info)
    if alternatives:
        message += f" Use {', '.join(a.api_version for a in alternatives)} {info.kind} instead"
        message += " and import its CRD (kiln import), whose shapes differ from the legacy group's."
    else:
        message += " Compose a namespaced kind instead, or make this kind's XR Cluster-scoped in kiln.toml."
    return message


def check_rendered(documents: list[dict], index: KindIndex, xr_scope: str) -> list[str]:
    """Errors for every composed resource in `crossplane render` output (the XR itself is skipped)."""
    errors = []
    for resource in documents:
        annotations = (resource.get("metadata") or {}).get("annotations") or {}
        if RESOURCE_NAME_ANNOTATION not in annotations:
            continue  # the XR, or anything that is not a composed resource
        label = _label(resource)
        info = index.get(resource.get("apiVersion", ""), resource.get("kind", ""))
        if info is None:
            errors.append(
                f"{label}: no CRD or XRD for {resource.get('apiVersion')} {resource.get('kind')} in crds/ or "
                f"the generated XRDs, so it cannot be checked. Check the apiVersion and kind, add the provider "
                f"to manifests/crossplane-providers/ and run kiln pull-crds, or generate the child kind first."
            )
            continue
        if xr_scope == "Namespaced" and info.scope == "Cluster":
            errors.append(f"{label}: {_scope_error(info, index)}")
        errors.extend(f"{label}: {e}" for e in validate_resource(resource, info))
    return errors


def scope_warning_for_import(crd_file: Path, project: Project) -> str | None:
    """A warning when a CRD's scope cannot be composed by the project's (namespaced) XRs."""
    infos = [i for doc in _read_yaml_docs(crd_file) for i in _infos(doc, crd_file)]
    if not infos or infos[0].scope != "Cluster" or project.scope != "Namespaced":
        return None
    info = infos[0]
    message = (
        f"kiln: {info.group} {info.kind} is cluster-scoped, but this project's XRs are namespaced, and a "
        f"namespaced XR cannot compose a cluster-scoped resource."
    )
    alternatives = KindIndex.load(project).namespaced_alternatives(info)
    if alternatives:
        paths = sorted({str(a.source) for a in alternatives})
        message += f" Import the namespaced variant instead: {', '.join(paths)}"
    cluster_kinds = sorted(k for k, s in project.kind_scopes.items() if s == "Cluster")
    if cluster_kinds:
        message += f" (Fine if only Cluster-scoped kinds compose it: {', '.join(cluster_kinds)}.)"
    return message
