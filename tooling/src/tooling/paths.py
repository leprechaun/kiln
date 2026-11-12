from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def kcl_scripts_dir() -> Path:
    return repo_root() / "kcl-scripts"


def compositions_dir() -> Path:
    return repo_root() / "manifests" / "crossplane-compositions"


def functions_file() -> Path:
    return repo_root() / "manifests" / "functions.yaml"


def render_fixtures_dir() -> Path:
    return repo_root() / "render-fixtures"
