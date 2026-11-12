from tooling.render import render


def test_staticwebsite_composition_renders_successfully():
    result = render("staticwebsite")

    assert result.returncode == 0, result.stderr
