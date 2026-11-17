import shutil
import sys
from pathlib import Path

from kiln.project import MARKER
from kiln.skills import install_skills

DEFAULT_GROUP = "platform.example.com"

_SCAFFOLD = Path(__file__).parent / "scaffold"


def init_project(directory: Path, group: str = DEFAULT_GROUP, output_format: str = "yaml", scope: str = "Namespaced") -> int:
    if (directory / MARKER).exists():
        print(f"kiln: {directory} is already a Kiln project", file=sys.stderr)
        return 1

    shutil.copytree(_SCAFFOLD, directory, dirs_exist_ok=True)
    (directory / "gitignore").rename(directory / ".gitignore")
    (directory / MARKER).write_text(f'group = "{group}"\nformat = "{output_format}"\nscope = "{scope}"\n')
    install_skills(directory)
    print(f"Created Kiln project in {directory}")
    return 0
