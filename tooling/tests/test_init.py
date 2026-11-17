from kiln.cli import main
from kiln.discover import discover_kinds
from kiln.project import find_project


def test_init_creates_an_empty_project_the_other_commands_can_use(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    assert main(["init", "my-platform"]) == 0

    project = find_project(tmp_path / "my-platform")
    assert project.group == "platform.example.com"
    assert discover_kinds(project.kcl_scripts_dir) == []
    assert main(["--root", str(project.root), "generate-all"]) == 0
    assert main(["--root", str(project.root), "render-all"]) == 0


def test_init_uses_the_requested_api_group(tmp_path):
    assert main(["init", str(tmp_path / "p"), "--group", "platform.acme.io"]) == 0

    assert find_project(tmp_path / "p").group == "platform.acme.io"


def test_init_refuses_to_overwrite_an_existing_project(tmp_path, capsys):
    (tmp_path / "kiln.toml").write_text('group = "platform.mine.io"\n')

    assert main(["init", str(tmp_path)]) != 0
    assert "already a Kiln project" in capsys.readouterr().err
    assert find_project(tmp_path).group == "platform.mine.io"


def test_init_ships_none_of_the_example_kinds(tmp_path):
    main(["init", str(tmp_path / "p")])

    contents = "\n".join(f.read_text() for f in (tmp_path / "p").rglob("*") if f.is_file()).lower()
    for kind in ("iamrole", "lambdafunction", "dnsvalidatedcertificate", "staticwebsite"):
        assert kind not in contents


def test_init_tells_agents_to_read_the_guide_first(tmp_path):
    main(["init", str(tmp_path / "p")])

    assert "kiln docs" in (tmp_path / "p" / "AGENTS.md").read_text()


def test_init_agents_file_makes_tests_a_requirement(tmp_path):
    main(["init", str(tmp_path / "p")])

    agents = (tmp_path / "p" / "AGENTS.md").read_text()
    for needed in ("<kind>_test.k", "kcl test .", "kiln render-all"):
        assert needed in agents


def test_init_agents_file_says_how_to_install_and_run_kiln(tmp_path):
    main(["init", str(tmp_path / "p")])

    agents = (tmp_path / "p" / "AGENTS.md").read_text()
    assert "not published on PyPI" in agents
    assert 'uvx --from "git+https://github.com/leprechaun/kiln#subdirectory=tooling" kiln' in agents
    assert "uv tool install" in agents


def test_init_agents_file_states_what_kiln_is_for(tmp_path):
    main(["init", str(tmp_path / "p")])

    agents = (tmp_path / "p" / "AGENTS.md").read_text()
    assert "## What Kiln is for" in agents
    intent = agents.split("## What Kiln is for", 1)[1].split("\n## ", 1)[0].lower()
    for idea in ("data structures", "cloud components", "seconds", "yaml", "sample data"):
        assert idea in intent


def test_init_installs_the_bundled_skills_for_agents_and_claude(tmp_path):
    main(["init", str(tmp_path / "p")])

    for skill in ("kiln", "kcl-primer", "crossplane-intro"):
        assert (tmp_path / "p" / ".agents" / "skills" / skill / "SKILL.md").is_file()
        assert (tmp_path / "p" / ".claude" / "skills" / skill / "SKILL.md").is_file()


def test_install_skills_keeps_local_edits_unless_forced(tmp_path):
    main(["init", str(tmp_path / "p")])
    skill = tmp_path / "p" / ".agents" / "skills" / "kiln" / "SKILL.md"
    skill.write_text("local edit")

    assert main(["--root", str(tmp_path / "p"), "install-skills"]) == 0
    assert skill.read_text() == "local edit"

    assert main(["--root", str(tmp_path / "p"), "install-skills", "--force"]) == 0
    assert skill.read_text().startswith("---\nname: kiln")


def test_init_writes_the_chosen_format_and_defaults_to_yaml(tmp_path):
    main(["init", str(tmp_path / "plain")])
    main(["init", str(tmp_path / "argo"), "--format", "jsonnet"])

    assert find_project(tmp_path / "plain").format == "yaml"
    assert find_project(tmp_path / "argo").format == "jsonnet"
    assert 'format = "yaml"' in (tmp_path / "plain" / "kiln.toml").read_text()


def test_init_rejects_an_unknown_format(tmp_path):
    import pytest

    with pytest.raises(SystemExit):
        main(["init", str(tmp_path / "p"), "--format", "cue"])
    assert not (tmp_path / "p").exists()
