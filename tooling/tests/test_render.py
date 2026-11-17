import os

import yaml

from kiln.cli import main
from test_validate import composed, write_crds

XR = {"apiVersion": "platform.example.io/v1alpha1", "kind": "Site", "metadata": {"name": "example"}}


def _project(path, scope="Namespaced"):
    path.mkdir()
    (path / "kiln.toml").write_text(f'group = "platform.example.io"\nscope = "{scope}"\n')
    (path / "kcl-scripts").mkdir()
    (path / "kcl-scripts" / "site.k").write_text("composeSite = lambda oxr, ocds -> [any] {\n  []\n}\n")
    (path / "render-fixtures" / "site").mkdir(parents=True)
    (path / "render-fixtures" / "site" / "xr.yaml").write_text(yaml.safe_dump(XR))
    write_crds(path)
    return path


def _fake_crossplane(tmp_path, monkeypatch, resources):
    """A `crossplane` that prints the XR and `resources` as render output, and logs each run's argv
    and the observed resources it was given."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    output = bin_dir / "output.yaml"
    output.write_text(yaml.safe_dump_all([XR, *resources]))
    log = bin_dir / "runs.txt"
    script = bin_dir / "crossplane"
    script.write_text(
        "#!/bin/sh\n"
        f'echo "RUN $*" >> {log}\n'
        'while [ $# -gt 0 ]; do\n'
        f'  if [ "$1" = "--observed-resources" ]; then cat "$2" >> {log}; echo >> {log}; fi\n'
        "  shift\n"
        "done\n"
        f"cat {output}\n"
    )
    script.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}:{os.environ['PATH']}")
    monkeypatch.setenv("DOCKER_HOST", "unix:///fake.sock")
    return log


GOOD_BUCKET = composed("s3.aws.m.upbound.io/v1beta1", "Bucket", {"forProvider": {"region": "eu-west-1"}}, "bucket")


def test_render_fails_when_a_namespaced_xr_composes_a_cluster_scoped_kind(tmp_path, monkeypatch, capsys):
    project = _project(tmp_path / "project")
    legacy = composed("s3.aws.upbound.io/v1beta1", "Bucket", {"forProvider": {"region": "eu-west-1"}}, "bucket")
    _fake_crossplane(tmp_path, monkeypatch, [legacy])
    monkeypatch.chdir(project)

    assert main(["render", "Site"]) == 1
    err = capsys.readouterr().err
    assert "Bucket/bucket: s3.aws.upbound.io/v1beta1 Bucket is cluster-scoped" in err
    assert "Use s3.aws.m.upbound.io/v1beta1 Bucket instead" in err


def test_render_takes_the_xr_scope_from_the_generated_xrd(tmp_path, monkeypatch):
    project = _project(tmp_path / "project")
    xrd_dir = project / "manifests" / "crossplane-compositions" / "site"
    xrd_dir.mkdir(parents=True)
    (xrd_dir / "xrd.yaml").write_text("spec:\n  scope: Cluster\n")
    legacy = composed("s3.aws.upbound.io/v1beta1", "Bucket", {"forProvider": {"region": "eu-west-1"}}, "bucket")
    _fake_crossplane(tmp_path, monkeypatch, [legacy])
    monkeypatch.chdir(project)

    assert main(["render", "Site"]) == 0


def test_render_fails_on_an_undeclared_for_provider_field_unless_validation_is_skipped(tmp_path, monkeypatch, capsys):
    project = _project(tmp_path / "project")
    bad = composed("s3.aws.m.upbound.io/v1beta1", "Bucket", {"forProvider": {"region": "x", "bucket": "b"}}, "bucket")
    _fake_crossplane(tmp_path, monkeypatch, [bad])
    monkeypatch.chdir(project)

    assert main(["render", "Site"]) == 1
    captured = capsys.readouterr()
    assert "Bucket/bucket: .spec.forProvider.bucket: field not declared in schema" in captured.err
    assert "kind: Bucket" in captured.out  # the render output is still shown

    assert main(["render", "Site", "--no-validate"]) == 0


def test_render_passes_a_valid_render(tmp_path, monkeypatch):
    project = _project(tmp_path / "project")
    _fake_crossplane(tmp_path, monkeypatch, [GOOD_BUCKET])
    monkeypatch.chdir(project)

    assert main(["render", "Site"]) == 0


def test_render_loads_every_yaml_file_in_an_observed_resources_directory(tmp_path, monkeypatch):
    project = _project(tmp_path / "project")
    log = _fake_crossplane(tmp_path, monkeypatch, [GOOD_BUCKET])
    observed = project / "render-fixtures" / "site" / "stage-2"
    observed.mkdir()
    (observed / "a-bucket.yaml").write_text("kind: Bucket\n")
    (observed / "b-distribution.yml").write_text("kind: Distribution\n---\nkind: Record\n")
    (observed / "notes.txt").write_text("kind: Ignored\n")
    monkeypatch.chdir(project)

    assert main(["render", "Site", "--observed-resources", "render-fixtures/site/stage-2"]) == 0

    passed = [d["kind"] for d in yaml.safe_load_all(log.read_text().split("\n", 1)[1]) if d]
    assert passed == ["Bucket", "Distribution", "Record"]


def test_render_rejects_a_missing_or_empty_observed_resources_path(tmp_path, monkeypatch, capsys):
    project = _project(tmp_path / "project")
    _fake_crossplane(tmp_path, monkeypatch, [GOOD_BUCKET])
    (project / "empty").mkdir()
    monkeypatch.chdir(project)

    assert main(["render", "Site", "--observed-resources", "nope"]) == 1
    assert "no such file or directory" in capsys.readouterr().err
    assert main(["render", "Site", "--observed-resources", "empty"]) == 1
    assert "has no .yaml or .yml files" in capsys.readouterr().err


def test_render_all_renders_cold_and_then_each_observed_fixture(tmp_path, monkeypatch, capsys):
    project = _project(tmp_path / "project")
    log = _fake_crossplane(tmp_path, monkeypatch, [GOOD_BUCKET])
    fixtures = project / "render-fixtures" / "site"
    (fixtures / "observed-1-bucket.yaml").write_text("kind: Bucket\n")
    (fixtures / "observed-2-all.yaml").write_text("kind: Distribution\n")
    monkeypatch.chdir(project)

    assert main(["render-all"]) == 0

    runs = [line for line in log.read_text().splitlines() if line.startswith("RUN ")]
    assert len(runs) == 3
    assert "--observed-resources" not in runs[0]
    assert runs[1].endswith("observed-1-bucket.yaml") and runs[2].endswith("observed-2-all.yaml")
    assert capsys.readouterr().out.splitlines() == [
        "✓ Site",
        "✓ Site (observed-1-bucket.yaml)",
        "✓ Site (observed-2-all.yaml)",
    ]


def test_render_all_fails_when_an_observed_stage_renders_an_invalid_resource(tmp_path, monkeypatch, capsys):
    project = _project(tmp_path / "project")
    bad = composed("s3.aws.m.upbound.io/v1beta1", "Bucket", {"forProvider": {}}, "bucket")
    _fake_crossplane(tmp_path, monkeypatch, [bad])
    (project / "render-fixtures" / "site" / "observed-all.yaml").write_text("kind: Bucket\n")
    monkeypatch.chdir(project)

    assert main(["render-all"]) == 1
    out = capsys.readouterr().out
    assert "✗ Site (observed-all.yaml)" in out
    assert ".spec.forProvider.region: required field is missing" in out
