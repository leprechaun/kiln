import os

import pytest

from kiln.cli import main
from kiln.kcl import KclError, run_kcl


def _kcl_on_path(bin_dir, monkeypatch, body):
    bin_dir.mkdir(exist_ok=True)
    script = bin_dir / "kcl"
    script.write_text(f"#!/bin/sh\n{body}\n")
    script.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}:{os.environ['PATH']}")


def test_run_kcl_runs_in_the_given_directory(tmp_path, monkeypatch):
    _kcl_on_path(tmp_path / "bin", monkeypatch, 'pwd > where.txt; echo "$@" > args.txt')
    work = tmp_path / "work"
    work.mkdir()

    run_kcl(["import", "-m", "crd", "x.yaml"], work)

    assert (work / "where.txt").read_text().strip() == str(work)
    assert (work / "args.txt").read_text().strip() == "import -m crd x.yaml"


def test_a_failing_kcl_raises_one_error_carrying_its_message(tmp_path, monkeypatch):
    _kcl_on_path(tmp_path / "bin", monkeypatch, 'echo "invalid schema in foo.k" >&2; exit 1')

    with pytest.raises(KclError, match=r"kcl doc.*invalid schema in foo\.k"):
        run_kcl(["doc", "generate"], tmp_path)


def test_a_missing_kcl_binary_is_reported_as_such(tmp_path, monkeypatch):
    monkeypatch.setenv("PATH", str(tmp_path))  # no kcl anywhere

    with pytest.raises(KclError, match="`kcl` binary"):
        run_kcl(["version"], tmp_path)


def _project(path):
    path.mkdir()
    (path / "kiln.toml").write_text('group = "g.io"\n')
    (path / "kcl-scripts").mkdir()
    (path / "kcl-scripts" / "schemas_providers.k").write_text("# header\n")
    (path / "crd.yaml").write_text("kind: CustomResourceDefinition\nspec:\n  group: x.io\n  names: {kind: Thing}\n  versions: [{name: v1}]\n")
    return path


def test_import_and_generate_report_a_failing_kcl_the_same_way(tmp_path, monkeypatch, capsys):
    project = _project(tmp_path / "project")
    (project / "kcl-scripts" / "schemas_compositions.k").write_text("schema SiteSpec:\n    d: str\n")
    (project / "kcl-scripts" / "site.k").write_text("composeSite = lambda oxr, ocds -> [any] {\n  []\n}\n")
    _kcl_on_path(tmp_path / "bin", monkeypatch, 'echo "boom from kcl" >&2; exit 1')
    monkeypatch.chdir(project)

    assert main(["import", "crd.yaml"]) == 1
    imported = capsys.readouterr().err
    assert main(["generate", "Site"]) == 1
    generated = capsys.readouterr().err

    for err in (imported, generated):
        assert "kiln:" in err and "boom from kcl" in err
        assert "Traceback" not in err


def test_an_error_kcl_prints_to_stdout_is_still_reported(tmp_path, monkeypatch):
    _kcl_on_path(tmp_path / "bin", monkeypatch, 'echo "error[E3M38]: bad schema" ; exit 1')

    with pytest.raises(KclError, match="E3M38"):
        run_kcl(["doc", "generate"], tmp_path)


def test_a_kcl_that_fails_silently_is_reported_with_its_exit_status(tmp_path, monkeypatch):
    _kcl_on_path(tmp_path / "bin", monkeypatch, "exit 3")

    with pytest.raises(KclError, match="exit status 3"):
        run_kcl(["doc", "generate"], tmp_path)


def test_the_failing_subcommand_is_named_not_its_first_flag(tmp_path, monkeypatch):
    _kcl_on_path(tmp_path / "bin", monkeypatch, 'echo "nope" >&2; exit 1')

    with pytest.raises(KclError) as e:
        run_kcl(["import", "-m", "crd", "x.yaml"], tmp_path)

    assert str(e.value).startswith("kcl import failed")
    assert "-m" not in str(e.value).split(":")[0]
