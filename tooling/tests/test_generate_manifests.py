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
