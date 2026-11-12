import json

import .schemas_compositions
import .schemas_providers

composeIAMRole = lambda oxr, ocds -> [any] {
    spec: schemas_compositions.IAMRoleSpec = oxr.spec

    _assumeRolePolicy = json.encode({
        Version = "2012-10-17"
        Statement = [{
            Effect = "Allow"
            Principal = {Service = spec.trustedService}
            Action = "sts:AssumeRole"
        }]
    })

    _roleForProvider: schemas_providers.IamAwsmUpboundIoV1beta1RoleSpecForProvider = {
        assumeRolePolicy = _assumeRolePolicy
        managedPolicyArns = spec.managedPolicyArns
        description = spec.description
        tags = spec.tags
    }

    _role = {
        apiVersion = "iam.aws.m.upbound.io/v1beta1"
        kind = "Role"
        metadata.annotations = {
            "crossplane.io/external-name" = spec.roleName
            "krm.kcl.dev/composition-resource-name" = "role"
        }
        spec.forProvider = _roleForProvider
    }

    [_role]
}
