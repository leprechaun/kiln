import tomllib
from dataclasses import dataclass
from pathlib import Path

MARKER = "kiln.toml"


class ProjectNotFound(Exception):
    pass


@dataclass(frozen=True)
class Project:
    root: Path
    group: str

    @property
    def kcl_scripts_dir(self) -> Path:
        return self.root / "kcl-scripts"

    @property
    def compositions_dir(self) -> Path:
        return self.root / "manifests" / "crossplane-compositions"

    @property
    def providers_dir(self) -> Path:
        return self.root / "manifests" / "crossplane-providers"

    @property
    def functions_file(self) -> Path:
        return self.root / "manifests" / "functions.yaml"

    @property
    def render_fixtures_dir(self) -> Path:
        return self.root / "render-fixtures"

    @property
    def crds_dir(self) -> Path:
        return self.root / "crds"


def find_project(start: Path, root: Path | None = None) -> Project:
    candidates = [root] if root else [start, *start.parents]
    for candidate in candidates:
        marker = candidate / MARKER
        if marker.is_file():
            config = tomllib.loads(marker.read_text())
            return Project(root=candidate, group=config["group"])
    raise ProjectNotFound(f"no {MARKER} found in {root or start}" + ("" if root else " or any parent directory"))
