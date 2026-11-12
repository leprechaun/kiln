from tooling.render import render


def test_iamrole_composition_renders_successfully():
    result = render("iamrole")

    assert result.returncode == 0, result.stderr
