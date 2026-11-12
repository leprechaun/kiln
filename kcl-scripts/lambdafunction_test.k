import .lambdafunction

test_builds_the_function_resource_from_spec = lambda {
    oxr = {
        spec = {
            functionName = "my-function"
            region = "us-east-1"
            role = "arn:aws:iam::123456789012:role/my-role"
            handler = "index.handler"
            runtime = "python3.12"
            code = {s3Bucket = "my-bucket", s3Key = "code.zip"}
        }
    }
    ocds = {}

    result = lambdafunction.composeLambdaFunction(oxr, ocds)

    assert len(result) == 1
    fn = result[0]
    assert fn.kind == "Function"
    assert fn.metadata.annotations["crossplane.io/external-name"] == "my-function"
    assert fn.spec.forProvider.handler == "index.handler"
    assert fn.spec.forProvider.runtime == "python3.12"
    assert fn.spec.forProvider.role == "arn:aws:iam::123456789012:role/my-role"
    assert fn.spec.forProvider.s3Bucket == "my-bucket"
    assert fn.spec.forProvider.s3Key == "code.zip"
}

test_function_passes_through_optional_fields_when_set = lambda {
    oxr = {
        spec = {
            functionName = "my-function"
            region = "us-east-1"
            role = "arn:aws:iam::123456789012:role/my-role"
            handler = "index.handler"
            runtime = "python3.12"
            code = {s3Bucket = "my-bucket", s3Key = "code.zip"}
            memorySize = 256
            timeout = 30
            environmentVariables = {LOG_LEVEL = "debug"}
            description = "handles widgets"
            tags = {team = "platform"}
        }
    }
    ocds = {}

    fn = lambdafunction.composeLambdaFunction(oxr, ocds)[0]

    assert fn.spec.forProvider.memorySize == 256
    assert fn.spec.forProvider.timeout == 30
    assert fn.spec.forProvider.environment.variables == {LOG_LEVEL = "debug"}
    assert fn.spec.forProvider.description == "handles widgets"
    assert fn.spec.forProvider.tags == {team = "platform"}
}

test_function_omits_optional_fields_when_not_set = lambda {
    oxr = {
        spec = {
            functionName = "my-function"
            region = "us-east-1"
            role = "arn:aws:iam::123456789012:role/my-role"
            handler = "index.handler"
            runtime = "python3.12"
            code = {s3Bucket = "my-bucket", s3Key = "code.zip"}
        }
    }
    ocds = {}

    fn = lambdafunction.composeLambdaFunction(oxr, ocds)[0]

    assert fn.spec.forProvider.memorySize == Undefined
    assert fn.spec.forProvider.timeout == Undefined
    assert fn.spec.forProvider.environment == Undefined
    assert fn.spec.forProvider.description == Undefined
    assert fn.spec.forProvider.tags == Undefined
}

test_function_tolerates_extra_fields_the_real_control_plane_injects_into_observed_spec = lambda {
    oxr = {
        spec = {
            functionName = "my-function"
            region = "us-east-1"
            role = "arn:aws:iam::123456789012:role/my-role"
            handler = "index.handler"
            runtime = "python3.12"
            code = {s3Bucket = "my-bucket", s3Key = "code.zip"}
            crossplane = {compositionRef = {name = "lambdafunction-kcl-first"}}
        }
    }
    ocds = {}

    result = lambdafunction.composeLambdaFunction(oxr, ocds)

    assert len(result) == 1
}

test_omits_function_url_when_not_enabled = lambda {
    oxr = {
        spec = {
            functionName = "my-function"
            region = "us-east-1"
            role = "arn:aws:iam::123456789012:role/my-role"
            handler = "index.handler"
            runtime = "python3.12"
            code = {s3Bucket = "my-bucket", s3Key = "code.zip"}
        }
    }
    ocds = {}

    result = lambdafunction.composeLambdaFunction(oxr, ocds)

    assert len(result) == 1
}

test_builds_function_url_on_cold_start_when_enabled = lambda {
    oxr = {
        spec = {
            functionName = "my-function"
            region = "us-east-1"
            role = "arn:aws:iam::123456789012:role/my-role"
            handler = "index.handler"
            runtime = "python3.12"
            code = {s3Bucket = "my-bucket", s3Key = "code.zip"}
            enableFunctionUrl = True
        }
    }
    ocds = {}

    result = lambdafunction.composeLambdaFunction(oxr, ocds)

    assert len(result) == 2
    url = result[1]
    assert url.kind == "FunctionURL"
    assert url.spec.forProvider.functionName == "my-function"
    assert url.spec.forProvider.authorizationType == "NONE"
}

_functionBaseOxr = {
    apiVersion = "platform.kcl-first.io/v1alpha1"
    kind = "LambdaFunction"
    metadata = {name = "my-function"}
    spec = {
        functionName = "my-function"
        region = "us-east-1"
        role = "arn:aws:iam::123456789012:role/my-role"
        handler = "index.handler"
        runtime = "python3.12"
        code = {s3Bucket = "my-bucket", s3Key = "code.zip"}
        enableFunctionUrl = True
    }
}

test_does_not_surface_status_before_the_url_is_observed = lambda {
    ocds = {}

    result = lambdafunction.composeLambdaFunction(_functionBaseOxr, ocds)

    assert len(result) == 2
}

test_does_not_surface_status_while_the_url_attribute_is_still_unset = lambda {
    ocds = {"function-url" = {Resource = {status = {atProvider = {}}}}}

    result = lambdafunction.composeLambdaFunction(_functionBaseOxr, ocds)

    assert len(result) == 2
}

test_surfaces_function_url_once_observed = lambda {
    ocds = {
        "function-url" = {
            Resource = {status = {atProvider = {functionUrl = "https://abc123.lambda-url.us-east-1.on.aws/"}}}
        }
    }

    result = lambdafunction.composeLambdaFunction(_functionBaseOxr, ocds)

    assert len(result) == 3
    dxr = result[2]
    assert dxr.kind == "LambdaFunction"
    assert dxr.status.functionUrl == "https://abc123.lambda-url.us-east-1.on.aws/"
}
