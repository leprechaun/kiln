import shutil
import sys
from pathlib import Path

from kiln.project import MARKER

DEFAULT_GROUP = "platform.example.com"

_SCAFFOLD = Path(__file__).parent / "scaffold"


def init_project(directory: Path, group: str = DEFAULT_GROUP) -> int:
    if (directory / MARKER).exists():
        print(f"kiln: {directory} is already a Kiln project", file=sys.stderr)
        return 1

    shutil.copytree(_SCAFFOLD, directory, dirs_exist_ok=True)
    (directory / "gitignore").rename(directory / ".gitignore")
    (directory / MARKER).write_text(f'group = "{group}"\n')
    print(f"Created Kiln project in {directory}")
    return 0
