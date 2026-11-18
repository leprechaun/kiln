import os

from kiln.cli import main
from kiln.generate_manifests import generate_kind
from kiln.project import find_project
from test_generate_end_to_end import _fake_kcl, _project


def _site(tmp_path, monkeypatch, toml='group = "g.io"\n'):
    project_dir = _project(tmp_path / "project", toml)
    _fake_kcl(tmp_path / "bin", monkeypatch)
    return project_dir


def test_a_clean_generate_returns_no_warnings_and_prints_nothing(tmp_path, monkeypatch, capsys):
    project = find_project(_site(tmp_path, monkeypatch))

    result = generate_kind(project, "Site")

    assert result.warnings == []
    assert capsys.readouterr().err == ""


def test_changing_a_kinds_scope_is_returned_as_a_warning_not_printed(tmp_path, monkeypatch, capsys):
    project_dir = _site(tmp_path, monkeypatch)
    generate_kind(find_project(project_dir), "Site")

    result = generate_kind(find_project(project_dir), "Site", scope="Cluster")

    [warning] = result.warnings
    assert "scope changed from Namespaced to Cluster" in warning and "immutable" in warning
    assert capsys.readouterr().err == ""
    assert generate_kind(find_project(project_dir), "Site", scope="Cluster").warnings == []


def test_an_open_spec_schema_is_returned_as_a_warning(tmp_path, monkeypatch):
    project_dir = _site(tmp_path, monkeypatch)
    (project_dir / "kcl-scripts" / "schemas_compositions.k").write_text(
        "schema SiteSpec:\n    domain: str\n    [str]: any\n"
    )

    [warning] = generate_kind(find_project(project_dir), "Site").warnings

    assert "SiteSpec ends in `[str]: any`" in warning


def test_a_composition_near_the_annotation_limit_is_returned_as_a_warning(tmp_path, monkeypatch):
    project_dir = _site(tmp_path, monkeypatch)
    scripts = project_dir / "kcl-scripts"
    (scripts / "schemas_providers.k").write_text("schema Huge:\n" + "".join(f"    field{i}?: str\n" for i in range(12000)))
    (scripts / "site.k").write_text("composeSite = lambda oxr, ocds -> [any] {\n  _h: Huge = {}\n  []\n}\n")

    [warning] = generate_kind(find_project(project_dir), "Site").warnings

    assert "Site composition is" in warning and "schema Huge" in warning
    assert "256 KB" in warning and "262144" not in warning
    assert "do not trim imported schemas by hand" in warning


def test_generate_prints_the_warnings_to_stderr(tmp_path, monkeypatch, capsys):
    project_dir = _site(tmp_path, monkeypatch)
    monkeypatch.chdir(project_dir)
    assert main(["generate", "Site"]) == 0
    capsys.readouterr()

    assert main(["generate", "Site", "--scope", "Cluster"]) == 0

    assert "scope changed from Namespaced to Cluster" in capsys.readouterr().err


def test_generate_all_prints_the_warnings_to_stderr_too(tmp_path, monkeypatch, capsys):
    project_dir = _site(tmp_path, monkeypatch)
    monkeypatch.chdir(project_dir)
    assert main(["generate-all"]) == 0
    (project_dir / "kiln.toml").write_text('group = "g.io"\n\n[kinds.Site]\nscope = "Cluster"\n')
    capsys.readouterr()

    assert main(["generate-all"]) == 0

    assert "scope changed from Namespaced to Cluster" in capsys.readouterr().err


def _failing_kcl(tmp_path, monkeypatch):
    bin_dir = tmp_path / "failbin"
    bin_dir.mkdir()
    script = bin_dir / "kcl"
    script.write_text('#!/bin/sh\necho "boom from kcl" >&2\nexit 1\n')
    script.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}:{os.environ['PATH']}")


def test_generate_and_generate_all_report_a_failing_kcl_the_same_way(tmp_path, monkeypatch, capsys):
    project_dir = _site(tmp_path, monkeypatch)
    _failing_kcl(tmp_path, monkeypatch)
    monkeypatch.chdir(project_dir)

    assert main(["generate", "Site"]) == 1
    single = capsys.readouterr().err
    assert main(["generate-all"]) == 1
    captured = capsys.readouterr()

    for err in (single, captured.err):
        assert "kiln:" in err and "Site" in err and "boom from kcl" in err
        assert "Traceback" not in err
    assert "✗ Site" in captured.out


