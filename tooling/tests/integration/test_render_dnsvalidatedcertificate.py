from tooling.render import render


def test_dnsvalidatedcertificate_composition_renders_successfully():
    result = render("dnsvalidatedcertificate")

    assert result.returncode == 0, result.stderr
