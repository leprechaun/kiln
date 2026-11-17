import os
import subprocess
from pathlib import Path

PACKAGE_DIR = Path(__file__).parents[1]


def test_installed_kiln_can_create_and_build_an_empty_project(tmp_path):
    bin_dir = tmp_path / "bin"
    env = {**os.environ, "UV_TOOL_DIR": str(tmp_path / "tools"), "UV_TOOL_BIN_DIR": str(bin_dir)}
    subprocess.run(["uv", "tool", "install", str(PACKAGE_DIR)], env=env, check=True, capture_output=True)
    kiln = str(bin_dir / "kiln")

    subprocess.run([kiln, "init", "my-platform"], cwd=tmp_path, check=True, capture_output=True)
    result = subprocess.run([kiln, "generate-all"], cwd=tmp_path / "my-platform" / "kcl-scripts", capture_output=True, text=True)

    assert result.returncode == 0, result.stderr
    docs = subprocess.run([kiln, "docs"], cwd=tmp_path, capture_output=True, text=True)
    assert docs.returncode == 0, docs.stderr
    assert docs.stdout.startswith("# Kiln\n")
    topic = subprocess.run([kiln, "docs", "troubleshooting"], cwd=tmp_path, capture_output=True, text=True)
    assert topic.returncode == 0 and topic.stdout.startswith("# Troubleshooting\n"), topic.stderr  # reference files ship too
    assert (tmp_path / "my-platform" / "manifests" / "functions.yaml").is_file()
    assert (tmp_path / "my-platform" / ".gitignore").is_file()
    assert (tmp_path / "my-platform" / ".agents" / "skills" / "kiln" / "SKILL.md").is_file()