def test_generate_for_a_kind_with_no_compose_file_fails_with_a_message(tmp_path, monkeypatch, capsys):
    project_dir = _site(tmp_path, monkeypatch)
    monkeypatch.chdir(project_dir)

    assert main(["generate", "Mystery"]) == 1
    err = capsys.readouterr().err
    assert "kiln:" in err and "Mystery" in err and "Traceback" not in err


def _kcl_emitting(tmp_path, monkeypatch, names):
    """A `kcl` that writes the given JSON file names (and nothing else) to <target>/docs."""
    bin_dir = tmp_path / "emitbin"
    bin_dir.mkdir(exist_ok=True)
    script = bin_dir / "kcl"
    writes = "".join(f'echo "{{}}" > "$target/docs/{n}"\n' for n in names)
    script.write_text(
        "#!/bin/sh\n"
        'while [ $# -gt 0 ]; do case "$1" in --target) target="$2";; esac; shift; done\n'
        'mkdir -p "$target/docs"\n' + writes
    )
    script.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}:{os.environ['PATH']}")


def test_kcl_producing_no_docs_or_several_is_reported_clearly(tmp_path, monkeypatch, capsys):
    project_dir = _site(tmp_path, monkeypatch)
    monkeypatch.chdir(project_dir)

    _kcl_emitting(tmp_path, monkeypatch, [])
    assert main(["generate", "Site"]) == 1
    none = capsys.readouterr().err
    _kcl_emitting(tmp_path, monkeypatch, ["a.json", "b.json"])
    assert main(["generate", "Site"]) == 1
    several = capsys.readouterr().err

    assert "expected 1" in none and "0" in none
    assert "expected 1" in several and "a.json" in several and "b.json" in several
    assert "unpack" not in none + several


def test_generate_all_gives_each_kind_its_own_scope(tmp_path, monkeypatch):
    project_dir = _site(tmp_path, monkeypatch, 'group = "g.io"\nscope = "Namespaced"\n\n[kinds.Site]\nscope = "Cluster"\n')
    scripts = project_dir / "kcl-scripts"
    (scripts / "schemas_compositions.k").write_text("schema SiteSpec:\n    domain: str\nschema RoleSpec:\n    domain: str\n")
    (scripts / "role.k").write_text("composeRole = lambda oxr, ocds -> [any] {\n  []\n}\n")
    # the fake kcl's doc only declares SiteSpec; give it RoleSpec too
    import json as _json

    doc = tmp_path / "bin" / "doc.json"
    spec = {"type": "object", "properties": {"domain": {"type": "string"}}, "required": ["domain"]}
    doc.write_text(_json.dumps({"components": {"schemas": {"SiteSpec": spec, "RoleSpec": spec}}}))
    monkeypatch.chdir(project_dir)

    assert main(["generate-all"]) == 0

    import yaml

    out = project_dir / "manifests" / "crossplane-compositions"
    scope = lambda kind: yaml.safe_load((out / kind / "xrd.yaml").read_text())["spec"]["scope"]
    assert (scope("site"), scope("role")) == ("Cluster", "Namespaced")


def test_the_scope_flag_beats_kiln_toml_which_beats_the_default(tmp_path, monkeypatch):
    import yaml

    project_dir = _site(tmp_path, monkeypatch, 'group = "g.io"\nscope = "Cluster"\n')
    monkeypatch.chdir(project_dir)
    xrd = project_dir / "manifests" / "crossplane-compositions" / "site" / "xrd.yaml"

    main(["generate", "Site"])
    assert yaml.safe_load(xrd.read_text())["spec"]["scope"] == "Cluster"  # kiln.toml beats the default

    main(["generate", "Site", "--scope", "Namespaced"])
    assert yaml.safe_load(xrd.read_text())["spec"]["scope"] == "Namespaced"  # the flag beats kiln.toml


def test_kiln_debug_shows_the_traceback_instead_of_a_one_line_message(tmp_path, monkeypatch):
    import pytest

    from kiln.kcl import KclError

    project_dir = _site(tmp_path, monkeypatch)
    _failing_kcl(tmp_path, monkeypatch)
    monkeypatch.chdir(project_dir)
    monkeypatch.setenv("KILN_DEBUG", "1")

    with pytest.raises(KclError):
        main(["generate", "Site"])
    with pytest.raises(KclError):
        main(["generate-all"])
