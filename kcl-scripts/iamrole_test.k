import .iamrole

test_builds_role_with_correct_trust_policy = lambda {
    oxr = {spec = {roleName = "my-role", trustedService = "lambda.amazonaws.com"}}
    ocds = {}

    result = iamrole.composeIAMRole(oxr, ocds)

    assert len(result) == 1
    role = result[0]
    assert role.kind == "Role"
    assert role.metadata.annotations["crossplane.io/external-name"] == "my-role"
    assert role.spec.forProvider.assumeRolePolicy == '{"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}]}'
}

test_role_passes_through_optional_fields_when_set = lambda {
    oxr = {
        spec = {
            roleName = "my-role"
            trustedService = "lambda.amazonaws.com"
            managedPolicyArns = ["arn:aws:iam::aws:policy/ReadOnlyAccess"]
            description = "role for my lambda"
            tags = {team = "platform"}
        }
    }
    ocds = {}

    role = iamrole.composeIAMRole(oxr, ocds)[0]

    assert role.spec.forProvider.managedPolicyArns == ["arn:aws:iam::aws:policy/ReadOnlyAccess"]
    assert role.spec.forProvider.description == "role for my lambda"
    assert role.spec.forProvider.tags == {team = "platform"}
}

test_role_omits_optional_fields_when_not_set = lambda {
    oxr = {spec = {roleName = "my-role", trustedService = "lambda.amazonaws.com"}}
    ocds = {}

    role = iamrole.composeIAMRole(oxr, ocds)[0]

    assert role.spec.forProvider.managedPolicyArns == Undefined
    assert role.spec.forProvider.description == Undefined
    assert role.spec.forProvider.tags == Undefined
}

test_tolerates_extra_fields_the_real_control_plane_injects_into_observed_spec = lambda {
    # Real Crossplane XRs carry runtime metadata (e.g. a `crossplane` key)
    # alongside the fields this schema declares -- a hand-built test fixture
    # would never include this, but a real `crossplane composition render`
    # does, so this must not be rejected as an unknown attribute.
    oxr = {
        spec = {
            roleName = "my-role"
            trustedService = "lambda.amazonaws.com"
            crossplane = {compositionRef = {name = "iamrole-kcl-first"}}
        }
    }
    ocds = {}

    result = iamrole.composeIAMRole(oxr, ocds)

    assert len(result) == 1
}
