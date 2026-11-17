import re

import pytest

from kiln.cli import main
from kiln.docs import topics
from kiln.skills import SKILLS_SOURCE

EXAMPLE_KINDS = ("iamrole", "lambdafunction", "dnsvalidatedcertificate", "staticwebsite")


@pytest.fixture
def docs(capsys, monkeypatch, tmp_path):
    """Run `kiln docs [topic]` outside any project and return what it printed."""
    monkeypatch.chdir(tmp_path)  # deliberately not a Kiln project

    def run(*topic: str) -> str:
        assert main(["docs", *topic]) == 0
        return capsys.readouterr().out

    return run


def _section(text: str, heading: str) -> str:
    return text.split(heading, 1)[1].split("\n## ", 1)[0]


def test_docs_prints_the_overview_anywhere_without_a_project(docs):
    overview = docs()

    for command in ("kiln pull-crds", "kiln import", "kiln generate", "kiln render"):
        assert command in overview
    assert "[str]: any" in overview
    assert not overview.startswith("---\nname:")  # skill frontmatter is stripped


def test_the_overview_ends_with_every_other_topic(docs):
    overview = docs()

    for topic in topics()[1:]:
        assert f"kiln docs {topic.name}" in overview
    assert "kiln docs all" in overview


def test_every_topic_prints_and_all_prints_them_together(docs):
    everything = docs("all")

    for topic in topics():
        text = docs(topic.name)
        assert text.strip()
        assert text.strip()[:200] in everything


def test_an_unknown_topic_fails_and_lists_the_real_ones(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)

    assert main(["docs", "nope"]) == 2
    err = capsys.readouterr().err
    assert "no docs topic 'nope'" in err
    assert "troubleshooting" in err


def test_topic_names_are_unique():
    names = [t.name for t in topics()]

    assert len(names) == len(set(names))


def test_every_relative_link_in_the_skills_points_at_a_bundled_file():
    for page in SKILLS_SOURCE.glob("*/*.md"):
        for target in re.findall(r"\]\(([^)#]+\.md)\)", page.read_text()):
            if "://" not in target:
                assert (page.parent / target).resolve().is_file(), f"{page}: broken link to {target}"


def test_the_docs_stand_alone_without_the_example_kinds(docs):
    everything = docs("all").lower()

    for kind in EXAMPLE_KINDS:
        assert kind not in everything
    assert "existing kind" not in everything


def test_every_kiln_command_the_docs_mention_exists(docs):
    mentioned = set(re.findall(r"(?:^|`)kiln ([a-z][a-z-]*)", docs("all"), re.MULTILINE))
    assert {"init", "pull-crds", "import", "generate", "render", "docs"} <= mentioned

    for subcommand in sorted(mentioned):
        with pytest.raises(SystemExit) as exit_info:
            main([subcommand, "--help"])
        assert exit_info.value.code == 0, f"the docs mention `kiln {subcommand}`, which is not a command"


def test_the_overview_says_how_to_run_kiln_since_it_is_not_on_pypi(docs):
    overview = docs()

    assert "not published on PyPI" in overview
    assert "uvx --from" in overview
    assert "github.com/leprechaun/kiln" in overview


def test_the_overview_defines_what_verified_means_as_one_ordered_sequence(docs):
    overview = docs()

    assert "## The workflow" in overview
    verify = overview.split("## Verify your work", 1)[1]
    assert verify.index("kcl test .") < verify.index("kiln generate-all") < verify.index("kiln render-all")


def test_the_docs_cover_the_users_project_not_kilns_own_tests(docs):
    assert "pytest" not in docs("all").lower()


def test_the_overview_opens_with_ground_rules_that_make_tests_a_deliverable(docs):
    rules = _section(docs(), "## Ground rules")

    assert "_test.k" in rules
    assert "test first" in rules.lower()
    assert "defer" in rules.lower()  # deferring render/YAML work never defers tests


def test_the_testing_topic_lists_the_tests_every_kind_needs(docs):
    tests = _section(docs("testing"), "## The tests every kind needs")

    for required in ("cold start", "optional", "conditional", "extra field", "status"):
        assert required in tests.lower()


def test_the_overview_says_a_project_without_tests_is_not_done(docs):
    assert "no tests" in _section(docs(), "## Verify your work").lower()


def test_the_overview_states_what_kiln_is_for(docs):
    intent = _section(docs(), "## What Kiln is for").lower()

    for idea in ("data structures", "cloud components", "seconds", "yaml", "sample data"):
        assert idea in intent


def test_the_overview_points_at_each_reference_file_with_when_to_read_it(docs):
    reference = _section(docs(), "## Reference")

    for topic in topics():
        if topic.path.parent.name == "kiln" and topic.path.name != "SKILL.md":
            assert f"]({topic.path.name})" in reference, f"{topic.path.name} has no pointer in the overview"


def test_the_troubleshooting_topic_covers_the_errors_kiln_and_the_cluster_report(docs):
    table = docs("troubleshooting")

    for message in (
        "cannot apply cluster scoped composed resource",
        "field not declared in schema",
        "metadata.annotations: Too long",
        "no status and no events",
        "no CRD or XRD for",
    ):
        assert message in table
