import shutil
from pathlib import Path

SKILLS_SOURCE = Path(__file__).parent / "skills"


def _bundled() -> list[Path]:
    return sorted(p for p in SKILLS_SOURCE.iterdir() if (p / "SKILL.md").is_file())


def _files(skill_dir: Path) -> dict[str, bytes]:
    return {str(f.relative_to(skill_dir)): f.read_bytes() for f in skill_dir.rglob("*") if f.is_file()}


def stale_skills(root: Path) -> list[str]:
    """Bundled skills installed in the project whose files differ from this Kiln's copy.

    Skills the project never installed are not stale; a project may not use them.
    """
    installed = root / ".agents" / "skills"
    return [
        source.name
        for source in _bundled()
        if (installed / source.name).is_dir() and _files(installed / source.name) != _files(source)
    ]


def stale_skills_warning(root: Path) -> str | None:
    stale = stale_skills(root)
    if not stale:
        return None
    return (
        f"kiln: the installed Kiln skills are out of date ({', '.join(stale)}): they differ from this Kiln's, "
        f"so their guidance may contradict what kiln does. Run `kiln install-skills --force`."
    )


def install_skills(root: Path, force: bool = False) -> int:
    agents_dir = root / ".agents" / "skills"
    claude_dir = root / ".claude" / "skills"
    agents_dir.mkdir(parents=True, exist_ok=True)
    claude_dir.mkdir(parents=True, exist_ok=True)

    for source in _bundled():
        target = agents_dir / source.name
        if target.exists() and not force:
            print(f"- {source.name} (exists; use --force to overwrite)")
        else:
            status = "updated" if target.exists() else "installed"
            shutil.rmtree(target, ignore_errors=True)
            shutil.copytree(source, target)
            print(f"✓ {source.name} ({status})")

        link = claude_dir / source.name
        if not link.is_symlink() and not link.exists():
            link.symlink_to(Path("..") / ".." / ".agents" / "skills" / source.name)

    return 0
