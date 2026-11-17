from kiln.render import render


def test_lambdafunction_composition_renders_successfully(project):
    result = render(project, "lambdafunction")

    assert result.returncode == 0, result.stderr
