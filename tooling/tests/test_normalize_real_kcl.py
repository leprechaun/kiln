import json
import shutil
import subprocess

import pytest

from kiln.normalize import normalize_openapi_schema

MAIN_K = '''schema NetworkSpec:
    vpcId: str
    subnetIds?: [str]

schema CreateVpcSpec:
    cidr: str
    region: str = "us-east-1"

type EnvironmentNetwork = NetworkSpec | CreateVpcSpec

schema EnvironmentSpec:
    network: EnvironmentNetwork
'''


@pytest.mark.skipif(shutil.which("kcl") is None, reason="kcl not installed")
def test_union_normalizes_against_real_kcl_doc_output(tmp_path):
    (tmp_path / "kcl.mod").write_text(
        '[package]\nname="u"\nedition="v0.10.0"\nversion="0.0.1"\n'
    )
    (tmp_path / "main.k").write_text(MAIN_K)
    subprocess.run(
        ["kcl", "doc", "generate", "--format", "openapi", "--target", str(tmp_path)],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    doc = json.loads((tmp_path / "docs" / "u.json").read_text())

    schema = normalize_openapi_schema(doc, "EnvironmentSpec")

    network = schema["properties"]["network"]
    assert set(network["properties"]) == {"vpcId", "subnetIds", "cidr", "region"}
    assert network["oneOf"] == [{"required": ["vpcId"]}, {"required": ["cidr"]}]
    assert "x-kcl" not in json.dumps(schema)
