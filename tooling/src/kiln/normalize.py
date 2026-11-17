import copy


def _parse_raw_default(raw: str, prop_type: str):
    if prop_type == "boolean":
        return raw == "True"
    if prop_type == "integer":
        return int(raw)
    if prop_type == "number":
        return float(raw)
    if prop_type == "string":
        return raw.strip('"')
    return raw


def _ref_name(ref: str) -> str:
    return ref.rsplit("/", 1)[-1]


def _walk(value, schemas: dict, seen: frozenset):
    if isinstance(value, dict):
        if "$ref" in value:
            name = _ref_name(value["$ref"])
            if name in seen:
                return {}  # cyclic ref guard; not expected for provider schemas
            return _walk(copy.deepcopy(schemas[name]), schemas, seen | {name})

        # `[str]: any` (an open-schema index signature, used purely to make
        # a composition schema tolerate the real control plane's injected
        # metadata) makes kcl emit a spurious `additionalProperties: {type:
        # object}` alongside `properties`. A genuine `{str:X}` map field has
        # no declared `properties` sibling and carries `x-kcl-dict-key-type`
        # -- that marker is how we tell the two apart before stripping it.
        is_real_map = "x-kcl-dict-key-type" in value
        node = {k: v for k, v in value.items() if not k.startswith("x-kcl")}
        if not is_real_map and "properties" in node:
            node.pop("additionalProperties", None)

        if node.get("type") == "bool":
            node["type"] = "boolean"

        if "properties" in node:
            node["properties"] = {k: _walk(v, schemas, seen) for k, v in node["properties"].items()}
        if "items" in node:
            node["items"] = _walk(node["items"], schemas, seen)
        if isinstance(node.get("additionalProperties"), dict):
            node["additionalProperties"] = _walk(node["additionalProperties"], schemas, seen)

        raw = node.get("default", "")
        if raw == "":
            node.pop("default", None)
        else:
            node["default"] = _parse_raw_default(raw, node.get("type"))

        if "required" in node and "properties" in node:
            node["required"] = [
                name for name in node["required"] if "default" not in node["properties"].get(name, {})
            ]

        return node

    if isinstance(value, list):
        return [_walk(v, schemas, seen) for v in value]

    return value


def normalize_openapi_schema(doc: dict, root: str) -> dict:
    schemas = doc["components"]["schemas"]
    return _walk(copy.deepcopy(schemas[root]), schemas, frozenset({root}))
