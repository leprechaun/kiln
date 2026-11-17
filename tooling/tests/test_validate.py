from pathlib import Path

import yaml

from kiln.project import Project
from kiln.validate import KindIndex, check_rendered, scope_warning_for_import, validate_value

BUCKET_SPEC = {
    "type": "object",
    "required": ["forProvider"],
    "properties": {
        "forProvider": {
            "type": "object",
            "required": ["region"],
            "properties": {
                "region": {"type": "string"},
                "forceDestroy": {"type": "boolean"},
                "tags": {"type": "object", "additionalProperties": {"type": "string"}},
            },
        },
        "providerConfigRef": {
            "type": "object",
            "properties": {"kind": {"type": "string"}, "name": {"type": "string"}},
        },
        "managementPolicies": {"type": "array", "items": {"type": "string"}},
    },
}

POLICY_SPEC = {
    "type": "object",
    "properties": {
        "forProvider": {"type": "object", "properties": {"policy": {"type": "string"}}},
        "initProvider": {"type": "object", "properties": {"policy": {"type": "string"}}},
        "managementPolicies": {"type": "array", "items": {"type": "string"}},
    },
    "x-kubernetes-validations": [{"message": "spec.forProvider.policy is a required parameter", "rule": "..."}],
}

DISTRIBUTION_SPEC = {
    "type": "object",
    "properties": {
        "forProvider": {
            "type": "object",
            "properties": {
                "viewerCertificate": {"type": "object", "properties": {"acmCertificateArn": {"type": "string"}}},
                "origin": {"type": "array", "items": {"type": "object", "properties": {"domainName": {"type": "string"}}}},
            },
        }
    },
}


def crd(group: str, kind: str, scope: str, spec_schema: dict, version: str = "v1beta1") -> dict:
    return {
        "apiVersion": "apiextensions.k8s.io/v1",
        "kind": "CustomResourceDefinition",
        "metadata": {"name": f"{kind.lower()}s.{group}"},
        "spec": {
            "group": group,
            "names": {"kind": kind, "plural": f"{kind.lower()}s"},
            "scope": scope,
            "versions": [
                {
                    "name": version,
                    "schema": {
                        "openAPIV3Schema": {
                            "type": "object",
                            "properties": {"apiVersion": {"type": "string"}, "spec": spec_schema},
                            "required": ["spec"],
                        }
                    },
                }
            ],
        },
    }


def write_crds(project_root: Path) -> None:
    """The Upbound layout: each service's kinds in a namespaced `.m.` group and a cluster-scoped legacy one."""
    for group, scope in (("s3.aws.m.upbound.io", "Namespaced"), ("s3.aws.upbound.io", "Cluster")):
        for kind, spec in (("Bucket", BUCKET_SPEC), ("BucketPolicy", POLICY_SPEC)):
            path = project_root / "crds" / group / "v1beta1" / f"{kind.lower()}.yaml"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(yaml.safe_dump(crd(group, kind, scope, spec)))
    path = project_root / "crds" / "cloudfront.aws.m.upbound.io" / "v1beta1" / "distribution.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(crd("cloudfront.aws.m.upbound.io", "Distribution", "Namespaced", DISTRIBUTION_SPEC)))


def composed(api_version: str, kind: str, spec: dict | None, name: str = "res") -> dict:
    resource = {
        "apiVersion": api_version,
        "kind": kind,
        "metadata": {"annotations": {"crossplane.io/composition-resource-name": name}},
    }
    if spec is not None:
        resource["spec"] = spec
    return resource


def _project(tmp_path, **kwargs) -> Project:
    write_crds(tmp_path)
    return Project(root=tmp_path, group="platform.example.io", **kwargs)


def _check(tmp_path, resources, xr_scope="Namespaced"):
    return check_rendered(resources, KindIndex.load(_project(tmp_path)), xr_scope)


def test_a_valid_namespaced_resource_passes(tmp_path):
    bucket = composed("s3.aws.m.upbound.io/v1beta1", "Bucket", {"forProvider": {"region": "eu-west-1"}})

    assert _check(tmp_path, [bucket]) == []


def test_the_xr_and_other_unannotated_documents_are_not_checked(tmp_path):
    xr = {"apiVersion": "platform.example.io/v1alpha1", "kind": "Site", "metadata": {"name": "x"}, "spec": {"a": 1}}

    assert _check(tmp_path, [xr]) == []


def test_composing_a_cluster_scoped_kind_from_a_namespaced_xr_names_the_namespaced_group(tmp_path):
    bucket = composed("s3.aws.upbound.io/v1beta1", "Bucket", {"forProvider": {"region": "eu-west-1"}}, name="bucket")

    [error] = _check(tmp_path, [bucket])

    assert error.startswith("Bucket/bucket: ")
    assert "cluster-scoped" in error
    assert "Use s3.aws.m.upbound.io/v1beta1 Bucket instead" in error


def test_a_cluster_xr_may_compose_cluster_scoped_kinds(tmp_path):
    bucket = composed("s3.aws.upbound.io/v1beta1", "Bucket", {"forProvider": {"region": "eu-west-1"}})

    assert _check(tmp_path, [bucket], xr_scope="Cluster") == []


def test_an_undeclared_for_provider_field_fails(tmp_path):
    bucket = composed("s3.aws.m.upbound.io/v1beta1", "Bucket", {"forProvider": {"region": "x", "bucket": "b"}}, "bucket")

    assert _check(tmp_path, [bucket]) == ["Bucket/bucket: .spec.forProvider.bucket: field not declared in schema"]


def test_a_missing_required_field_fails(tmp_path):
    bucket = composed("s3.aws.m.upbound.io/v1beta1", "Bucket", {"forProvider": {"forceDestroy": True}})

    assert _check(tmp_path, [bucket]) == ["Bucket/res: .spec.forProvider.region: required field is missing"]


