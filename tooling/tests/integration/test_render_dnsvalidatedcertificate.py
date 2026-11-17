from kiln.render import render


def test_dnsvalidatedcertificate_composition_renders_successfully(project):
    result = render(project, "dnsvalidatedcertificate")

    assert result.returncode == 0, result.stderr
