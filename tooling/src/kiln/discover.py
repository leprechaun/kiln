import re
import sys
from pathlib import Path


class DuplicateKind(ValueError):
    pass


def compose_function(kind: str = r"\w+") -> re.Pattern:
    """Matches `compose<Kind> = lambda oxr, ocds`, capturing the kind; the one definition of the naming convention."""
    return re.compile(rf"^compose({kind})\s*=\s*lambda\s+oxr\s*,\s*ocds\b", re.MULTILINE)


def discover_compose_files(kcl_dir: Path) -> dict[str, Path]:
    """Map each kind to the .k file that defines its compose function. Unreadable files are skipped."""
    files = {}
    for f in sorted(kcl_dir.glob("*.k")):
        if f.name.startswith("schemas_") or f.name.endswith("_test.k"):
            continue
        try:
            source = f.read_text()
        except (UnicodeDecodeError, OSError) as e:
            print(f"kiln: skipping {f}: {_reason(e)}", file=sys.stderr)
            continue
        match = compose_function().search(source)
        if match:
            kind = match.group(1)
            if kind in files:
                raise DuplicateKind(
                    f"{kind} is defined in both {files[kind].name} and {f.name} ({kcl_dir.name}/); keep one"
                )
            files[kind] = f
    return files


def _reason(e: Exception) -> str:
    if isinstance(e, UnicodeDecodeError):
        return "not valid UTF-8"
    return e.strerror or str(e)


def discover_kinds(kcl_dir: Path) -> list[str]:
    return list(discover_compose_files(kcl_dir))
