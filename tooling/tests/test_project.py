import pytest

from kiln.project import InvalidConfig, ProjectNotFound, find_project


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


def test_format_defaults_to_yaml_and_can_be_set_to_jsonnet(tmp_path):
    (tmp_path / "kiln.toml").write_text('group = "platform.example.io"\n')
    assert find_project(tmp_path).format == "yaml"

    (tmp_path / "kiln.toml").write_text('group = "platform.example.io"\nformat = "jsonnet"\n')
    assert find_project(tmp_path).format == "jsonnet"


def test_unknown_format_is_rejected(tmp_path):
    (tmp_path / "kiln.toml").write_text('group = "platform.example.io"\nformat = "cue"\n')

    with pytest.raises(InvalidConfig, match="format must be one of"):
        find_project(tmp_path)


def test_scope_defaults_to_namespaced_with_a_per_kind_override(tmp_path):
    (tmp_path / "kiln.toml").write_text('group = "g.io"\n\n[kinds.Site]\nscope = "Cluster"\n')

    project = find_project(tmp_path)

    assert project.scope == "Namespaced"
    assert project.scope_for("Site") == "Cluster"
    assert project.scope_for("Other") == "Namespaced"


def test_a_project_scope_applies_to_kinds_without_their_own(tmp_path):
    (tmp_path / "kiln.toml").write_text('group = "g.io"\nscope = "Cluster"\n\n[kinds.Role]\nscope = "Namespaced"\n')

    project = find_project(tmp_path)

    assert project.scope_for("Role") == "Namespaced"
    assert project.scope_for("Anything") == "Cluster"


def test_unknown_scopes_are_rejected_wherever_they_appear(tmp_path):
    (tmp_path / "kiln.toml").write_text('group = "g.io"\nscope = "Everywhere"\n')
    with pytest.raises(InvalidConfig, match="scope must be one of"):
        find_project(tmp_path)

    (tmp_path / "kiln.toml").write_text('group = "g.io"\n\n[kinds.Site]\nscope = "Mine"\n')
    with pytest.raises(InvalidConfig, match=r"kinds\.Site\.scope must be one of"):
        find_project(tmp_path)


def test_provider_config_has_a_project_default_and_per_kind_overrides(tmp_path):
    (tmp_path / "kiln.toml").write_text(
        'group = "g.io"\nproviderConfig = { kind = "ClusterProviderConfig", name = "pod-identity" }\n\n'
        '[kinds.Site]\nproviderConfig = { kind = "ProviderConfig", name = "site" }\n'
    )

    project = find_project(tmp_path)

    assert project.provider_config_for("Other") == {"kind": "ClusterProviderConfig", "name": "pod-identity"}
    assert project.provider_config_for("Site") == {"kind": "ProviderConfig", "name": "site"}
    assert project.provider_config_for("site") == {"kind": "ProviderConfig", "name": "site"}


def test_provider_config_is_unset_by_default(tmp_path):
    (tmp_path / "kiln.toml").write_text('group = "g.io"\n')

    assert find_project(tmp_path).provider_config_for("Site") is None


def test_a_malformed_provider_config_is_rejected(tmp_path):
    (tmp_path / "kiln.toml").write_text('group = "g.io"\nproviderConfig = { name = "pod-identity" }\n')
    with pytest.raises(InvalidConfig, match="providerConfig must be a table with exactly a kind and a name"):
        find_project(tmp_path)

    (tmp_path / "kiln.toml").write_text('group = "g.io"\n\n[kinds.Site]\nproviderConfig = "pod-identity"\n')
    with pytest.raises(InvalidConfig, match=r"kinds\.Site\.providerConfig must be a table"):
        find_project(tmp_path)


def test_kind_settings_match_kinds_case_insensitively(tmp_path):
    (tmp_path / "kiln.toml").write_text('group = "g.io"\n\n[kinds.StaticWebsite]\nscope = "Cluster"\n')

    assert find_project(tmp_path).scope_for("staticwebsite") == "Cluster"
