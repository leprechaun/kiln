import pytest

from kiln.generate import (
    build_combined_kcl_source,
    enforce_naming_convention,
    generate_composition,
    generate_xrd,
)


def test_accepts_a_correctly_named_compose_function():
    enforce_naming_convention("IAMRole", "composeIAMRole = lambda oxr, ocds -> [any] {\n  []\n}\n")


def test_rejects_a_missing_compose_function():
    with pytest.raises(ValueError):
        enforce_naming_convention("IAMRole", "someOtherFunction = lambda oxr, ocds -> [any] {\n  []\n}\n")


def test_rejects_wrong_parameter_names():
    with pytest.raises(ValueError):
        enforce_naming_convention("IAMRole", "composeIAMRole = lambda xr, resources -> [any] {\n  []\n}\n")


def test_combines_sources_stripping_local_imports_but_keeping_external_ones():
    schemas_providers = "schema Foo:\n    x: str\n"
    schemas_compositions = "import .schemas_providers\n\nschema Bar:\n    y: str\n"
    compose = (
        "import json\n"
        "import .schemas_compositions\n"
        "import .schemas_providers\n\n"
        "composeIAMRole = lambda oxr, ocds -> [any] {\n"
        "    a: schemas_providers.Foo = oxr.a\n"
        "    b: schemas_compositions.Bar = oxr.b\n"
        "    []\n}\n"
    )

    combined = build_combined_kcl_source(
        {"schemas_providers": schemas_providers, "schemas_compositions": schemas_compositions}, compose
    )

    assert "import .schemas_compositions" not in combined
    assert "import .schemas_providers" not in combined
    assert "import json" in combined
    assert "schema Foo:" in combined
    assert "schema Bar:" in combined
    assert "composeIAMRole" in combined


def test_strips_module_qualified_references_once_flattened():
    schemas_a = "schema Foo:\n    x: str\n"
    schemas_b = "import .schemas_a\n\nschema Bar:\n    f: schemas_a.Foo\n"
    compose = (
        "import .schemas_a\n"
        "import .schemas_b\n\n"
        "composeThing = lambda oxr, ocds -> [any] {\n"
        "    x: schemas_a.Foo = oxr.spec\n"
        "    y: schemas_b.Bar = ocds\n"
        "    []\n"
        "}\n"
    )

    combined = build_combined_kcl_source({"schemas_a": schemas_a, "schemas_b": schemas_b}, compose)

    assert "schemas_a." not in combined
    assert "schemas_b." not in combined
    assert "x: Foo = oxr.spec" in combined
    assert "y: Bar = ocds" in combined
    assert "f: Foo" in combined


def test_generate_composition_produces_the_expected_pipeline_shape():
    combined_source = "composeIAMRole = lambda oxr, ocds -> [any] {\n  []\n}\n"

    composition = generate_composition(kind="IAMRole", group="platform.kcl-first.io", combined_source=combined_source)

    assert composition["apiVersion"] == "apiextensions.crossplane.io/v1"
    assert composition["kind"] == "Composition"
    assert composition["spec"]["compositeTypeRef"] == {
        "apiVersion": "platform.kcl-first.io/v1alpha1",
        "kind": "IAMRole",
    }
    assert composition["spec"]["mode"] == "Pipeline"

    compose_step = composition["spec"]["pipeline"][0]
    assert compose_step["functionRef"]["name"] == "function-kcl"
    source = compose_step["input"]["spec"]["source"]
    assert "composeIAMRole" in source
    assert 'items = composeIAMRole(option("params").oxr, option("params").ocds)' in source

    auto_ready_step = composition["spec"]["pipeline"][1]
    assert auto_ready_step["functionRef"]["name"] == "function-auto-ready"


def test_generate_composition_rejects_source_without_a_matching_compose_function():
    with pytest.raises(ValueError):
        generate_composition(
            kind="IAMRole",
            group="platform.kcl-first.io",
            combined_source="someOther = lambda oxr, ocds -> [any] {\n  []\n}\n",
        )


