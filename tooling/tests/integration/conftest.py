import shutil
from pathlib import Path

import pytest

from kiln.project import Project, find_project

_REQUIRED_TOOLS = ("crossplane", "docker")


def pytest_collection_modifyitems(items):
    missing = [tool for tool in _REQUIRED_TOOLS if shutil.which(tool) is None]
    if missing:
        skip = pytest.mark.skip(reason=f"needs {', '.join(missing)} on PATH")
        here = Path(__file__).parent
        for item in items:
            if here in item.path.parents:
                item.add_marker(skip)


@pytest.fixture
def project() -> Project:
    return find_project(Path(__file__).parent)
