import os
import shutil
from pathlib import Path

from kiln.cli import main

FIXTURES = Path(__file__).parent / "fixtures"
ROLE_CRD = FIXTURES / "role_crd.yaml"
# Reconstructed from `kcl import -m crd` 0.13.3 output for the lambda FunctionURL CRD (one file per schema).
FUNCTIONURL_013 = FIXTURES / "kcl_0_13" / "functionurl" / "models"
FUNCTIONURL_CRD = FIXTURES / "kcl_0_13" / "functionurl" / "functionurl_crd.yaml"
FUNCTIONURL_PREFIX = "LambdaAwsmUpboundIoV1beta1FunctionURL"
ROLE_SPEC = "schema IamAwsmUpboundIoV1beta1RoleSpecForProvider:"


def _project(path):
    path.mkdir()
    (path / "kiln.toml").write_text('group = "platform.example.io"\n')
    (path / "kcl-scripts").mkdir()
    (path / "kcl-scripts" / "schemas_providers.k").write_text("# header\n")
    return path


def _fake_kcl(bin_dir, monkeypatch, generated: Path):
    """Put a `kcl` on PATH whose `import` emits `generated` where real kcl would.

    A file is emitted as the single models/<dir>/schema.k that kcl 0.12 wrote; a directory
    is copied over as models/, the way kcl 0.13 lays out one file per schema.
    """
    bin_dir.mkdir()
    script = bin_dir / "kcl"
    emit = f'cp -r "{generated}/." models/' if generated.is_dir() else f'mkdir -p models/fake\ncp "{generated}" models/fake/schema.k'
    script.write_text(f"#!/bin/sh\n{emit}\n")
    script.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}:{os.environ['PATH']}")


def test_importing_the_same_crd_twice_leaves_the_schemas_file_unchanged(tmp_path, monkeypatch):
    project = _project(tmp_path / "project")
    _fake_kcl(tmp_path / "bin", monkeypatch, FIXTURES / "role_kcl_import.k")
    schemas = project / "kcl-scripts" / "schemas_providers.k"
    monkeypatch.chdir(project)

    assert main(["import", str(ROLE_CRD)]) == 0
    after_first = schemas.read_text()
    assert main(["import", str(ROLE_CRD)]) == 0

    assert after_first.count(ROLE_SPEC) == 1
    assert schemas.read_text() == after_first


def test_importing_replaces_a_stale_schema_in_place_and_leaves_others_alone(tmp_path, monkeypatch):
    project = _project(tmp_path / "project")
    _fake_kcl(tmp_path / "bin", monkeypatch, FIXTURES / "role_kcl_import.k")
    schemas = project / "kcl-scripts" / "schemas_providers.k"
    schemas.write_text(
        "# header\n\n"
        "schema Before:\n    a?: str\n\n"
        f"{ROLE_SPEC}\n    staleField?: str\n\n"
        "schema After:\n    b?: str\n"
    )
    monkeypatch.chdir(project)

    assert main(["import", str(ROLE_CRD)]) == 0

    text = schemas.read_text()
    assert text.startswith("# header\n")
    assert "staleField" not in text
    assert text.count(ROLE_SPEC) == 1
    assert text.index("schema Before:") < text.index(ROLE_SPEC) < text.index("schema After:")
    assert "schema Before:\n    a?: str\n" in text
    assert "schema After:\n    b?: str\n" in text


