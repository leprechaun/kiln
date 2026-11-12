from tooling.discover import discover_kinds


def test_finds_kinds_from_compose_function_names(tmp_path):
    (tmp_path / "iamrole.k").write_text("composeIAMRole = lambda oxr, ocds -> [any] {\n  []\n}\n")
    (tmp_path / "lambdafunction.k").write_text(
        "composeLambdaFunction = lambda oxr, ocds -> [any] {\n  []\n}\n"
    )

    assert discover_kinds(tmp_path) == ["IAMRole", "LambdaFunction"]


def test_ignores_schema_and_test_files(tmp_path):
    (tmp_path / "iamrole.k").write_text("composeIAMRole = lambda oxr, ocds -> [any] {\n  []\n}\n")
    (tmp_path / "iamrole_test.k").write_text("test_something = lambda {\n  assert True\n}\n")
    (tmp_path / "schemas_providers.k").write_text("schema Foo:\n    x: str\n")
    (tmp_path / "schemas_compositions.k").write_text("schema IAMRoleSpec:\n    x: str\n")

    assert discover_kinds(tmp_path) == ["IAMRole"]


def test_returns_kinds_in_sorted_file_order(tmp_path):
    (tmp_path / "staticwebsite.k").write_text(
        "composeStaticWebsite = lambda oxr, ocds -> [any] {\n  []\n}\n"
    )
    (tmp_path / "dnsvalidatedcertificate.k").write_text(
        "composeDnsValidatedCertificate = lambda oxr, ocds -> [any] {\n  []\n}\n"
    )

    assert discover_kinds(tmp_path) == ["DnsValidatedCertificate", "StaticWebsite"]
