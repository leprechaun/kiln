import os
import sys

from kiln.discover import discover_kinds
from kiln.generate_manifests import generate_kind
from kiln.project import Project


def generate_all(project: Project) -> int:
    failures = []
    for kind in discover_kinds(project.kcl_scripts_dir):
        try:
            result = generate_kind(project, kind)
        except Exception as e:
            if os.environ.get("KILN_DEBUG"):
                raise
            print(f"kiln: {kind}: {e}", file=sys.stderr)
            print(f"✗ {kind}")
            failures.append(kind)
            continue
        print(f"✓ {kind}")
        for warning in result.warnings:
            print(warning, file=sys.stderr)

    return 1 if failures else 0
