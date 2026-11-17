from kiln.render import render


def test_iamrole_composition_renders_successfully(project):
    result = render(project, "iamrole")

    assert result.returncode == 0, result.stderr
