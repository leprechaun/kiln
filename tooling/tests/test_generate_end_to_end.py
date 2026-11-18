import json
import os

import yaml

from kiln.cli import main

DOC = {
    "components": {
        "schemas": {
            "SiteSpec": {"type": "object", "properties": {"domain": {"type": "string"}}, "required": ["domain"]},
        }
    }
}


def _fake_kcl(bin_dir, monkeypatch, doc_content=None):
    """A `kcl` on PATH that behaves like `kcl doc generate --file-path P --target T`: it writes T/docs/<package>.json
    and records the directory it ran in (bin/cwd.txt) and the package it was pointed at (bin/package.txt)."""
    bin_dir.mkdir()
    doc = bin_dir / "doc.json"
    doc.write_text(json.dumps(DOC if doc_content is None else doc_content))
    script = bin_dir / "kcl"
    script.write_text(
        "#!/bin/sh\n"
        f'pwd > "{bin_dir}/cwd.txt"\n'
        'while [ $# -gt 0 ]; do\n'
        f'  case "$1" in --target) target="$2";; --file-path) package="$2"; echo "$2" > "{bin_dir}/package.txt";; esac\n'
        "  shift\n"
        "done\n"
        '[ -d "$target" ] || { echo "target directory does not exist" >&2; exit 2; }\n'
        '[ -d "$package" ] || { echo "--file-path must be a package directory" >&2; exit 2; }\n'
        'mkdir -p "$target/docs"\n'
        f'cp "{doc}" "$target/docs/openapi.json"\n'
    )
    script.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}:{os.environ['PATH']}")


def _project(path, toml='group = "platform.example.io"\n'):
    path.mkdir()
    (path / "kiln.toml").write_text(toml)
    scripts = path / "kcl-scripts"
    scripts.mkdir()
    (scripts / "schemas_providers.k").write_text("schema Provider:\n    x: str\n")
    (scripts / "schemas_compositions.k").write_text("schema SiteSpec:\n    domain: str\n")
    (scripts / "site.k").write_text("composeSite = lambda oxr, ocds -> [any] {\n  []\n}\n")
    return path


def _outputs(project):
    out = project / "manifests" / "crossplane-compositions" / "site"
    return sorted(p.name for p in out.iterdir()), yaml.safe_load((out / "xrd.yaml").read_text())


def test_generate_all_writes_each_kinds_manifests_under_its_conventional_directory(tmp_path, monkeypatch):
    project = _project(tmp_path / "project", 'group = "g.io"\n\n[kinds.Site]\nscope = "Cluster"\n')
    _fake_kcl(tmp_path / "bin", monkeypatch)
    monkeypatch.chdir(project)

    assert main(["generate-all"]) == 0

    files, xrd = _outputs(project)
    assert files == ["composition.yaml", "xrd.yaml"]
    assert xrd["spec"]["group"] == "g.io"
    assert xrd["spec"]["names"] == {"kind": "Site", "plural": "sites"}
    assert xrd["spec"]["scope"] == "Cluster"


def test_generate_for_one_kind_writes_the_same_manifests_as_generate_all(tmp_path, monkeypatch):
    toml = 'group = "g.io"\n\n[kinds.Site]\nscope = "Cluster"\n'
    all_project, one_project = _project(tmp_path / "all", toml), _project(tmp_path / "one", toml)
    _fake_kcl(tmp_path / "bin", monkeypatch)

    monkeypatch.chdir(all_project)
    assert main(["generate-all"]) == 0
    monkeypatch.chdir(one_project)
    assert main(["generate", "site"]) == 0

    assert _outputs(one_project) == _outputs(all_project)
    out = lambda p: (p / "manifests" / "crossplane-compositions" / "site" / "composition.yaml").read_text()
    assert out(one_project) == out(all_project)


def test_generate_scope_flag_beats_the_kiln_toml_setting(tmp_path, monkeypatch):
    project = _project(tmp_path / "project", 'group = "g.io"\n\n[kinds.Site]\nscope = "Cluster"\n')
    _fake_kcl(tmp_path / "bin", monkeypatch)
    monkeypatch.chdir(project)

    assert main(["generate", "Site", "--scope", "Namespaced"]) == 0

    assert _outputs(project)[1]["spec"]["scope"] == "Namespaced"


def test_a_kinds_compose_file_need_not_be_named_after_the_kind(tmp_path, monkeypatch):
    project = _project(tmp_path / "project")
    scripts = project / "kcl-scripts"
    (scripts / "site.k").rename(scripts / "my_site.k")
    _fake_kcl(tmp_path / "bin", monkeypatch)
    monkeypatch.chdir(project)

    assert main(["generate-all"]) == 0
    assert _outputs(project)[0] == ["composition.yaml", "xrd.yaml"]

    assert main(["generate", "site"]) == 0


def test_generate_leaves_the_users_kcl_scripts_directory_untouched(tmp_path, monkeypatch):
    project = _project(tmp_path / "project")
    scripts = project / "kcl-scripts"
    (scripts / "docs").mkdir()
    for name in ("mine.json", "also-mine.json", "notes.md"):
        (scripts / "docs" / name).write_text("keep me")
    before = sorted(str(p.relative_to(scripts)) for p in scripts.rglob("*"))
    _fake_kcl(tmp_path / "bin", monkeypatch)
    monkeypatch.chdir(project)

    assert main(["generate-all"]) == 0

    assert sorted(str(p.relative_to(scripts)) for p in scripts.rglob("*")) == before
    assert (scripts / "docs" / "mine.json").read_text() == "keep me"
    bin_dir = tmp_path / "bin"
    assert (bin_dir / "package.txt").read_text().strip() == str(scripts)
    assert (bin_dir / "cwd.txt").read_text().strip() != str(scripts)


def test_generate_reports_an_ambiguous_union_as_a_clean_error(tmp_path, monkeypatch, capsys):
    project = _project(tmp_path / "project", 'group = "g.io"\n\n[kinds.Site]\nscope = "Cluster"\n')
    ambiguous = {
        "components": {
            "schemas": {
                "SiteSpec": {
                    "type": "object",
                    "properties": {
                        "network": {
                            "x-kcl-union-types": [
                                {"ref": "#/definitions/Small"},
                                {"ref": "#/definitions/Big"},
                            ]
                        }
                    },
                },
                "Small": {"type": "object", "properties": {"a": {"type": "string"}}, "required": ["a"]},
                "Big": {
                    "type": "object",
                    "properties": {"a": {"type": "string"}, "b": {"type": "string"}},
                    "required": ["a", "b"],
                },
            }
        }
    }
    _fake_kcl(tmp_path / "bin", monkeypatch, ambiguous)
    monkeypatch.chdir(project)

    code = main(["generate", "Site"])

    err = capsys.readouterr().err
    assert code != 0
    assert "network" in err and "Small" in err and "Big" in err
    assert "Traceback" not in err
