import json
from pathlib import Path

from tooling.normalize import normalize_openapi_schema

PROBE = json.loads((Path(__file__).parent / "fixtures" / "openapi_defaults_probe.json").read_text())
IAMROLE = json.loads((Path(__file__).parent / "fixtures" / "openapi_iamrole.json").read_text())


def test_fixes_the_bool_type_keyword():
    schema = normalize_openapi_schema(PROBE, "Probe")

    assert schema["properties"]["flag"]["type"] == "boolean"


def test_parses_raw_kcl_defaults_into_correctly_typed_json_values():
    schema = normalize_openapi_schema(PROBE, "Probe")

    assert schema["properties"]["flag"]["default"] is True
    assert schema["properties"]["priceClass"]["default"] == "PriceClass_100"
    assert schema["properties"]["count"]["default"] == 3


def test_excludes_defaulted_fields_from_required():
    schema = normalize_openapi_schema(PROBE, "Probe")

    assert schema["required"] == []


def test_fields_without_a_real_default_keep_no_default_and_stay_required():
    schema = normalize_openapi_schema(IAMROLE, "IAMRoleSpec")

    assert "default" not in schema["properties"]["roleName"]
    assert schema["required"] == ["roleName", "trustedService"]


def test_inlines_refs_with_no_dollar_ref_left_anywhere():
    schema = normalize_openapi_schema(IAMROLE, "IamAwsmUpboundIoV1beta1RoleSpecForProvider")

    assert "$ref" not in json.dumps(schema)

    # one level of nesting: inlinePolicy is an array of a referenced schema
    inline_policy_item = schema["properties"]["inlinePolicy"]["items"]
    assert inline_policy_item["properties"]["policy"]["type"] == "string"

    # two levels of nesting: managedPolicyArnsSelector -> policy -> resolution
    selector = schema["properties"]["managedPolicyArnsSelector"]
    assert selector["properties"]["policy"]["properties"]["resolution"]["type"] == "object"


def test_removes_stray_default_on_the_root_schema_itself():
    schema = normalize_openapi_schema(IAMROLE, "IAMRoleSpec")

    assert "default" not in schema


def test_removes_stray_default_on_array_items():
    schema = normalize_openapi_schema(IAMROLE, "IAMRoleSpec")

    assert "default" not in schema["properties"]["managedPolicyArns"]["items"]


def test_strips_kcl_vendor_extension_keys_anywhere_in_the_tree():
    schema = normalize_openapi_schema(IAMROLE, "IamAwsmUpboundIoV1beta1RoleSpecForProvider")

    assert "x-kcl" not in json.dumps(schema)


def test_strips_the_open_schema_index_signature_artifact_but_keeps_real_maps():
    # `[str]: any` (used so a composition schema tolerates the real control
    # plane's injected `spec.crossplane` metadata) makes kcl doc generate
    # emit a spurious `additionalProperties: {type: object}` on the schema
    # itself -- that's an internal validation-tolerance artifact, not a
    # real map type, and shouldn't leak into the published XRD schema.
    # A genuine `{str:str}` field (like `tags`) must still keep its
    # additionalProperties -- the two are distinguished by whether kcl
    # tagged it as a real dict key type.
    schema = normalize_openapi_schema(IAMROLE, "IAMRoleSpec")

    assert "additionalProperties" not in schema
    assert schema["properties"]["tags"]["additionalProperties"] == {"type": "string"}
