"""`kiln generate` on a real project (real `kcl doc`, real `kcl run`): a spec schema can be closed."""

import json
import shutil
import subprocess

import pytest
import yaml

from kiln.cli import main

pytestmark = pytest.mark.skipif(shutil.which("kcl") is None, reason="needs kcl on PATH")

CLOSED_SPEC = """\
schema SiteSpec:
    domainName: str
    region: str = "us-east-1"
    tags?: {str:str}
"""

SITE = """\
import .schemas_compositions

composeSite = lambda oxr, ocds -> [any] {
    spec: schemas_compositions.SiteSpec = oxr.spec
    _region = spec.region
    _tags = spec.tags
    _domainName = spec.domainName
    [{
        apiVersion = "s3.aws.m.upbound.io/v1beta1"
        kind = "Bucket"
        metadata.annotations = {"krm.kcl.dev/composition-resource-name" = "bucket"}
        spec.forProvider = {region = _region, tags = _tags}
        spec.writeConnectionSecretToRef.name = _domainName
    }]
}
"""

XR = {
    "apiVersion": "platform.example.com/v1alpha1",
    "kind": "Site",
    "metadata": {"name": "example", "namespace": "default"},
    "spec": {
        "domainName": "www.example.com",
        "tags": {"team": "web"},
        "crossplane": {"compositionRef": {"name": "site-kcl-first"}, "resourceRefs": []},
        "compositionRef": {"name": "site-kcl-first"},
    },
}


def _project(tmp_path, spec_source=CLOSED_SPEC, toml=""):
    root = tmp_path / "project"
    kcl = root / "kcl-scripts"
    kcl.mkdir(parents=True)
    (root / "kiln.toml").write_text('group = "platform.example.com"\n' + toml)
    (kcl / "kcl.mod").write_text('[package]\nname = "kcl-scripts"\n')
    (kcl / "schemas_providers.k").write_text("")
    (kcl / "schemas_compositions.k").write_text(spec_source)
    (kcl / "site.k").write_text(SITE)
    return root


def _generate(project, monkeypatch):
    monkeypatch.chdir(project)
    assert main(["generate", "Site"]) == 0
    return project / "manifests" / "crossplane-compositions" / "site"


def _generated_source(kind_dir):
    if (kind_dir / "composition.k").is_file():  # jsonnet format keeps the source beside the Composition
        return (kind_dir / "composition.k").read_text()
    composition = yaml.safe_load((kind_dir / "composition.yaml").read_text())
    return composition["spec"]["pipeline"][0]["input"]["spec"]["source"]


def _compose(project, monkeypatch, xr=XR):
    """Generate, then run the generated Composition source as function-kcl would."""
    main_k = project / "main.k"
    main_k.write_text(_generated_source(_generate(project, monkeypatch)))
    result = subprocess.run(
        ["kcl", "run", str(main_k), "-D", "params=" + json.dumps({"oxr": xr, "ocds": {}})],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    return yaml.safe_load(result.stdout)["items"]


def test_a_closed_spec_schema_composes_an_xr_carrying_crossplanes_own_spec_fields(tmp_path, monkeypatch):
    items = _compose(_project(tmp_path), monkeypatch)

    assert items[0]["spec"]["forProvider"] == {"region": "us-east-1", "tags": {"team": "web"}}
    assert items[0]["spec"]["writeConnectionSecretToRef"] == {"name": "www.example.com"}


def test_a_closed_spec_schema_works_with_a_default_provider_config_in_jsonnet_format(tmp_path, monkeypatch):
    toml = 'format = "jsonnet"\nproviderConfig = { kind = "ClusterProviderConfig", name = "default-aws" }\n'

    items = _compose(_project(tmp_path, toml=toml), monkeypatch)

    assert items[0]["spec"]["forProvider"]["tags"] == {"team": "web"}
    assert items[0]["spec"]["providerConfigRef"] == {"kind": "ClusterProviderConfig", "name": "default-aws"}


def test_declared_fields_pass_through_even_when_named_like_crossplane_or_reserved_words(tmp_path, monkeypatch):
    spec_source = CLOSED_SPEC + "    $type: str\n    compositionRef?: {str:str}\n"
    site = SITE.replace("_domainName = spec.domainName", "_domainName = spec.$type + spec.compositionRef.name")
    project = _project(tmp_path, spec_source=spec_source)
    (project / "kcl-scripts" / "site.k").write_text(site)
    xr = {**XR, "spec": {**XR["spec"], "type": "static-"}}

    items = _compose(project, monkeypatch, xr=xr)

    assert items[0]["spec"]["writeConnectionSecretToRef"] == {"name": "static-site-kcl-first"}


OPEN_SPEC = """\
schema SiteSpec:
    domainName: str
    tags?: {str:str}
    endpoint?: Endpoint
    [str]: any

schema Endpoint:
    labels?: {str:str}
"""


def _xrd_spec(project, monkeypatch):
    xrd = yaml.safe_load((_generate(project, monkeypatch) / "xrd.yaml").read_text())
    return xrd["spec"]["versions"][0]["schema"]["openAPIV3Schema"]["properties"]["spec"]


def test_the_xrd_spec_rejects_undeclared_fields_even_from_a_schema_with_an_index_signature(tmp_path, monkeypatch):
    spec = _xrd_spec(_project(tmp_path, spec_source=OPEN_SPEC), monkeypatch)

    assert "additionalProperties" not in spec
    assert spec["properties"]["tags"]["additionalProperties"] == {"type": "string"}
    assert spec["properties"]["endpoint"]["properties"]["labels"]["additionalProperties"] == {"type": "string"}


def test_generate_says_an_index_signature_on_a_spec_schema_can_be_removed(tmp_path, monkeypatch, capsys):
    _generate(_project(tmp_path, spec_source=OPEN_SPEC), monkeypatch)

    err = capsys.readouterr().err
    assert err.count("[str]: any") == 1
    assert "SiteSpec" in err and "no longer needed" in err


def test_generate_is_silent_about_a_closed_spec_schema(tmp_path, monkeypatch, capsys):
    _generate(_project(tmp_path), monkeypatch)

    assert capsys.readouterr().err == ""


def test_render_reports_a_misspelt_child_xr_field_as_undeclared(tmp_path, monkeypatch, capsys):
    from test_render import _fake_crossplane  # a `crossplane` that prints the given resources

    project = _project(tmp_path, spec_source=OPEN_SPEC)
    _generate(project, monkeypatch)
    child = {
        "apiVersion": "platform.example.com/v1alpha1",
        "kind": "Site",
        "metadata": {"annotations": {"crossplane.io/composition-resource-name": "site"}},
        "spec": {"domainName": "www.example.com", "domainNme": "typo"},
    }
    _fake_crossplane(tmp_path, monkeypatch, [child])
    (project / "render-fixtures" / "site").mkdir(parents=True)
    (project / "render-fixtures" / "site" / "xr.yaml").write_text(yaml.safe_dump(XR))
    capsys.readouterr()

    assert main(["render", "Site"]) == 1
    assert "Site/site: .spec.domainNme: field not declared in schema" in capsys.readouterr().err
