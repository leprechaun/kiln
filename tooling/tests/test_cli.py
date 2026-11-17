import os

from kiln.cli import main


def test_command_outside_a_project_fails_with_a_clear_message(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)

    exit_code = main(["generate-all"])

    assert exit_code != 0
    assert "no kiln.toml found" in capsys.readouterr().err


def _empty_project(path):
    path.mkdir(exist_ok=True)
    (path / "kiln.toml").write_text('group = "platform.example.io"\n')
    (path / "kcl-scripts").mkdir()
    return path


def test_render_all_with_no_kinds_succeeds(tmp_path, monkeypatch):
    monkeypatch.chdir(_empty_project(tmp_path))

    assert main(["render-all"]) == 0


def _fake_crossplane(bin_dir, monkeypatch):
    """Put a `crossplane` on PATH that records its argv, one argument per line."""
    bin_dir.mkdir()
    calls = bin_dir / "calls.txt"
    script = bin_dir / "crossplane"
    script.write_text(f'#!/bin/sh\nprintf "%s\\n" "$@" > {calls}\n')
    script.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}:{os.environ['PATH']}")
    return calls


def test_pull_crds_fetches_crds_for_the_projects_providers(tmp_path, monkeypatch):
    project = _empty_project(tmp_path / "project")
    calls = _fake_crossplane(tmp_path / "bin", monkeypatch)
    monkeypatch.chdir(project / "kcl-scripts")

    assert main(["pull-crds"]) == 0
    assert calls.read_text().splitlines() == [
        "xpkg",
        "get-crds",
        f"{project}/manifests/crossplane-providers",
        "--output-dir",
        f"{project}/crds",
    ]


def test_render_passes_the_kinds_project_files_to_crossplane(tmp_path, monkeypatch):
    project = _empty_project(tmp_path / "project")
    calls = _fake_crossplane(tmp_path / "bin", monkeypatch)
    monkeypatch.setenv("DOCKER_HOST", "unix:///fake.sock")
    monkeypatch.chdir(project / "kcl-scripts")

    assert main(["render", "IAMRole", "--observed-resources", "observed.yaml"]) == 0
    assert calls.read_text().splitlines() == [
        "composition",
        "render",
        f"{project}/render-fixtures/iamrole/xr.yaml",
        f"{project}/manifests/crossplane-compositions/iamrole/composition.yaml",
        f"{project}/manifests/functions.yaml",
        "--observed-resources",
        "observed.yaml",
    ]


def test_root_flag_targets_a_project_from_outside_it(tmp_path, monkeypatch):
    project = _empty_project(tmp_path / "project")
    calls = _fake_crossplane(tmp_path / "bin", monkeypatch)
    monkeypatch.chdir(tmp_path)

    assert main(["--root", str(project), "pull-crds"]) == 0
    assert f"{project}/crds" in calls.read_text().splitlines()


def _jsonnet_project(path):
    project = _empty_project(path)
    (project / "kiln.toml").write_text('group = "platform.example.io"\nformat = "jsonnet"\n')
    kind_dir = project / "manifests" / "crossplane-compositions" / "iamrole"
    kind_dir.mkdir(parents=True)
    (kind_dir / "composition.jsonnet").write_text("{}")
    return project


def _fake_jsonnet(bin_dir, monkeypatch, exit_code=0):
    """Put a `jsonnet` on PATH that prints a marker instead of evaluating."""
    bin_dir.mkdir(exist_ok=True)
    script = bin_dir / "jsonnet"
    script.write_text(f'#!/bin/sh\necho \'{{"evaluated": "$1"}}\'\nexit {exit_code}\n')
    script.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}:{os.environ['PATH']}")


def test_render_evaluates_jsonnet_and_renders_the_result(tmp_path, monkeypatch):
    project = _jsonnet_project(tmp_path / "project")
    calls = _fake_crossplane(tmp_path / "bin", monkeypatch)
    _fake_jsonnet(tmp_path / "bin", monkeypatch)
    monkeypatch.setenv("DOCKER_HOST", "unix:///fake.sock")
    monkeypatch.chdir(project)

    assert main(["render", "IAMRole"]) == 0

    argv = calls.read_text().splitlines()
    composition = argv[3]
    assert composition.endswith("composition.yaml")
    assert not composition.startswith(str(project))  # a temp file, not something under manifests/
    assert not (project / "manifests" / "crossplane-compositions" / "iamrole" / "composition.yaml").exists()


def test_render_in_jsonnet_mode_without_the_jsonnet_binary_fails_clearly(tmp_path, monkeypatch, capsys):
    project = _jsonnet_project(tmp_path / "project")
    _fake_crossplane(tmp_path / "bin", monkeypatch)
    monkeypatch.setenv("PATH", str(tmp_path / "bin"))  # no jsonnet anywhere
    monkeypatch.setenv("DOCKER_HOST", "unix:///fake.sock")
    (project / "kcl-scripts" / "iamrole.k").write_text("composeIAMRole = lambda oxr, ocds -> [any] {\n []\n}\n")
    monkeypatch.chdir(project)

    assert main(["render", "IAMRole"]) == 127
    assert "`jsonnet` binary" in capsys.readouterr().err
    assert main(["render-all"]) == 1


def test_render_reports_a_jsonnet_evaluation_failure(tmp_path, monkeypatch, capsys):
    project = _jsonnet_project(tmp_path / "project")
    _fake_crossplane(tmp_path / "bin", monkeypatch)
    _fake_jsonnet(tmp_path / "bin", monkeypatch, exit_code=1)
    monkeypatch.setenv("DOCKER_HOST", "unix:///fake.sock")
    monkeypatch.chdir(project)

    assert main(["render", "IAMRole"]) == 1
