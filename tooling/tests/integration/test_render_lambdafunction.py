from tooling.render import render


def test_lambdafunction_composition_renders_successfully():
    result = render("lambdafunction")

    assert result.returncode == 0, result.stderr
