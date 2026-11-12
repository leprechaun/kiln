import .schemas_compositions
import .schemas_providers

composeLambdaFunction = lambda oxr, ocds -> [any] {
    spec: schemas_compositions.LambdaFunctionSpec = oxr.spec

    _environment: schemas_providers.LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderEnvironment = {
        variables = spec.environmentVariables
    } if spec.environmentVariables else Undefined

    _functionForProvider: schemas_providers.LambdaAwsmUpboundIoV1beta1FunctionSpecForProvider = {
        region = spec.region
        handler = spec.handler
        runtime = spec.runtime
        role = spec.role
        s3Bucket = spec.code.s3Bucket
        s3Key = spec.code.s3Key
        memorySize = spec.memorySize
        timeout = spec.timeout
        environment = _environment
        description = spec.description
        tags = spec.tags
    }

    _function = {
        apiVersion = "lambda.aws.m.upbound.io/v1beta1"
        kind = "Function"
        metadata.annotations = {
            "crossplane.io/external-name" = spec.functionName
            "krm.kcl.dev/composition-resource-name" = "function"
        }
        spec.forProvider = _functionForProvider
    }

    _functionUrl = {
        apiVersion = "lambda.aws.m.upbound.io/v1beta1"
        kind = "FunctionURL"
        metadata.annotations = {
            "krm.kcl.dev/composition-resource-name" = "function-url"
        }
        spec.forProvider = schemas_providers.LambdaAwsmUpboundIoV1beta1FunctionURLSpecForProvider {
            region = spec.region
            functionName = spec.functionName
            authorizationType = "NONE"
        }
    } if spec.enableFunctionUrl else None

    _observedFunctionUrl = ocds["function-url"]?.Resource?.status?.atProvider?.functionUrl
    _dxr = {
        apiVersion = oxr.apiVersion
        kind = oxr.kind
        metadata = oxr.metadata
        status.functionUrl = _observedFunctionUrl
    } if _observedFunctionUrl else None

    [_function] + ([_functionUrl] if spec.enableFunctionUrl else []) + ([_dxr] if _dxr else [])
}
