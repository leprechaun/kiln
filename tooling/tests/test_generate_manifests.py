import json

import yaml

from kiln import generate_manifests
from kiln.generate_manifests import generate_manifests_for

WIDGET_DOC = {
    "components": {
        "schemas": {
            "WidgetSpec": {"type": "object", "properties": {"name": {"type": "string"}}},
            "WidgetStatus": {
                "type": "object",
                "x-kcl-dict-key-type": "str",
                "properties": {
                    "ready": {"type": "bool", "x-kcl-type": "bool"},
                    "endpoint": {"$ref": "#/components/schemas/Endpoint"},
                },
            },
            "Endpoint": {
                "type": "object",
                "properties": {"url": {"type": "string"}},
            },
        }
    }
}


def _write_kcl_dir(kcl_dir):
    (kcl_dir / "widget.k").write_text("composeWidget = lambda oxr, ocds -> [any] {\n  []\n}\n")
    (kcl_dir / "schemas_providers.k").write_text("schema Provider:\n    x: str\n")
    (kcl_dir / "schemas_compositions.k").write_text("schema WidgetSpec:\n    name: str\n")


def _generate_widget(tmp_path, monkeypatch, doc):
    kcl_dir = tmp_path / "kcl"
    kcl_dir.mkdir()
    _write_kcl_dir(kcl_dir)
    monkeypatch.setattr(generate_manifests, "_run_kcl_doc_generate", lambda _kcl_dir: doc)

    output_dir = tmp_path / "out"
    generate_manifests_for(
        kind="Widget",
        spec_schema="WidgetSpec",
        group="platform.kcl-first.io",
        plural="widgets",
        kcl_dir=kcl_dir,
        output_dir=output_dir,
    )
    return yaml.safe_load((output_dir / "xrd.yaml").read_text())


def test_normalizes_a_status_schema_into_the_xrd_status(tmp_path, monkeypatch):
    xrd = _generate_widget(tmp_path, monkeypatch, WIDGET_DOC)

    properties = xrd["spec"]["versions"][0]["schema"]["openAPIV3Schema"]["properties"]
    status = properties["status"]

    assert status["properties"]["ready"]["type"] == "boolean"
    assert status["properties"]["endpoint"]["properties"]["url"]["type"] == "string"
    assert "$ref" not in json.dumps(status)
    assert "x-kcl" not in json.dumps(status)


def test_a_kind_without_a_status_schema_gets_an_xrd_that_only_declares_spec(tmp_path, monkeypatch):
    doc = {"components": {"schemas": {"WidgetSpec": WIDGET_DOC["components"]["schemas"]["WidgetSpec"]}}}

    xrd = _generate_widget(tmp_path, monkeypatch, doc)

    properties = xrd["spec"]["versions"][0]["schema"]["openAPIV3Schema"]["properties"]
    assert list(properties) == ["spec"]


def test_jsonnet_format_imports_the_kcl_source_instead_of_embedding_it(tmp_path, monkeypatch):
    kcl_dir = tmp_path / "kcl"
    kcl_dir.mkdir()
    _write_kcl_dir(kcl_dir)
    monkeypatch.setattr(generate_manifests, "_run_kcl_doc_generate", lambda _kcl_dir: WIDGET_DOC)
    output_dir = tmp_path / "out"

    generate_manifests_for(
        kind="Widget",
        spec_schema="WidgetSpec",
        group="platform.kcl-first.io",
        plural="widgets",
        kcl_dir=kcl_dir,
        output_dir=output_dir,
        output_format="jsonnet",
    )

    jsonnet = (output_dir / "composition.jsonnet").read_text()
    assert "source: " not in jsonnet
    assert '"source": importstr \'composition.k\'' in jsonnet
    assert "composeWidget" not in jsonnet
    assert "composeWidget" in (output_dir / "composition.k").read_text()
    assert not (output_dir / "composition.yaml").exists()
    assert (output_dir / "xrd.yaml").exists()


def _xrd_scope(tmp_path, monkeypatch, **kwargs):
    kcl_dir = tmp_path / "kcl"
    kcl_dir.mkdir(exist_ok=True)
    _write_kcl_dir(kcl_dir)
    monkeypatch.setattr(generate_manifests, "_run_kcl_doc_generate", lambda _kcl_dir: WIDGET_DOC)
    generate_manifests_for(
        kind="Widget", spec_schema="WidgetSpec", group="g.io", plural="widgets",
        kcl_dir=kcl_dir, output_dir=tmp_path / "out", **kwargs,
    )
    return yaml.safe_load((tmp_path / "out" / "xrd.yaml").read_text())["spec"]["scope"]


def test_xrd_scope_is_namespaced_unless_told_otherwise(tmp_path, monkeypatch):
    assert _xrd_scope(tmp_path, monkeypatch) == "Namespaced"


def test_xrd_scope_can_be_cluster(tmp_path, monkeypatch):
    assert _xrd_scope(tmp_path, monkeypatch, scope="Cluster") == "Cluster"


def test_changing_a_kinds_scope_warns_that_xrd_scope_is_immutable(tmp_path, monkeypatch, capsys):
    _xrd_scope(tmp_path, monkeypatch, scope="Namespaced")
    assert "immutable" not in capsys.readouterr().err

    _xrd_scope(tmp_path, monkeypatch, scope="Cluster")
    err = capsys.readouterr().err
    assert "scope changed from Namespaced to Cluster" in err
    assert "immutable" in err

    _xrd_scope(tmp_path, monkeypatch, scope="Cluster")
    assert capsys.readouterr().err == ""


def test_yaml_composition_embeds_the_kcl_as_a_readable_literal_block(tmp_path, monkeypatch):
    _xrd_scope(tmp_path, monkeypatch)

    text = (tmp_path / "out" / "composition.yaml").read_text()
    composition = yaml.safe_load(text)

    assert "        source: |\n          composeWidget = lambda oxr, ocds" in text
    source = composition["spec"]["pipeline"][0]["input"]["spec"]["source"]
    assert source.startswith("composeWidget")
    assert "\\n" not in text  # no escaped newlines: the code is laid out as real lines