def test_importing_split_kcl_output_yields_the_same_group_prefixed_schemas(tmp_path, monkeypatch):
    project = _project(tmp_path / "project")
    _fake_kcl(tmp_path / "bin", monkeypatch, FUNCTIONURL_013)
    monkeypatch.chdir(project)

    assert main(["import", str(FUNCTIONURL_CRD)]) == 0

    text = (project / "kcl-scripts" / "schemas_providers.k").read_text()
    for name in ("SpecForProvider", "SpecForProviderCors", "SpecForProviderFunctionNameRef",
                 "SpecForProviderFunctionNameRefPolicy", "StatusAtProvider", "AtProviderCors"):
        assert f"schema {FUNCTIONURL_PREFIX}{name}:" in text
    assert f"cors?: {FUNCTIONURL_PREFIX}SpecForProviderCors" in text
    assert f"cors?: [{FUNCTIONURL_PREFIX}AtProviderCors]" in text
    assert "FunctionURLV1beta1" not in text
    assert "InitProvider" not in text


def test_importing_split_kcl_output_twice_leaves_the_schemas_file_unchanged(tmp_path, monkeypatch):
    project = _project(tmp_path / "project")
    _fake_kcl(tmp_path / "bin", monkeypatch, FUNCTIONURL_013)
    schemas = project / "kcl-scripts" / "schemas_providers.k"
    monkeypatch.chdir(project)

    assert main(["import", str(FUNCTIONURL_CRD)]) == 0
    after_first = schemas.read_text()
    assert main(["import", str(FUNCTIONURL_CRD)]) == 0

    assert schemas.read_text() == after_first


def test_importing_drops_schemas_the_resource_no_longer_generates_but_not_a_neighbouring_kind(tmp_path, monkeypatch):
    project = _project(tmp_path / "project")
    _fake_kcl(tmp_path / "bin", monkeypatch, FUNCTIONURL_013)
    schemas = project / "kcl-scripts" / "schemas_providers.k"
    schemas.write_text(
        "# header\n\n"
        "schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProvider:\n    other?: str\n\n"
        f"schema {FUNCTIONURL_PREFIX}SpecForProviderRemovedThing:\n    gone?: str\n"
    )
    monkeypatch.chdir(project)

    assert main(["import", str(FUNCTIONURL_CRD)]) == 0

    text = schemas.read_text()
    assert "RemovedThing" not in text
    assert "schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProvider:\n    other?: str\n" in text
    assert f"schema {FUNCTIONURL_PREFIX}SpecForProvider:" in text


def _add_referenced_cors(generated: Path, definition: str):
    """Add an unscoped `Cors` schema that SpecForProvider refers to, so it survives curation."""
    version_dir = generated / "v1beta1"
    (version_dir / "function_url_v1beta1_cors.k").write_text(definition)
    spec_for_provider = version_dir / "function_url_v1beta1_spec_for_provider.k"
    spec_for_provider.write_text(spec_for_provider.read_text() + "    otherCors?: FunctionURLV1beta1Cors\n")


def test_importing_refuses_when_two_generated_schemas_would_get_the_same_name(tmp_path, monkeypatch, capsys):
    project = _project(tmp_path / "project")
    generated = tmp_path / "generated"
    shutil.copytree(FUNCTIONURL_013, generated)
    # 0.13's unscoped `Cors` and `ForProviderCors` would both become `...SpecForProviderCors`
    _add_referenced_cors(generated, "schema FunctionURLV1beta1Cors:\n    x?: str\n")
    _fake_kcl(tmp_path / "bin", monkeypatch, generated)
    schemas = project / "kcl-scripts" / "schemas_providers.k"
    monkeypatch.chdir(project)

    assert main(["import", str(FUNCTIONURL_CRD)]) != 0

    err = capsys.readouterr().err
    assert "collide" in err
    assert "FunctionURLV1beta1Cors" in err and "FunctionURLV1beta1ForProviderCors" in err
    assert "FunctionURLV1beta1Spec" not in err
    assert schemas.read_text() == "# header\n"


