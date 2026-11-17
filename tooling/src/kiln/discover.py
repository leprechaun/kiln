import re
from pathlib import Path

_COMPOSE_FN = re.compile(r"^compose(\w+)\s*=\s*lambda\s+oxr\s*,\s*ocds\b", re.MULTILINE)


def discover_kinds(kcl_dir: Path) -> list[str]:
    kinds = []
    for f in sorted(kcl_dir.glob("*.k")):
        if f.name.startswith("schemas_") or f.name.endswith("_test.k"):
            continue
        match = _COMPOSE_FN.search(f.read_text())
        if match:
            kinds.append(match.group(1))
    return kinds
