import re
from pathlib import Path

from kiln.curate import curate_provider_schema

FIXTURE = Path(__file__).parent / "fixtures" / "bucket_kcl_import.k"
ROLE_FIXTURE = Path(__file__).parent / "fixtures" / "role_kcl_import.k"


def test_keeps_the_specforprovider_and_statusatprovider_schemas():
    source = FIXTURE.read_text()

    curated = curate_provider_schema(source)

    assert "schema S3AwsmUpboundIoV1beta1BucketSpecForProvider:" in curated
    assert "schema S3AwsmUpboundIoV1beta1BucketStatusAtProvider:" in curated
    assert "schema S3AwsmUpboundIoV1beta1BucketStatus:" not in curated


def test_discards_every_schema_outside_the_provider_groups():
    source = FIXTURE.read_text()

    curated = curate_provider_schema(source)

    names = re.findall(r"^schema (\w+):", curated, re.MULTILINE)
    assert names
    for name in names:
        assert name.startswith(("S3AwsmUpboundIoV1beta1BucketSpecForProvider", "S3AwsmUpboundIoV1beta1BucketStatusAtProvider"))


def test_preserves_required_optional_markers_and_docstrings():
    source = FIXTURE.read_text()

    curated = curate_provider_schema(source)

    assert "region: str" in curated  # required: no trailing `?`
    assert "tags?: {str:str}" in curated  # optional: trailing `?`
    assert "Region where this resource will be managed" in curated


SOURCE_WITH_NESTED_TYPE = '''
schema FooSpecForProvider:
    r"""
    docstring
    """
    name: str
    tagsRef: FooTagsRef

schema FooTagsRef:
    r"""
    nested
    """
    key: str
    value: str

schema FooStatusAtProvider:
    r"""
    irrelevant
    """
    arn: str
'''


def test_keeps_schemas_transitively_referenced_by_specforprovider():
    curated = curate_provider_schema(SOURCE_WITH_NESTED_TYPE)

    assert "schema FooSpecForProvider:" in curated
    assert "schema FooTagsRef:" in curated
    assert "schema FooStatusAtProvider:" in curated


SOURCE_WITH_DOCSTRING_PROSE_MATCHING_AN_UNRELATED_SCHEMA_NAME = '''
schema Function:
    r"""
    The top-level k8s wrapper, irrelevant to forProvider.
    """
    spec: FunctionSpec

schema FunctionSpec:
    r"""
    Irrelevant wrapper spec.
    """
    forProvider: FunctionSpecForProvider

schema FunctionSpecForProvider:
    r"""
    handler : str, optional
        The name of the method within your Function that Lambda calls.
    """
    handler?: str
'''


def test_does_not_pull_in_schemas_only_mentioned_in_docstring_prose():
    curated = curate_provider_schema(SOURCE_WITH_DOCSTRING_PROSE_MATCHING_AN_UNRELATED_SCHEMA_NAME)

    assert "schema FunctionSpecForProvider:" in curated
    assert "schema FunctionSpec:" not in curated
    assert "schema Function:" not in curated


def test_curates_a_real_resource_with_multiple_levels_of_nested_types():
    source = ROLE_FIXTURE.read_text()

    curated = curate_provider_schema(source)

    assert curated.count("schema ") == 8
    for name in [
        "IamAwsmUpboundIoV1beta1RoleSpecForProvider",
        "IamAwsmUpboundIoV1beta1RoleSpecForProviderInlinePolicyItems0",
        "IamAwsmUpboundIoV1beta1RoleSpecForProviderManagedPolicyArnsRefsItems0",
        "IamAwsmUpboundIoV1beta1RoleSpecForProviderManagedPolicyArnsRefsItems0Policy",
        "IamAwsmUpboundIoV1beta1RoleSpecForProviderManagedPolicyArnsSelector",
        "IamAwsmUpboundIoV1beta1RoleSpecForProviderManagedPolicyArnsSelectorPolicy",
        "IamAwsmUpboundIoV1beta1RoleStatusAtProvider",
        "IamAwsmUpboundIoV1beta1RoleStatusAtProviderInlinePolicyItems0",
    ]:
        assert f"schema {name}:" in curated
    for name in [
        "IamAwsmUpboundIoV1beta1RoleSpecInitProvider",
        "IamAwsmUpboundIoV1beta1RoleStatus",
        "IamAwsmUpboundIoV1beta1RoleSpecProviderConfigRef",
        "IamAwsmUpboundIoV1beta1RoleSpecWriteConnectionSecretToRef",
    ]:
        assert f"schema {name}:" not in curated


SOURCE_WITH_STATUS_AT_PROVIDER = '''
schema FooSpecForProvider:
    r"""
    docstring
    """
    name: str

schema FooSpecInitProvider:
    r"""
    irrelevant
    """
    label: str

schema FooStatus:
    r"""
    wrapper, irrelevant
    """
    atProvider?: FooStatusAtProvider

schema FooStatusAtProvider:
    r"""
    docstring
    """
    arn?: str
    rules?: [FooStatusAtProviderRulesItems0]

schema FooStatusAtProviderRulesItems0:
    r"""
    nested
    """
    priority?: float
'''


def test_keeps_status_at_provider_and_its_referenced_types_but_drops_other_schemas():
    curated = curate_provider_schema(SOURCE_WITH_STATUS_AT_PROVIDER)

    assert "schema FooSpecForProvider:" in curated
    assert "schema FooStatusAtProvider:" in curated
    assert "schema FooStatusAtProviderRulesItems0:" in curated
    assert "schema FooSpecInitProvider:" not in curated
    assert "schema FooStatus:" not in curated