def test_importing_merges_colliding_schemas_whose_definitions_are_identical(tmp_path, monkeypatch):
    project = _project(tmp_path / "project")
    generated = tmp_path / "generated"
    shutil.copytree(FUNCTIONURL_013, generated)
    # same fields as ForProviderCors, differing only in the docstring kcl derives from the name
    _add_referenced_cors(
        generated,
        'schema FunctionURLV1beta1Cors:\n    r"""\n    function URL v1beta1 cors\n    """\n    allowOrigins?: [str]\n',
    )
    _fake_kcl(tmp_path / "bin", monkeypatch, generated)
    schemas = project / "kcl-scripts" / "schemas_providers.k"
    monkeypatch.chdir(project)

    assert main(["import", str(FUNCTIONURL_CRD)]) == 0

    assert schemas.read_text().count(f"schema {FUNCTIONURL_PREFIX}SpecForProviderCors:") == 1


def test_importing_ignores_a_name_collision_between_schemas_that_curation_drops(tmp_path, monkeypatch):
    project = _project(tmp_path / "project")
    generated = tmp_path / "generated"
    shutil.copytree(FUNCTIONURL_013, generated)
    # `Cors` would collide with `ForProviderCors`, but nothing kept refers to it
    (generated / "v1beta1" / "function_url_v1beta1_cors.k").write_text("schema FunctionURLV1beta1Cors:\n    x?: str\n")
    _fake_kcl(tmp_path / "bin", monkeypatch, generated)
    schemas = project / "kcl-scripts" / "schemas_providers.k"
    monkeypatch.chdir(project)

    assert main(["import", str(FUNCTIONURL_CRD)]) == 0

    assert f"schema {FUNCTIONURL_PREFIX}SpecForProviderCors:" in schemas.read_text()


def test_importing_keeps_distinct_the_two_nested_status_types_kcl_names_atprovider_and_statusatprovider(tmp_path, monkeypatch):
    project = _project(tmp_path / "project")
    generated = tmp_path / "generated"
    shutil.copytree(FUNCTIONURL_013, generated)
    version_dir = generated / "v1beta1"
    # the real Distribution shape: a list of {enabled, items}, whose `items` are a second, differently shaped type
    (version_dir / "function_url_v1beta1_at_provider_things.k").write_text(
        "schema FunctionURLV1beta1AtProviderThings:\n    enabled?: bool\n    items?: [FunctionURLV1beta1StatusAtProviderThings]\n"
    )
    (version_dir / "function_url_v1beta1_status_at_provider_things.k").write_text(
        "schema FunctionURLV1beta1StatusAtProviderThings:\n    keyGroupId?: str\n    keyPairIds?: [str]\n"
    )
    status_at_provider = version_dir / "function_url_v1beta1_status_at_provider.k"
    status_at_provider.write_text(status_at_provider.read_text() + "    things?: [FunctionURLV1beta1AtProviderThings]\n")
    _fake_kcl(tmp_path / "bin", monkeypatch, generated)
    schemas = project / "kcl-scripts" / "schemas_providers.k"
    monkeypatch.chdir(project)

    assert main(["import", str(FUNCTIONURL_CRD)]) == 0

    text = schemas.read_text()
    assert f"schema {FUNCTIONURL_PREFIX}AtProviderThings:\n    enabled?: bool\n" in text
    assert f"items?: [{FUNCTIONURL_PREFIX}StatusAtProviderThings]" in text
    assert f"schema {FUNCTIONURL_PREFIX}StatusAtProviderThings:\n    keyGroupId?: str\n" in text


def test_importing_drops_a_stale_status_side_schema_the_resource_no_longer_generates(tmp_path, monkeypatch):
    project = _project(tmp_path / "project")
    _fake_kcl(tmp_path / "bin", monkeypatch, FUNCTIONURL_013)
    schemas = project / "kcl-scripts" / "schemas_providers.k"
    schemas.write_text(f"# header\n\nschema {FUNCTIONURL_PREFIX}AtProviderStale:\n    gone?: str\n")
    monkeypatch.chdir(project)

    assert main(["import", str(FUNCTIONURL_CRD)]) == 0

    assert "AtProviderStale" not in schemas.read_text()
