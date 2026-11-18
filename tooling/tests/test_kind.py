from kiln.project import find_project


def _project(tmp_path, toml='group = "platform.example.io"\n', kinds=("StaticWebsite",)):
    (tmp_path / "kiln.toml").write_text(toml)
    (tmp_path / "kcl-scripts").mkdir()
    for kind in kinds:
        (tmp_path / "kcl-scripts" / f"{kind.lower()}.k").write_text(
            f"compose{kind} = lambda oxr, ocds -> [any] {{\n  []\n}}\n"
        )
    return find_project(tmp_path)


def test_a_kind_knows_its_conventional_names_and_output_directory(tmp_path):
    project = _project(tmp_path)

    kind = project.kind("StaticWebsite")

    assert kind.name == "StaticWebsite"
    assert kind.spec_schema == "StaticWebsiteSpec"
    assert kind.plural == "staticwebsites"
    assert kind.output_dir == tmp_path / "manifests" / "crossplane-compositions" / "staticwebsite"


def test_a_lowercased_kind_resolves_to_the_composed_kinds_real_name(tmp_path):
    project = _project(tmp_path)

    kind = project.kind("staticwebsite")

    assert kind.name == "StaticWebsite"
    assert kind.spec_schema == "StaticWebsiteSpec"
    assert kind.output_dir.name == "staticwebsite"


def test_a_kind_with_no_compose_function_keeps_the_name_as_given(tmp_path):
    project = _project(tmp_path, kinds=())

    assert project.kind("Mystery").name == "Mystery"


def test_a_kind_takes_its_scope_and_provider_config_from_kiln_toml(tmp_path):
    project = _project(
        tmp_path,
        'group = "g.io"\nscope = "Namespaced"\n\n[kinds.StaticWebsite]\nscope = "Cluster"\n'
        'providerConfig = { kind = "ProviderConfig", name = "site" }\n',
        kinds=("StaticWebsite", "IAMRole"),
    )

    site, role = project.kind("staticwebsite"), project.kind("IAMRole")

    assert (site.scope, site.provider_config) == ("Cluster", {"kind": "ProviderConfig", "name": "site"})
    assert (role.scope, role.provider_config) == ("Namespaced", None)


def test_explicit_overrides_beat_the_conventions(tmp_path):
    project = _project(tmp_path)

    kind = project.kind("StaticWebsite", spec_schema="SiteSpec", plural="sites", scope="Cluster")

    assert (kind.spec_schema, kind.plural, kind.scope) == ("SiteSpec", "sites", "Cluster")


def test_a_kind_knows_where_its_render_fixtures_and_generated_manifests_live(tmp_path):
    project = _project(tmp_path)

    kind = project.kind("staticwebsite")

    fixtures = tmp_path / "render-fixtures" / "staticwebsite"
    out = tmp_path / "manifests" / "crossplane-compositions" / "staticwebsite"
    assert kind.fixtures_dir == fixtures
    assert kind.xr_file == fixtures / "xr.yaml"
    assert kind.xrd_file == out / "xrd.yaml"
    assert kind.composition_file == out / "composition.yaml"
    assert kind.composition_jsonnet_file == out / "composition.jsonnet"


def test_the_deployed_scope_is_what_the_generated_xrd_says_else_kiln_toml(tmp_path):
    project = _project(tmp_path, 'group = "g.io"\nscope = "Namespaced"\n')
    assert project.kind("StaticWebsite").deployed_scope() == "Namespaced"  # no XRD yet

    xrd = project.kind("StaticWebsite").xrd_file
    xrd.parent.mkdir(parents=True)
    xrd.write_text("spec:\n  scope: Cluster\n")

    assert project.kind("StaticWebsite").deployed_scope() == "Cluster"
