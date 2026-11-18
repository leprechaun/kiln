from kiln.discover import discover_kinds


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


def test_a_kind_defined_in_two_files_is_an_error_naming_both(tmp_path):
    import pytest

    from kiln.discover import DuplicateKind, discover_compose_files

    (tmp_path / "site.k").write_text("composeSite = lambda oxr, ocds -> [any] {\n  []\n}\n")
    (tmp_path / "site_old.k").write_text("composeSite = lambda oxr, ocds -> [any] {\n  []\n}\n")

    with pytest.raises(DuplicateKind, match=r"Site.*site\.k.*site_old\.k"):
        discover_compose_files(tmp_path)


def test_a_file_that_cannot_be_read_is_skipped_with_a_warning_naming_it(tmp_path, capsys):
    from kiln.discover import discover_compose_files

    (tmp_path / "site.k").write_text("composeSite = lambda oxr, ocds -> [any] {\n  []\n}\n")
    (tmp_path / "latin.k").write_bytes(b"\xff\xfe not utf-8")

    assert list(discover_compose_files(tmp_path)) == ["Site"]
    assert "latin.k" in capsys.readouterr().err
