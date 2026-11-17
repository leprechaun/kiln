import re

import pytest

from kiln.cli import main

EXAMPLE_KINDS = ("iamrole", "lambdafunction", "dnsvalidatedcertificate", "staticwebsite")


def _guide(capsys, monkeypatch, tmp_path) -> str:
    monkeypatch.chdir(tmp_path)  # deliberately not a Kiln project
    assert main(["docs"]) == 0
    return capsys.readouterr().out


def test_docs_prints_the_guide_anywhere_without_a_project(tmp_path, monkeypatch, capsys):
    guide = _guide(capsys, monkeypatch, tmp_path)

    for command in ("kiln pull-crds", "kiln import", "kiln generate", "kiln render"):
        assert command in guide
    assert "[str]: any" in guide


def test_the_guide_stands_alone_without_the_example_kinds(tmp_path, monkeypatch, capsys):
    guide = _guide(capsys, monkeypatch, tmp_path).lower()

    for kind in EXAMPLE_KINDS:
        assert kind not in guide
    assert "existing kind" not in guide


def test_every_kiln_command_the_guide_mentions_exists(tmp_path, monkeypatch, capsys):
    guide = _guide(capsys, monkeypatch, tmp_path)
    mentioned = set(re.findall(r"(?:^|`)kiln ([a-z][a-z-]*)", guide, re.MULTILINE))
    assert {"init", "pull-crds", "import", "generate", "render"} <= mentioned

    for subcommand in sorted(mentioned):
        with pytest.raises(SystemExit) as exit_info:
            main([subcommand, "--help"])
        assert exit_info.value.code == 0, f"the guide mentions `kiln {subcommand}`, which is not a command"