def test_a_one_item_list_where_the_api_takes_an_object_fails_with_a_hint(tmp_path):
    spec = {"forProvider": {"viewerCertificate": [{"acmCertificateArn": "arn"}], "origin": [{"domainName": "d"}]}}

    [error] = _check(tmp_path, [composed("cloudfront.aws.m.upbound.io/v1beta1", "Distribution", spec)])

    assert ".spec.forProvider.viewerCertificate: expected object, got array" in error
    assert "single object" in error


def test_a_policy_document_given_as_an_object_fails_with_a_hint(tmp_path):
    spec = {"forProvider": {"policy": {"Version": "2012-10-17"}}}

    [error] = _check(tmp_path, [composed("s3.aws.m.upbound.io/v1beta1", "BucketPolicy", spec)])

    assert ".spec.forProvider.policy: expected string, got object" in error
    assert "json.encode" in error


def test_a_cel_required_parameter_must_be_set_in_for_provider_or_init_provider(tmp_path):
    missing = composed("s3.aws.m.upbound.io/v1beta1", "BucketPolicy", {"forProvider": {}})
    in_init = composed("s3.aws.m.upbound.io/v1beta1", "BucketPolicy", {"forProvider": {}, "initProvider": {"policy": "{}"}})
    observe_only = composed(
        "s3.aws.m.upbound.io/v1beta1", "BucketPolicy", {"forProvider": {}, "managementPolicies": ["Observe"]}
    )

    assert _check(tmp_path, [missing]) == [
        "BucketPolicy/res: .spec.forProvider.policy: required parameter is missing (set it in forProvider or initProvider)"
    ]
    assert _check(tmp_path, [in_init, observe_only]) == []


def test_a_kind_with_no_crd_fails(tmp_path):
    [error] = _check(tmp_path, [composed("ec2.aws.m.upbound.io/v1beta1", "VPC", {})])

    assert "no CRD or XRD for ec2.aws.m.upbound.io/v1beta1 VPC" in error
    assert "kiln pull-crds" in error


def test_a_child_xr_is_checked_against_its_generated_xrd(tmp_path):
    project = _project(tmp_path)
    xrd_dir = project.compositions_dir / "certificate"
    xrd_dir.mkdir(parents=True)
    xrd_dir.joinpath("xrd.yaml").write_text(
        yaml.safe_dump(
            {
                "apiVersion": "apiextensions.crossplane.io/v2",
                "kind": "CompositeResourceDefinition",
                "spec": {
                    "group": "platform.example.io",
                    "names": {"kind": "Certificate"},
                    "scope": "Namespaced",
                    "versions": [
                        {
                            "name": "v1alpha1",
                            "schema": {
                                "openAPIV3Schema": {
                                    "type": "object",
                                    "properties": {
                                        "spec": {"type": "object", "properties": {"domainName": {"type": "string"}}}
                                    },
                                }
                            },
                        }
                    ],
                },
            }
        )
    )
    index = KindIndex.load(project)
    good = composed("platform.example.io/v1alpha1", "Certificate", {"domainName": "a.example.com"})
    bad = composed("platform.example.io/v1alpha1", "Certificate", {"domain": "a.example.com"})

    assert check_rendered([good], index, "Namespaced") == []
    assert check_rendered([bad], index, "Namespaced") == ["Certificate/res: .spec.domain: field not declared in schema"]


def test_validate_value_accepts_free_form_objects_and_ints_for_numbers():
    schema = {
        "type": "object",
        "properties": {"labels": {"type": "object"}, "ratio": {"type": "number"}, "count": {"type": "integer"}},
    }

    assert validate_value({"labels": {"anything": {"goes": 1}}, "ratio": 1, "count": 2}, schema, "") == []
    assert validate_value({"count": 1.5}, schema, "") == [".count: expected integer, got number"]
    assert validate_value({"count": True}, schema, "") == [".count: expected integer, got boolean"]


def test_validate_value_checks_enums_and_list_items():
    schema = {"type": "array", "items": {"type": "string", "enum": ["a", "b"]}}

    assert validate_value(["a", "c", 3], schema, ".x") == [
        ".x[1]: 'c' is not one of ['a', 'b']",
        ".x[2]: expected string, got integer",
    ]


def test_importing_a_cluster_scoped_crd_into_a_namespaced_project_warns_and_names_the_namespaced_crd(tmp_path):
    project = _project(tmp_path)
    legacy = tmp_path / "crds" / "s3.aws.upbound.io" / "v1beta1" / "bucket.yaml"

    warning = scope_warning_for_import(legacy, project)

    assert "cluster-scoped" in warning
    assert str(tmp_path / "crds" / "s3.aws.m.upbound.io" / "v1beta1" / "bucket.yaml") in warning


def test_importing_a_namespaced_crd_or_into_a_cluster_project_does_not_warn(tmp_path):
    namespaced = tmp_path / "crds" / "s3.aws.m.upbound.io" / "v1beta1" / "bucket.yaml"
    legacy = tmp_path / "crds" / "s3.aws.upbound.io" / "v1beta1" / "bucket.yaml"

    assert scope_warning_for_import(namespaced, _project(tmp_path)) is None
    assert scope_warning_for_import(legacy, _project(tmp_path, scope="Cluster")) is None


def test_the_import_warning_mentions_cluster_scoped_kinds(tmp_path):
    project = _project(tmp_path, kind_scopes={"Legacy": "Cluster"})
    legacy = tmp_path / "crds" / "s3.aws.upbound.io" / "v1beta1" / "bucket.yaml"

    assert "Fine if only Cluster-scoped kinds compose it: Legacy" in scope_warning_for_import(legacy, project)
