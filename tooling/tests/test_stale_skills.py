"""Commands that work on a project say when its installed skills are older than this Kiln's."""

import pytest

from kiln.cli import main


@pytest.fixture
def project(tmp_path, monkeypatch, capsys):
    root = tmp_path / "project"
    (root / "kcl-scripts").mkdir(parents=True)
    (root / "kiln.toml").write_text('group = "platform.example.com"\n')
    monkeypatch.chdir(root)
    assert main(["install-skills"]) == 0
    capsys.readouterr()
    return root


def _stderr_of(capsys, *command):
    main(list(command))
    return capsys.readouterr().err


@pytest.mark.parametrize("command", [["generate-all"], ["render-all"]])
def test_a_changed_installed_skill_is_reported_as_out_of_date(project, capsys, command):
    (project / ".agents" / "skills" / "kiln" / "composing.md").write_text("old guidance\n")

    err = _stderr_of(capsys, *command)

    assert "installed Kiln skills are out of date (kiln)" in err
    assert "kiln install-skills --force" in err


def test_a_missing_or_extra_file_in_an_installed_skill_counts_as_out_of_date(project, capsys):
    (project / ".agents" / "skills" / "kiln" / "testing.md").unlink()
    (project / ".agents" / "skills" / "kcl-primer" / "old-topic.md").write_text("gone\n")

    assert "out of date (kcl-primer, kiln)" in _stderr_of(capsys, "generate-all")


def test_current_skills_and_projects_without_installed_skills_are_not_reported(project, capsys, tmp_path):
    assert "out of date" not in _stderr_of(capsys, "generate-all")

    bare = tmp_path / "bare"
    (bare / "kcl-scripts").mkdir(parents=True)
    (bare / "kiln.toml").write_text('group = "platform.example.com"\n')
    assert "out of date" not in _stderr_of(capsys, "--root", str(bare), "generate-all")


def test_refreshing_the_skills_clears_the_report(project, capsys):
    (project / ".agents" / "skills" / "kiln" / "SKILL.md").write_text("old\n")
    assert main(["install-skills", "--force"]) == 0
    capsys.readouterr()

    assert "out of date" not in _stderr_of(capsys, "generate-all")
