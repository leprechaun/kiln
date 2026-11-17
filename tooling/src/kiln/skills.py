import shutil
from pathlib import Path

SKILLS_SOURCE = Path(__file__).parent / "skills"


def _bundled() -> list[Path]:
    return sorted(p for p in SKILLS_SOURCE.iterdir() if (p / "SKILL.md").is_file())


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