def test_generate_xrd_wraps_the_schema_under_spec():
    schema = {"type": "object", "properties": {"roleName": {"type": "string"}}, "required": ["roleName"]}

    xrd = generate_xrd(kind="IAMRole", group="platform.kcl-first.io", plural="iamroles", spec_schema=schema)

    assert xrd["apiVersion"] == "apiextensions.crossplane.io/v1"
    assert xrd["kind"] == "CompositeResourceDefinition"
    assert xrd["metadata"]["name"] == "iamroles.platform.kcl-first.io"
    assert xrd["spec"]["group"] == "platform.kcl-first.io"
    assert xrd["spec"]["names"] == {"kind": "IAMRole", "plural": "iamroles"}

    version = xrd["spec"]["versions"][0]
    assert version["name"] == "v1alpha1"
    assert version["served"] is True
    assert version["referenceable"] is True
    assert version["schema"]["openAPIV3Schema"]["properties"]["spec"] == schema


def test_generate_xrd_declares_the_status_schema_under_status_when_given_one():
    spec_schema = {"type": "object", "properties": {"functionName": {"type": "string"}}}
    status_schema = {"type": "object", "properties": {"functionUrl": {"type": "string"}}}

    xrd = generate_xrd(
        kind="LambdaFunction",
        group="platform.kcl-first.io",
        plural="lambdafunctions",
        spec_schema=spec_schema,
        status_schema=status_schema,
    )

    properties = xrd["spec"]["versions"][0]["schema"]["openAPIV3Schema"]["properties"]
    assert properties == {"spec": spec_schema, "status": status_schema}


_COMPOSE_USING_A = "import .schemas_a\n\ncomposeThing = lambda oxr, ocds -> [any] {\n    x: schemas_a.A = oxr\n    []\n}\n"


def _combine(schemas: str, compose: str = _COMPOSE_USING_A) -> str:
    return build_combined_kcl_source({"schemas_a": schemas}, compose)


def test_drops_schemas_the_compose_function_cannot_reach():
    combined = _combine("schema A:\n    x: str\n\nschema Unused:\n    y: str\n")

    assert "schema A:" in combined
    assert "Unused" not in combined


def test_keeps_schemas_reachable_through_other_schemas_and_inheritance():
    schemas = (
        "schema A(Base):\n    inner: Inner\n    items: [Listed]\n\n"
        "schema Base:\n    b: str\n\n"
        "schema Inner:\n    i: str\n\n"
        "schema Listed:\n    l: str\n\n"
        "schema Unused:\n    u: str\n"
    )

    combined = _combine(schemas)

    for kept in ("schema A(Base):", "schema Base:", "schema Inner:", "schema Listed:"):
        assert kept in combined
    assert "Unused" not in combined


def test_a_name_that_only_appears_in_prose_does_not_keep_a_schema():
    schemas = 'schema A:\n    r"""Wraps a Role, not the Role schema."""\n    x: str\n\nschema Role:\n    r: str\n'

    assert "schema Role:" not in _combine(schemas)


def test_strips_schema_docstrings_but_leaves_the_compose_source_alone():
    schemas = 'schema A:\n    r"""\n    Long description.\n\n    Attributes\n    ----------\n    x: str\n    """\n    x: str\n'
    compose = _COMPOSE_USING_A + '\n# kept comment\n_note = """\n    kept text\n"""\n'

    combined = _combine(schemas, compose)

    assert "Long description" not in combined
    assert "schema A:\n    x: str" in combined
    assert "# kept comment" in combined
    assert "kept text" in combined


def test_keeps_top_level_code_that_follows_a_dropped_schema():
    schemas = "schema A:\n    x: str\n\nschema Unused:\n    y: str\n\nhelper = lambda v: str -> str {\n    v\n}\n"

    combined = _combine(schemas)

    assert "Unused" not in combined
    assert "helper = lambda v: str -> str {" in combined


def test_keeps_whatever_a_top_level_helper_depends_on():
    schemas = "schema A:\n    x: str\n\nschema OnlyForHelper:\n    y: str\n\nhelper = lambda v -> OnlyForHelper {\n    v\n}\n"

    assert "schema OnlyForHelper:" in _combine(schemas)


def test_the_generated_source_has_no_runs_of_blank_lines():
    combined = _combine("schema A:\n    x: str\n\n\n\nschema Unused:\n    y: str\n\n\nschema Also:\n    z: str\n")

    assert "\n\n\n" not in combined


def test_generate_xrd_defaults_to_namespaced_and_accepts_a_cluster_scope():
    args = dict(kind="Widget", group="g.io", plural="widgets", spec_schema={"type": "object"})

    assert generate_xrd(**args)["spec"]["scope"] == "Namespaced"
    assert generate_xrd(**args, scope="Cluster")["spec"]["scope"] == "Cluster"
