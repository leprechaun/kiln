from kiln.render import render


def test_staticwebsite_composition_renders_successfully(project):
    result = render(project, "staticwebsite")

    assert result.returncode == 0, result.stderr
