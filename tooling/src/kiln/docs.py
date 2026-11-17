"""`kiln docs`: the bundled skills, readable without installing them.

The skills under kiln/skills/ are the single source of the documentation. `kiln docs` prints the
kiln skill; `kiln docs <topic>` prints any other skill (by its name) or a reference file next to
a skill (by its file name without `.md`).
"""

import re
from dataclasses import dataclass
from pathlib import Path

from kiln.skills import SKILLS_SOURCE

MAIN_SKILL = "kiln"
ALL = "all"

_FRONTMATTER = re.compile(r"\A---\n.*?\n---\n+", re.DOTALL)
_TITLE = re.compile(r"^# (.+)$", re.MULTILINE)


@dataclass(frozen=True)
class Topic:
    name: str
    path: Path

    @property
    def text(self) -> str:
        return _FRONTMATTER.sub("", self.path.read_text())

    @property
    def title(self) -> str:
        match = _TITLE.search(self.text)
        return match.group(1) if match else self.name


def topics() -> list[Topic]:
    """The main skill first, then its reference files, then every other skill and its files."""
    skill_dirs = sorted((p for p in SKILLS_SOURCE.iterdir() if (p / "SKILL.md").is_file()),
                        key=lambda p: (p.name != MAIN_SKILL, p.name))
    found = []
    for skill in skill_dirs:
        found.append(Topic(skill.name, skill / "SKILL.md"))
        found.extend(Topic(f.stem, f) for f in sorted(skill.glob("*.md")) if f.name != "SKILL.md")
    return found


def _index(listed: list[Topic]) -> str:
    width = max(len(t.name) for t in listed)
    lines = "\n".join(f"  kiln docs {t.name:<{width}}  {t.title}" for t in listed)
    return (
        "\n---\n\n"
        "More topics. A link to `<name>.md`, and a skill named in the text, are `kiln docs <name>`;\n"
        "`kiln docs all` prints everything.\n\n"
        f"{lines}\n"
    )


def render_docs(topic: str | None = None) -> str:
    """The text `kiln docs [topic]` prints. Raises KeyError for an unknown topic."""
    available = topics()
    if topic == ALL:
        return "\n\n".join(t.text.rstrip("\n") for t in available) + "\n"
    if topic is None:
        main, rest = available[0], available[1:]
        return main.text.rstrip("\n") + "\n" + _index(rest)
    by_name = {t.name: t for t in available}
    if topic not in by_name:
        raise KeyError(topic)
    return by_name[topic].text


def topic_names() -> list[str]:
    return [t.name for t in topics()] + [ALL]
