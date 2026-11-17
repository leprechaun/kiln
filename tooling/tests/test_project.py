import pytest

from kiln.project import ProjectNotFound, find_project


def test_finds_project_root_from_a_nested_directory(tmp_path):
    (tmp_path / "kiln.toml").write_text('group = "platform.example.io"\n')
    nested = tmp_path / "kcl-scripts" / "deeper"
    nested.mkdir(parents=True)

    project = find_project(nested)

    assert project.root == tmp_path


def test_reports_missing_marker_when_no_project_above(tmp_path):
    with pytest.raises(ProjectNotFound, match="no kiln.toml found"):
        find_project(tmp_path)


def test_explicit_root_wins_over_the_start_directory(tmp_path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "kiln.toml").write_text('group = "platform.example.io"\n')
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    project = find_project(elsewhere, root=project_dir)

    assert project.root == project_dir


def test_explicit_root_without_marker_is_rejected(tmp_path):
    with pytest.raises(ProjectNotFound, match="no kiln.toml found"):
        find_project(tmp_path, root=tmp_path)


def test_reads_api_group_from_kiln_toml(tmp_path):
    (tmp_path / "kiln.toml").write_text('group = "platform.example.io"\n')

    assert find_project(tmp_path).group == "platform.example.io"
