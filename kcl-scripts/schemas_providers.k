schema IamAwsmUpboundIoV1beta1RoleSpecForProvider:
    r"""
    iam awsm upbound io v1beta1 role spec for provider

    Attributes
    ----------
    assumeRolePolicy : str, default is Undefined, optional
        Policy that grants an entity permission to assume the role. This field is required, but it can be specified in either 'spec.forProvider.assumeRolePolicy' or 'spec.initProvider.assumeRolePolicy'. While it may appear optional in each location individually, the resource requires that it is defined in at least one of them during creation.
    description : str, default is Undefined, optional
        Description of the role.
    forceDetachPolicies : bool, default is Undefined, optional
        Whether to force detaching any policies the role has before destroying it. Defaults to false.
    inlinePolicy : [IamAwsmUpboundIoV1beta1RoleSpecForProviderInlinePolicyItems0], default is Undefined, optional
        Configuration block defining an exclusive set of IAM inline policies associated with the IAM role. See below. If no blocks are configured, Crossplane will not manage any inline policies in this resource. Configuring one empty block (i.e., inline_policy {}) will cause Crossplane to remove all inline policies added out of band on apply.
    managedPolicyArns : [str], default is Undefined, optional
        Set of exclusive IAM managed policy ARNs to attach to the IAM role. If this attribute is not configured, Crossplane will ignore policy attachments to this resource. When configured, Crossplane will align the role's managed policy attachments with this set by attaching or detaching managed policies. Configuring an empty set (i.e., managed_policy_arns = []) will cause Crossplane to remove all managed policy attachments.
    managedPolicyArnsRefs : [IamAwsmUpboundIoV1beta1RoleSpecForProviderManagedPolicyArnsRefsItems0], default is Undefined, optional
        References to Policy in iam to populate managedPolicyArns.
    managedPolicyArnsSelector : IamAwsmUpboundIoV1beta1RoleSpecForProviderManagedPolicyArnsSelector, default is Undefined, optional
        managed policy arns selector
    maxSessionDuration : float, default is Undefined, optional
        Maximum session duration (in seconds) that you want to set for the specified role. If you do not specify a value for this setting, the default maximum of one hour is applied. This setting can have a value from 1 hour to 12 hours.
    path : str, default is Undefined, optional
        Path to the role. See IAM Identifiers for more information.
    permissionsBoundary : str, default is Undefined, optional
        ARN of the policy that is used to set the permissions boundary for the role.
    tags : {str:str}, default is Undefined, optional
        Key-value map of resource tags.
    """


    assumeRolePolicy?: str

    description?: str

    forceDetachPolicies?: bool

    inlinePolicy?: [IamAwsmUpboundIoV1beta1RoleSpecForProviderInlinePolicyItems0]

    managedPolicyArns?: [str]

    managedPolicyArnsRefs?: [IamAwsmUpboundIoV1beta1RoleSpecForProviderManagedPolicyArnsRefsItems0]

    managedPolicyArnsSelector?: IamAwsmUpboundIoV1beta1RoleSpecForProviderManagedPolicyArnsSelector

    maxSessionDuration?: float

    path?: str

    permissionsBoundary?: str

    tags?: {str:str}



schema IamAwsmUpboundIoV1beta1RoleSpecForProviderInlinePolicyItems0:
    r"""
    iam awsm upbound io v1beta1 role spec for provider inline policy items0

    Attributes
    ----------
    name : str, default is Undefined, optional
        Friendly name of the role. See IAM Identifiers for more information.
    policy : str, default is Undefined, optional
        Policy document as a JSON formatted string.
    """


    name?: str

    policy?: str



schema IamAwsmUpboundIoV1beta1RoleSpecForProviderManagedPolicyArnsRefsItems0:
    r"""
    A NamespacedReference to a named object.

    Attributes
    ----------
    name : str, default is Undefined, required
        Name of the referenced object.
    namespace : str, default is Undefined, optional
        Namespace of the referenced object
    policy : IamAwsmUpboundIoV1beta1RoleSpecForProviderManagedPolicyArnsRefsItems0Policy, default is Undefined, optional
        policy
    """


    name: str

    namespace?: str

    policy?: IamAwsmUpboundIoV1beta1RoleSpecForProviderManagedPolicyArnsRefsItems0Policy



schema IamAwsmUpboundIoV1beta1RoleSpecForProviderManagedPolicyArnsRefsItems0Policy:
    r"""
    Policies for referencing.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"



schema IamAwsmUpboundIoV1beta1RoleSpecForProviderManagedPolicyArnsSelector:
    r"""
    Selector for a list of Policy in iam to populate managedPolicyArns.

    Attributes
    ----------
    matchControllerRef : bool, default is Undefined, optional
        MatchControllerRef ensures an object with the same controller reference
        as the selecting object is selected.
    matchLabels : {str:str}, default is Undefined, optional
        MatchLabels ensures an object with matching labels is selected.
    namespace : str, default is Undefined, optional
        Namespace for the selector
    policy : IamAwsmUpboundIoV1beta1RoleSpecForProviderManagedPolicyArnsSelectorPolicy, default is Undefined, optional
        policy
    """


    matchControllerRef?: bool

    matchLabels?: {str:str}

    namespace?: str

    policy?: IamAwsmUpboundIoV1beta1RoleSpecForProviderManagedPolicyArnsSelectorPolicy



schema IamAwsmUpboundIoV1beta1RoleSpecForProviderManagedPolicyArnsSelectorPolicy:
    r"""
    Policies for selection.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"


schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProvider:
    r"""
    lambda awsm upbound io v1beta1 function spec for provider

    Attributes
    ----------
    architectures : [str], default is Undefined, optional
        Instruction set architecture for your Lambda function. Valid values are ["x86_64"] and ["arm64"]. Default is ["x86_64"]. Removing this attribute, function's architecture stays the same.
    capacityProviderConfig : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderCapacityProviderConfig, default is Undefined, optional
        capacity provider config
    codeSha256 : str, default is Undefined, optional
        Base64-encoded representation the source code package file. Use this argument to trigger updates when the function source code changes. For OCI, this value is relayed directly from the image digest. For zip files, this value is the Base64 encoded SHA-256 hash of the .zip file. Layers are not included in the calculation. To trigger updates using a non-standard hashing algorithm, use the source_code_hash argument instead.
    codeSigningConfigArn : str, default is Undefined, optional
        ARN of a code-signing configuration to enable code signing for this function.
    deadLetterConfig : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderDeadLetterConfig, default is Undefined, optional
        dead letter config
    description : str, default is Undefined, optional
        Description of what your Lambda Function does.
    durableConfig : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderDurableConfig, default is Undefined, optional
        durable config
    environment : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderEnvironment, default is Undefined, optional
        environment
    ephemeralStorage : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderEphemeralStorage, default is Undefined, optional
        ephemeral storage
    fileSystemConfig : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderFileSystemConfig, default is Undefined, optional
        file system config
    handler : str, default is Undefined, optional
        Function entry point in your code. Required if package_type is Zip.
    imageConfig : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderImageConfig, default is Undefined, optional
        image config
    imageUri : str, default is Undefined, optional
        ECR image URI containing the function's deployment package. Conflicts with filename and s3_bucket. One of filename, image_uri, or s3_bucket must be specified.
    kmsKeyArn : str, default is Undefined, optional
        ARN of the KMS key used to encrypt environment variables. If not provided when environment variables are in use, AWS Lambda uses a default service key. If provided when environment variables are not in use, the AWS Lambda API does not save this configuration.
    kmsKeyArnRef : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderKmsKeyArnRef, default is Undefined, optional
        kms key arn ref
    kmsKeyArnSelector : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderKmsKeyArnSelector, default is Undefined, optional
        kms key arn selector
    layers : [str], default is Undefined, optional
        List of Lambda Layer Version ARNs (maximum of 5) to attach to your Lambda Function.
    layersRefs : [LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderLayersRefsItems0], default is Undefined, optional
        References to LayerVersion in lambda to populate layers.
    layersSelector : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderLayersSelector, default is Undefined, optional
        layers selector
    loggingConfig : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderLoggingConfig, default is Undefined, optional
        logging config
    memorySize : float, default is Undefined, optional
        Amount of memory in MB your Lambda Function can use at runtime. Valid value between 128 MB to 32,768 MB (32 GB), in 1 MB increments. Defaults to 128.
    packageType : str, default is Undefined, optional
        Lambda deployment package type. Valid values are Zip and Image. Defaults to Zip.
    publish : bool, default is Undefined, optional
        Whether to publish creation/change as new Lambda Function Version. Defaults to false.
    publishTo : str, default is Undefined, optional
        Whether to publish to a alias or version number. Omit for regular version publishing. Option is LATEST_PUBLISHED.
    region : str, default is Undefined, required
        Region where this resource will be managed. Defaults to the Region set in the provider configuration.
        Region is the region you'd like your resource to be created in.
    replaceSecurityGroupsOnDestroy : bool, default is Undefined, optional
        Whether to replace the security groups on the function's VPC configuration prior to destruction. Default is false.
    replacementSecurityGroupIdRefs : [LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderReplacementSecurityGroupIDRefsItems0], default is Undefined, optional
        References to SecurityGroup in ec2 to populate replacementSecurityGroupIds.
    replacementSecurityGroupIdSelector : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderReplacementSecurityGroupIDSelector, default is Undefined, optional
        replacement security group Id selector
    replacementSecurityGroupIds : [str], default is Undefined, optional
        List of security group IDs to assign to the function's VPC configuration prior to destruction. Required if replace_security_groups_on_destroy is true.
    reservedConcurrentExecutions : float, default is Undefined, optional
        Amount of reserved concurrent executions for this lambda function. A value of 0 disables lambda from being triggered and -1 removes any concurrency limitations. Defaults to Unreserved Concurrency Limits -1.
    role : str, default is Undefined, optional
        ARN of the function's execution role. The role provides the function's identity and access to AWS services and resources.
    roleRef : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderRoleRef, default is Undefined, optional
        role ref
    roleSelector : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderRoleSelector, default is Undefined, optional
        role selector
    runtime : str, default is Undefined, optional
        Identifier of the function's runtime. Required if package_type is Zip. See Runtimes for valid values.
    s3Bucket : str, default is Undefined, optional
        S3 bucket location containing the function's deployment package. Conflicts with filename and image_uri. One of filename, image_uri, or s3_bucket must be specified.
    s3BucketRef : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderS3BucketRef, default is Undefined, optional
        s3 bucket ref
    s3BucketSelector : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderS3BucketSelector, default is Undefined, optional
        s3 bucket selector
    s3Key : str, default is Undefined, optional
        S3 key of an object containing the function's deployment package. Required if s3_bucket is set.
    s3ObjectVersion : str, default is Undefined, optional
        Object version containing the function's deployment package. Conflicts with filename and image_uri.
    skipDestroy : bool, default is Undefined, optional
        Whether to retain the old version of a previously deployed Lambda Layer. Default is false.
    snapStart : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderSnapStart, default is Undefined, optional
        snap start
    sourceCodeHash : str, default is Undefined, optional
        Used to trigger updates. Must be set to a base64 encoded SHA256 hash of the package file specified with either filename or s3_key. If you have specified this field manually, it should be the actual (computed) hash of the underlying lambda function specified in the filename, image_uri, s3_bucket fields.
    sourceKmsKeyArn : str, default is Undefined, optional
        ARN of the KMS key used to encrypt the function's .zip deployment package. Conflicts with image_uri.
    tags : {str:str}, default is Undefined, optional
        Key-value map of resource tags.
    tenancyConfig : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderTenancyConfig, default is Undefined, optional
        tenancy config
    timeout : float, default is Undefined, optional
        Amount of time your Lambda Function has to run in seconds. Defaults to 3. Valid between 1 and 900.
    tracingConfig : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderTracingConfig, default is Undefined, optional
        tracing config
    useResourceTimeoutForPropagation : bool, default is Undefined, optional
        Whether to apply resource level timeout values while retrying eventually consistent API operations. By default the provider uses a 5 minute timeout to allow for propagation in the Lambda service. When set to true, this default value is replaced with the configurable resource timeouts. Increased timeout values may be useful in highly active accounts, or regions where propagation delays are inconsistent.
    vpcConfig : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderVpcConfig, default is Undefined, optional
        vpc config
    """


    architectures?: [str]

    capacityProviderConfig?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderCapacityProviderConfig

    codeSha256?: str

    codeSigningConfigArn?: str

    deadLetterConfig?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderDeadLetterConfig

    description?: str

    durableConfig?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderDurableConfig

    environment?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderEnvironment

    ephemeralStorage?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderEphemeralStorage

    fileSystemConfig?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderFileSystemConfig

    handler?: str

    imageConfig?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderImageConfig

    imageUri?: str

    kmsKeyArn?: str

    kmsKeyArnRef?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderKmsKeyArnRef

    kmsKeyArnSelector?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderKmsKeyArnSelector

    layers?: [str]

    layersRefs?: [LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderLayersRefsItems0]

    layersSelector?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderLayersSelector

    loggingConfig?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderLoggingConfig

    memorySize?: float

    packageType?: str

    publish?: bool

    publishTo?: str

    region: str

    replaceSecurityGroupsOnDestroy?: bool

    replacementSecurityGroupIdRefs?: [LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderReplacementSecurityGroupIDRefsItems0]

    replacementSecurityGroupIdSelector?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderReplacementSecurityGroupIDSelector

    replacementSecurityGroupIds?: [str]

    reservedConcurrentExecutions?: float

    role?: str

    roleRef?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderRoleRef

    roleSelector?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderRoleSelector

    runtime?: str

    s3Bucket?: str

    s3BucketRef?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderS3BucketRef

    s3BucketSelector?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderS3BucketSelector

    s3Key?: str

    s3ObjectVersion?: str

    skipDestroy?: bool

    snapStart?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderSnapStart

    sourceCodeHash?: str

    sourceKmsKeyArn?: str

    tags?: {str:str}

    tenancyConfig?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderTenancyConfig

    timeout?: float

    tracingConfig?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderTracingConfig

    useResourceTimeoutForPropagation?: bool

    vpcConfig?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderVpcConfig



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderCapacityProviderConfig:
    r"""
    Configuration block for Lambda Capacity Provider. See below.

    Attributes
    ----------
    lambdaManagedInstancesCapacityProviderConfig : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderCapacityProviderConfigLambdaManagedInstancesCapacityProviderConfig, default is Undefined, optional
        lambda managed instances capacity provider config
    """


    lambdaManagedInstancesCapacityProviderConfig?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderCapacityProviderConfigLambdaManagedInstancesCapacityProviderConfig



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderCapacityProviderConfigLambdaManagedInstancesCapacityProviderConfig:
    r"""
    Configuration block for Lambda Managed Instances Capacity Provider. See below.

    Attributes
    ----------
    capacityProviderArn : str, default is Undefined, optional
        ARN of the Capacity Provider.
    executionEnvironmentMemoryGibPerVcpu : float, default is Undefined, optional
        Memory GiB per vCPU for the execution environment.
    perExecutionEnvironmentMaxConcurrency : float, default is Undefined, optional
        Maximum concurrency per execution environment.
    """


    capacityProviderArn?: str

    executionEnvironmentMemoryGibPerVcpu?: float

    perExecutionEnvironmentMaxConcurrency?: float



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderDeadLetterConfig:
    r"""
    Configuration block for dead letter queue. See below.

    Attributes
    ----------
    targetArn : str, default is Undefined, optional
        ARN of an SNS topic or SQS queue to notify when an invocation fails.
    targetArnRef : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderDeadLetterConfigTargetArnRef, default is Undefined, optional
        target arn ref
    targetArnSelector : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderDeadLetterConfigTargetArnSelector, default is Undefined, optional
        target arn selector
    """


    targetArn?: str

    targetArnRef?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderDeadLetterConfigTargetArnRef

    targetArnSelector?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderDeadLetterConfigTargetArnSelector



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderDeadLetterConfigTargetArnRef:
    r"""
    Reference to a Queue in sqs to populate targetArn.

    Attributes
    ----------
    name : str, default is Undefined, required
        Name of the referenced object.
    namespace : str, default is Undefined, optional
        Namespace of the referenced object
    policy : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderDeadLetterConfigTargetArnRefPolicy, default is Undefined, optional
        policy
    """


    name: str

    namespace?: str

    policy?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderDeadLetterConfigTargetArnRefPolicy



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderDeadLetterConfigTargetArnRefPolicy:
    r"""
    Policies for referencing.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderDeadLetterConfigTargetArnSelector:
    r"""
    Selector for a Queue in sqs to populate targetArn.

    Attributes
    ----------
    matchControllerRef : bool, default is Undefined, optional
        MatchControllerRef ensures an object with the same controller reference
        as the selecting object is selected.
    matchLabels : {str:str}, default is Undefined, optional
        MatchLabels ensures an object with matching labels is selected.
    namespace : str, default is Undefined, optional
        Namespace for the selector
    policy : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderDeadLetterConfigTargetArnSelectorPolicy, default is Undefined, optional
        policy
    """


    matchControllerRef?: bool

    matchLabels?: {str:str}

    namespace?: str

    policy?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderDeadLetterConfigTargetArnSelectorPolicy



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderDeadLetterConfigTargetArnSelectorPolicy:
    r"""
    Policies for selection.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderDurableConfig:
    r"""
    Configuration block for durable function settings. See below. durable_config may only be available in limited regions, including us-east-2.

    Attributes
    ----------
    executionTimeout : float, default is Undefined, optional
        Maximum execution time in seconds for the durable function. Valid value between 1 and 31622400 (366 days).
    retentionPeriod : float, default is Undefined, optional
        Number of days to retain the function's execution state. Valid value between 1 and 90. If not specified, the function's execution state is not retained. Defaults to 14.
    """


    executionTimeout?: float

    retentionPeriod?: float



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderEnvironment:
    r"""
    Configuration block for environment variables. See below.

    Attributes
    ----------
    variables : {str:str}, default is Undefined, optional
        Map of environment variables available to your Lambda function during execution.
    """


    variables?: {str:str}



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderEphemeralStorage:
    r"""
    Amount of ephemeral storage (/tmp) to allocate for the Lambda Function. See below.

    Attributes
    ----------
    size : float, default is Undefined, optional
        Amount of ephemeral storage (/tmp) in MB. Valid between 512 MB and 10,240 MB (10 GB).
    """


    size?: float



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderFileSystemConfig:
    r"""
    Configuration block for EFS or S3 Files file system. See below.

    Attributes
    ----------
    arn : str, default is Undefined, optional
        ARN of the Amazon EFS Access Point, or the Amazon S3 Files access point.
    arnRef : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderFileSystemConfigArnRef, default is Undefined, optional
        arn ref
    arnSelector : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderFileSystemConfigArnSelector, default is Undefined, optional
        arn selector
    localMountPath : str, default is Undefined, optional
        Path where the function can access the file system. Must start with /mnt/.
    """


    arn?: str

    arnRef?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderFileSystemConfigArnRef

    arnSelector?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderFileSystemConfigArnSelector

    localMountPath?: str



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderFileSystemConfigArnRef:
    r"""
    Reference to a AccessPoint in efs to populate arn.

    Attributes
    ----------
    name : str, default is Undefined, required
        Name of the referenced object.
    namespace : str, default is Undefined, optional
        Namespace of the referenced object
    policy : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderFileSystemConfigArnRefPolicy, default is Undefined, optional
        policy
    """


    name: str

    namespace?: str

    policy?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderFileSystemConfigArnRefPolicy



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderFileSystemConfigArnRefPolicy:
    r"""
    Policies for referencing.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderFileSystemConfigArnSelector:
    r"""
    Selector for a AccessPoint in efs to populate arn.

    Attributes
    ----------
    matchControllerRef : bool, default is Undefined, optional
        MatchControllerRef ensures an object with the same controller reference
        as the selecting object is selected.
    matchLabels : {str:str}, default is Undefined, optional
        MatchLabels ensures an object with matching labels is selected.
    namespace : str, default is Undefined, optional
        Namespace for the selector
    policy : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderFileSystemConfigArnSelectorPolicy, default is Undefined, optional
        policy
    """


    matchControllerRef?: bool

    matchLabels?: {str:str}

    namespace?: str

    policy?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderFileSystemConfigArnSelectorPolicy



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderFileSystemConfigArnSelectorPolicy:
    r"""
    Policies for selection.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderImageConfig:
    r"""
    Container image configuration values. See below.

    Attributes
    ----------
    command : [str], default is Undefined, optional
        Parameters to pass to the container image.
    entryPoint : [str], default is Undefined, optional
        Entry point to your application.
    workingDirectory : str, default is Undefined, optional
        Working directory for the container image.
    """


    command?: [str]

    entryPoint?: [str]

    workingDirectory?: str



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderKmsKeyArnRef:
    r"""
    Reference to a Key in kms to populate kmsKeyArn.

    Attributes
    ----------
    name : str, default is Undefined, required
        Name of the referenced object.
    namespace : str, default is Undefined, optional
        Namespace of the referenced object
    policy : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderKmsKeyArnRefPolicy, default is Undefined, optional
        policy
    """


    name: str

    namespace?: str

    policy?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderKmsKeyArnRefPolicy



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderKmsKeyArnRefPolicy:
    r"""
    Policies for referencing.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderKmsKeyArnSelector:
    r"""
    Selector for a Key in kms to populate kmsKeyArn.

    Attributes
    ----------
    matchControllerRef : bool, default is Undefined, optional
        MatchControllerRef ensures an object with the same controller reference
        as the selecting object is selected.
    matchLabels : {str:str}, default is Undefined, optional
        MatchLabels ensures an object with matching labels is selected.
    namespace : str, default is Undefined, optional
        Namespace for the selector
    policy : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderKmsKeyArnSelectorPolicy, default is Undefined, optional
        policy
    """


    matchControllerRef?: bool

    matchLabels?: {str:str}

    namespace?: str

    policy?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderKmsKeyArnSelectorPolicy



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderKmsKeyArnSelectorPolicy:
    r"""
    Policies for selection.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderLayersRefsItems0:
    r"""
    A NamespacedReference to a named object.

    Attributes
    ----------
    name : str, default is Undefined, required
        Name of the referenced object.
    namespace : str, default is Undefined, optional
        Namespace of the referenced object
    policy : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderLayersRefsItems0Policy, default is Undefined, optional
        policy
    """


    name: str

    namespace?: str

    policy?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderLayersRefsItems0Policy



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderLayersRefsItems0Policy:
    r"""
    Policies for referencing.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderLayersSelector:
    r"""
    Selector for a list of LayerVersion in lambda to populate layers.

    Attributes
    ----------
    matchControllerRef : bool, default is Undefined, optional
        MatchControllerRef ensures an object with the same controller reference
        as the selecting object is selected.
    matchLabels : {str:str}, default is Undefined, optional
        MatchLabels ensures an object with matching labels is selected.
    namespace : str, default is Undefined, optional
        Namespace for the selector
    policy : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderLayersSelectorPolicy, default is Undefined, optional
        policy
    """


    matchControllerRef?: bool

    matchLabels?: {str:str}

    namespace?: str

    policy?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderLayersSelectorPolicy



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderLayersSelectorPolicy:
    r"""
    Policies for selection.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderLoggingConfig:
    r"""
    Configuration block for advanced logging settings. See below.

    Attributes
    ----------
    applicationLogLevel : str, default is Undefined, optional
        Detail level of application logs. Valid values: TRACE, DEBUG, INFO, WARN, ERROR, FATAL.
    logFormat : str, default is Undefined, optional
        Log format. Valid values: Text, JSON.
    logGroup : str, default is Undefined, optional
        CloudWatch log group where logs are sent.
    logGroupRef : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderLoggingConfigLogGroupRef, default is Undefined, optional
        log group ref
    logGroupSelector : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderLoggingConfigLogGroupSelector, default is Undefined, optional
        log group selector
    systemLogLevel : str, default is Undefined, optional
        Detail level of Lambda platform logs. Valid values: DEBUG, INFO, WARN.
    """


    applicationLogLevel?: str

    logFormat?: str

    logGroup?: str

    logGroupRef?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderLoggingConfigLogGroupRef

    logGroupSelector?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderLoggingConfigLogGroupSelector

    systemLogLevel?: str



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderLoggingConfigLogGroupRef:
    r"""
    Reference to a Group in cloudwatchlogs to populate logGroup.

    Attributes
    ----------
    name : str, default is Undefined, required
        Name of the referenced object.
    namespace : str, default is Undefined, optional
        Namespace of the referenced object
    policy : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderLoggingConfigLogGroupRefPolicy, default is Undefined, optional
        policy
    """


    name: str

    namespace?: str

    policy?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderLoggingConfigLogGroupRefPolicy



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderLoggingConfigLogGroupRefPolicy:
    r"""
    Policies for referencing.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderLoggingConfigLogGroupSelector:
    r"""
    Selector for a Group in cloudwatchlogs to populate logGroup.

    Attributes
    ----------
    matchControllerRef : bool, default is Undefined, optional
        MatchControllerRef ensures an object with the same controller reference
        as the selecting object is selected.
    matchLabels : {str:str}, default is Undefined, optional
        MatchLabels ensures an object with matching labels is selected.
    namespace : str, default is Undefined, optional
        Namespace for the selector
    policy : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderLoggingConfigLogGroupSelectorPolicy, default is Undefined, optional
        policy
    """


    matchControllerRef?: bool

    matchLabels?: {str:str}

    namespace?: str

    policy?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderLoggingConfigLogGroupSelectorPolicy



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderLoggingConfigLogGroupSelectorPolicy:
    r"""
    Policies for selection.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderReplacementSecurityGroupIDRefsItems0:
    r"""
    A NamespacedReference to a named object.

    Attributes
    ----------
    name : str, default is Undefined, required
        Name of the referenced object.
    namespace : str, default is Undefined, optional
        Namespace of the referenced object
    policy : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderReplacementSecurityGroupIDRefsItems0Policy, default is Undefined, optional
        policy
    """


    name: str

    namespace?: str

    policy?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderReplacementSecurityGroupIDRefsItems0Policy



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderReplacementSecurityGroupIDRefsItems0Policy:
    r"""
    Policies for referencing.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderReplacementSecurityGroupIDSelector:
    r"""
    Selector for a list of SecurityGroup in ec2 to populate replacementSecurityGroupIds.

    Attributes
    ----------
    matchControllerRef : bool, default is Undefined, optional
        MatchControllerRef ensures an object with the same controller reference
        as the selecting object is selected.
    matchLabels : {str:str}, default is Undefined, optional
        MatchLabels ensures an object with matching labels is selected.
    namespace : str, default is Undefined, optional
        Namespace for the selector
    policy : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderReplacementSecurityGroupIDSelectorPolicy, default is Undefined, optional
        policy
    """


    matchControllerRef?: bool

    matchLabels?: {str:str}

    namespace?: str

    policy?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderReplacementSecurityGroupIDSelectorPolicy



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderReplacementSecurityGroupIDSelectorPolicy:
    r"""
    Policies for selection.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderRoleRef:
    r"""
    Reference to a Role in iam to populate role.

    Attributes
    ----------
    name : str, default is Undefined, required
        Name of the referenced object.
    namespace : str, default is Undefined, optional
        Namespace of the referenced object
    policy : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderRoleRefPolicy, default is Undefined, optional
        policy
    """


    name: str

    namespace?: str

    policy?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderRoleRefPolicy



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderRoleRefPolicy:
    r"""
    Policies for referencing.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderRoleSelector:
    r"""
    Selector for a Role in iam to populate role.

    Attributes
    ----------
    matchControllerRef : bool, default is Undefined, optional
        MatchControllerRef ensures an object with the same controller reference
        as the selecting object is selected.
    matchLabels : {str:str}, default is Undefined, optional
        MatchLabels ensures an object with matching labels is selected.
    namespace : str, default is Undefined, optional
        Namespace for the selector
    policy : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderRoleSelectorPolicy, default is Undefined, optional
        policy
    """


    matchControllerRef?: bool

    matchLabels?: {str:str}

    namespace?: str

    policy?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderRoleSelectorPolicy



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderRoleSelectorPolicy:
    r"""
    Policies for selection.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderS3BucketRef:
    r"""
    Reference to a Bucket in s3 to populate s3Bucket.

    Attributes
    ----------
    name : str, default is Undefined, required
        Name of the referenced object.
    namespace : str, default is Undefined, optional
        Namespace of the referenced object
    policy : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderS3BucketRefPolicy, default is Undefined, optional
        policy
    """


    name: str

    namespace?: str

    policy?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderS3BucketRefPolicy



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderS3BucketRefPolicy:
    r"""
    Policies for referencing.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderS3BucketSelector:
    r"""
    Selector for a Bucket in s3 to populate s3Bucket.

    Attributes
    ----------
    matchControllerRef : bool, default is Undefined, optional
        MatchControllerRef ensures an object with the same controller reference
        as the selecting object is selected.
    matchLabels : {str:str}, default is Undefined, optional
        MatchLabels ensures an object with matching labels is selected.
    namespace : str, default is Undefined, optional
        Namespace for the selector
    policy : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderS3BucketSelectorPolicy, default is Undefined, optional
        policy
    """


    matchControllerRef?: bool

    matchLabels?: {str:str}

    namespace?: str

    policy?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderS3BucketSelectorPolicy



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderS3BucketSelectorPolicy:
    r"""
    Policies for selection.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderSnapStart:
    r"""
    Configuration block for snap start settings. See below.

    Attributes
    ----------
    applyOn : str, default is Undefined, optional
        When to apply snap start optimization. Valid value: PublishedVersions.
    """


    applyOn?: str



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderTenancyConfig:
    r"""
    Configuration block for Tenancy. See below.

    Attributes
    ----------
    tenantIsolationMode : str, default is Undefined, optional
        Tenant Isolation Mode. Valid values: PER_TENANT.
    """


    tenantIsolationMode?: str



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderTracingConfig:
    r"""
    Configuration block for X-Ray tracing. See below.

    Attributes
    ----------
    mode : str, default is Undefined, optional
        X-Ray tracing mode. Valid values: Active, PassThrough.
    """


    mode?: str



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderVpcConfig:
    r"""
    Configuration block for VPC. See below.

    Attributes
    ----------
    ipv6AllowedForDualStack : bool, default is Undefined, optional
        Whether to allow outbound IPv6 traffic on VPC functions connected to dual-stack subnets. Default: false.
    securityGroupIdRefs : [LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderVpcConfigSecurityGroupIDRefsItems0], default is Undefined, optional
        References to SecurityGroup in ec2 to populate securityGroupIds.
    securityGroupIdSelector : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderVpcConfigSecurityGroupIDSelector, default is Undefined, optional
        security group Id selector
    securityGroupIds : [str], default is Undefined, optional
        List of security group IDs associated with the Lambda function.
    subnetIdRefs : [LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderVpcConfigSubnetIDRefsItems0], default is Undefined, optional
        References to Subnet in ec2 to populate subnetIds.
    subnetIdSelector : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderVpcConfigSubnetIDSelector, default is Undefined, optional
        subnet Id selector
    subnetIds : [str], default is Undefined, optional
        List of subnet IDs associated with the Lambda function.
    """


    ipv6AllowedForDualStack?: bool

    securityGroupIdRefs?: [LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderVpcConfigSecurityGroupIDRefsItems0]

    securityGroupIdSelector?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderVpcConfigSecurityGroupIDSelector

    securityGroupIds?: [str]

    subnetIdRefs?: [LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderVpcConfigSubnetIDRefsItems0]

    subnetIdSelector?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderVpcConfigSubnetIDSelector

    subnetIds?: [str]



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderVpcConfigSecurityGroupIDRefsItems0:
    r"""
    A NamespacedReference to a named object.

    Attributes
    ----------
    name : str, default is Undefined, required
        Name of the referenced object.
    namespace : str, default is Undefined, optional
        Namespace of the referenced object
    policy : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderVpcConfigSecurityGroupIDRefsItems0Policy, default is Undefined, optional
        policy
    """


    name: str

    namespace?: str

    policy?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderVpcConfigSecurityGroupIDRefsItems0Policy



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderVpcConfigSecurityGroupIDRefsItems0Policy:
    r"""
    Policies for referencing.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderVpcConfigSecurityGroupIDSelector:
    r"""
    Selector for a list of SecurityGroup in ec2 to populate securityGroupIds.

    Attributes
    ----------
    matchControllerRef : bool, default is Undefined, optional
        MatchControllerRef ensures an object with the same controller reference
        as the selecting object is selected.
    matchLabels : {str:str}, default is Undefined, optional
        MatchLabels ensures an object with matching labels is selected.
    namespace : str, default is Undefined, optional
        Namespace for the selector
    policy : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderVpcConfigSecurityGroupIDSelectorPolicy, default is Undefined, optional
        policy
    """


    matchControllerRef?: bool

    matchLabels?: {str:str}

    namespace?: str

    policy?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderVpcConfigSecurityGroupIDSelectorPolicy



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderVpcConfigSecurityGroupIDSelectorPolicy:
    r"""
    Policies for selection.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderVpcConfigSubnetIDRefsItems0:
    r"""
    A NamespacedReference to a named object.

    Attributes
    ----------
    name : str, default is Undefined, required
        Name of the referenced object.
    namespace : str, default is Undefined, optional
        Namespace of the referenced object
    policy : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderVpcConfigSubnetIDRefsItems0Policy, default is Undefined, optional
        policy
    """


    name: str

    namespace?: str

    policy?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderVpcConfigSubnetIDRefsItems0Policy



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderVpcConfigSubnetIDRefsItems0Policy:
    r"""
    Policies for referencing.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderVpcConfigSubnetIDSelector:
    r"""
    Selector for a list of Subnet in ec2 to populate subnetIds.

    Attributes
    ----------
    matchControllerRef : bool, default is Undefined, optional
        MatchControllerRef ensures an object with the same controller reference
        as the selecting object is selected.
    matchLabels : {str:str}, default is Undefined, optional
        MatchLabels ensures an object with matching labels is selected.
    namespace : str, default is Undefined, optional
        Namespace for the selector
    policy : LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderVpcConfigSubnetIDSelectorPolicy, default is Undefined, optional
        policy
    """


    matchControllerRef?: bool

    matchLabels?: {str:str}

    namespace?: str

    policy?: LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderVpcConfigSubnetIDSelectorPolicy



schema LambdaAwsmUpboundIoV1beta1FunctionSpecForProviderVpcConfigSubnetIDSelectorPolicy:
    r"""
    Policies for selection.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"


schema LambdaAwsmUpboundIoV1beta1FunctionURLSpecForProvider:
    r"""
    lambda awsm upbound io v1beta1 function URL spec for provider

    Attributes
    ----------
    authorizationType : str, default is Undefined, optional
        Type of authentication that the function URL uses. Valid values are AWS_IAM and NONE.
    cors : LambdaAwsmUpboundIoV1beta1FunctionURLSpecForProviderCors, default is Undefined, optional
        cors
    functionName : str, default is Undefined, optional
        Name or ARN of the Lambda function.
    functionNameRef : LambdaAwsmUpboundIoV1beta1FunctionURLSpecForProviderFunctionNameRef, default is Undefined, optional
        function name ref
    functionNameSelector : LambdaAwsmUpboundIoV1beta1FunctionURLSpecForProviderFunctionNameSelector, default is Undefined, optional
        function name selector
    invokeMode : str, default is Undefined, optional
        How the Lambda function responds to an invocation. Valid values are BUFFERED (default) and RESPONSE_STREAM.
    qualifier : str, default is Undefined, optional
        Alias name or $LATEST.
    region : str, default is Undefined, required
        Region where this resource will be managed. Defaults to the Region set in the provider configuration.
        Region is the region you'd like your resource to be created in.
    """


    authorizationType?: str

    cors?: LambdaAwsmUpboundIoV1beta1FunctionURLSpecForProviderCors

    functionName?: str

    functionNameRef?: LambdaAwsmUpboundIoV1beta1FunctionURLSpecForProviderFunctionNameRef

    functionNameSelector?: LambdaAwsmUpboundIoV1beta1FunctionURLSpecForProviderFunctionNameSelector

    invokeMode?: str

    qualifier?: str

    region: str



schema LambdaAwsmUpboundIoV1beta1FunctionURLSpecForProviderCors:
    r"""
    Cross-origin resource sharing (CORS) settings for the function URL. See below.

    Attributes
    ----------
    allowCredentials : bool, default is Undefined, optional
        Whether to allow cookies or other credentials in requests to the function URL.
    allowHeaders : [str], default is Undefined, optional
        HTTP headers that origins can include in requests to the function URL.
    allowMethods : [str], default is Undefined, optional
        HTTP methods that are allowed when calling the function URL.
    allowOrigins : [str], default is Undefined, optional
        Origins that can access the function URL.
    exposeHeaders : [str], default is Undefined, optional
        HTTP headers in your function response that you want to expose to origins that call the function URL.
    maxAge : float, default is Undefined, optional
        Maximum amount of time, in seconds, that web browsers can cache results of a preflight request. Maximum value is 86400.
    """


    allowCredentials?: bool

    allowHeaders?: [str]

    allowMethods?: [str]

    allowOrigins?: [str]

    exposeHeaders?: [str]

    maxAge?: float



schema LambdaAwsmUpboundIoV1beta1FunctionURLSpecForProviderFunctionNameRef:
    r"""
    Reference to a Function in lambda to populate functionName.

    Attributes
    ----------
    name : str, default is Undefined, required
        Name of the referenced object.
    namespace : str, default is Undefined, optional
        Namespace of the referenced object
    policy : LambdaAwsmUpboundIoV1beta1FunctionURLSpecForProviderFunctionNameRefPolicy, default is Undefined, optional
        policy
    """


    name: str

    namespace?: str

    policy?: LambdaAwsmUpboundIoV1beta1FunctionURLSpecForProviderFunctionNameRefPolicy



schema LambdaAwsmUpboundIoV1beta1FunctionURLSpecForProviderFunctionNameRefPolicy:
    r"""
    Policies for referencing.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"



schema LambdaAwsmUpboundIoV1beta1FunctionURLSpecForProviderFunctionNameSelector:
    r"""
    Selector for a Function in lambda to populate functionName.

    Attributes
    ----------
    matchControllerRef : bool, default is Undefined, optional
        MatchControllerRef ensures an object with the same controller reference
        as the selecting object is selected.
    matchLabels : {str:str}, default is Undefined, optional
        MatchLabels ensures an object with matching labels is selected.
    namespace : str, default is Undefined, optional
        Namespace for the selector
    policy : LambdaAwsmUpboundIoV1beta1FunctionURLSpecForProviderFunctionNameSelectorPolicy, default is Undefined, optional
        policy
    """


    matchControllerRef?: bool

    matchLabels?: {str:str}

    namespace?: str

    policy?: LambdaAwsmUpboundIoV1beta1FunctionURLSpecForProviderFunctionNameSelectorPolicy



schema LambdaAwsmUpboundIoV1beta1FunctionURLSpecForProviderFunctionNameSelectorPolicy:
    r"""
    Policies for selection.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"


schema AcmAwsmUpboundIoV1beta1CertificateSpecForProvider:
    r"""
    acm awsm upbound io v1beta1 certificate spec for provider

    Attributes
    ----------
    certificateAuthorityArn : str, default is Undefined, optional
        ARN of an ACM PCA
    certificateAuthorityArnRef : AcmAwsmUpboundIoV1beta1CertificateSpecForProviderCertificateAuthorityArnRef, default is Undefined, optional
        certificate authority arn ref
    certificateAuthorityArnSelector : AcmAwsmUpboundIoV1beta1CertificateSpecForProviderCertificateAuthorityArnSelector, default is Undefined, optional
        certificate authority arn selector
    certificateBody : str, default is Undefined, optional
        Certificate's PEM-formatted public key
    certificateChain : str, default is Undefined, optional
        Certificate's PEM-formatted chain
    domainName : str, default is Undefined, optional
        Domain name for which the certificate should be issued
    earlyRenewalDuration : str, default is Undefined, optional
        Amount of time to start automatic renewal process before expiration.
        Has no effect if less than 60 days.
        Represented by either
        a subset of RFC 3339 duration supporting years, months, and days (e.g., P90D),
        or a string such as 2160h.
    keyAlgorithm : str, default is Undefined, optional
        Specifies the algorithm of the public and private key pair that your Amazon issued certificate uses to encrypt data. See ACM Certificate characteristics for more details.
    options : AcmAwsmUpboundIoV1beta1CertificateSpecForProviderOptions, default is Undefined, optional
        options
    privateKeySecretRef : AcmAwsmUpboundIoV1beta1CertificateSpecForProviderPrivateKeySecretRef, default is Undefined, optional
        private key secret ref
    privateKeyWo : str, default is Undefined, optional
        Certificate's PEM-formatted private key. Conflicts with private_key. If set, requires private_key_wo_version to be set.
    privateKeyWoVersion : float, default is Undefined, optional
        Required when private_key_wo is set. Changing this value triggers an update to private_key_wo.
    region : str, default is Undefined, required
        Region where this resource will be managed. Defaults to the Region set in the provider configuration.
        Region is the region you'd like your resource to be created in.
    subjectAlternativeNames : [str], default is Undefined, optional
        Set of domains that should be SANs in the issued certificate.
    tags : {str:str}, default is Undefined, optional
        Key-value map of resource tags.
    validationMethod : str, default is Undefined, optional
        Which method to use for validation. DNS or EMAIL are valid.
    validationOption : [AcmAwsmUpboundIoV1beta1CertificateSpecForProviderValidationOptionItems0], default is Undefined, optional
        Configuration block used to specify information about the initial validation of each domain name. Detailed below.
    """


    certificateAuthorityArn?: str

    certificateAuthorityArnRef?: AcmAwsmUpboundIoV1beta1CertificateSpecForProviderCertificateAuthorityArnRef

    certificateAuthorityArnSelector?: AcmAwsmUpboundIoV1beta1CertificateSpecForProviderCertificateAuthorityArnSelector

    certificateBody?: str

    certificateChain?: str

    domainName?: str

    earlyRenewalDuration?: str

    keyAlgorithm?: str

    options?: AcmAwsmUpboundIoV1beta1CertificateSpecForProviderOptions

    privateKeySecretRef?: AcmAwsmUpboundIoV1beta1CertificateSpecForProviderPrivateKeySecretRef

    privateKeyWo?: str

    privateKeyWoVersion?: float

    region: str

    subjectAlternativeNames?: [str]

    tags?: {str:str}

    validationMethod?: str

    validationOption?: [AcmAwsmUpboundIoV1beta1CertificateSpecForProviderValidationOptionItems0]



schema AcmAwsmUpboundIoV1beta1CertificateSpecForProviderCertificateAuthorityArnRef:
    r"""
    Reference to a CertificateAuthority in acmpca to populate certificateAuthorityArn.

    Attributes
    ----------
    name : str, default is Undefined, required
        Name of the referenced object.
    namespace : str, default is Undefined, optional
        Namespace of the referenced object
    policy : AcmAwsmUpboundIoV1beta1CertificateSpecForProviderCertificateAuthorityArnRefPolicy, default is Undefined, optional
        policy
    """


    name: str

    namespace?: str

    policy?: AcmAwsmUpboundIoV1beta1CertificateSpecForProviderCertificateAuthorityArnRefPolicy



schema AcmAwsmUpboundIoV1beta1CertificateSpecForProviderCertificateAuthorityArnRefPolicy:
    r"""
    Policies for referencing.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"



schema AcmAwsmUpboundIoV1beta1CertificateSpecForProviderCertificateAuthorityArnSelector:
    r"""
    Selector for a CertificateAuthority in acmpca to populate certificateAuthorityArn.

    Attributes
    ----------
    matchControllerRef : bool, default is Undefined, optional
        MatchControllerRef ensures an object with the same controller reference
        as the selecting object is selected.
    matchLabels : {str:str}, default is Undefined, optional
        MatchLabels ensures an object with matching labels is selected.
    namespace : str, default is Undefined, optional
        Namespace for the selector
    policy : AcmAwsmUpboundIoV1beta1CertificateSpecForProviderCertificateAuthorityArnSelectorPolicy, default is Undefined, optional
        policy
    """


    matchControllerRef?: bool

    matchLabels?: {str:str}

    namespace?: str

    policy?: AcmAwsmUpboundIoV1beta1CertificateSpecForProviderCertificateAuthorityArnSelectorPolicy



schema AcmAwsmUpboundIoV1beta1CertificateSpecForProviderCertificateAuthorityArnSelectorPolicy:
    r"""
    Policies for selection.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"



schema AcmAwsmUpboundIoV1beta1CertificateSpecForProviderOptions:
    r"""
    Configuration block used to set certificate options. Detailed below.

    Attributes
    ----------
    certificateTransparencyLoggingPreference : str, default is Undefined, optional
        Whether certificate details should be added to a certificate transparency log. Valid values are ENABLED or DISABLED. See https://docs.aws.amazon.com/acm/latest/userguide/acm-concepts.html#concept-transparency for more details.
    export : str, default is Undefined, optional
        Whether the certificate can be exported. Valid values are ENABLED or DISABLED (default). Note Issuing an exportable certificate is subject to additional charges. See AWS Certificate Manager pricing for more details.
    """


    certificateTransparencyLoggingPreference?: str

    export?: str



schema AcmAwsmUpboundIoV1beta1CertificateSpecForProviderPrivateKeySecretRef:
    r"""
    Certificate's PEM-formatted private key. Conflicts with private_key_wo.

    Attributes
    ----------
    key : str, default is Undefined, required
        key
    name : str, default is Undefined, required
        Name of the secret.
    """


    key: str

    name: str



schema AcmAwsmUpboundIoV1beta1CertificateSpecForProviderValidationOptionItems0:
    r"""
    acm awsm upbound io v1beta1 certificate spec for provider validation option items0

    Attributes
    ----------
    domainName : str, default is Undefined, optional
        Fully qualified domain name (FQDN) in the certificate.
    validationDomain : str, default is Undefined, optional
        Domain name that you want ACM to use to send you validation emails. This domain name is the suffix of the email addresses that you want ACM to use. This must be the same as the domain_name value or a superdomain of the domain_name value. For example, if you request a certificate for "testing.example.com", you can specify "example.com" for this value.
    """


    domainName?: str

    validationDomain?: str


schema AcmAwsmUpboundIoV1beta1CertificateValidationSpecForProvider:
    r"""
    acm awsm upbound io v1beta1 certificate validation spec for provider

    Attributes
    ----------
    certificateArn : str, default is Undefined, optional
        ARN of the certificate that is being validated.
    certificateArnRef : AcmAwsmUpboundIoV1beta1CertificateValidationSpecForProviderCertificateArnRef, default is Undefined, optional
        certificate arn ref
    certificateArnSelector : AcmAwsmUpboundIoV1beta1CertificateValidationSpecForProviderCertificateArnSelector, default is Undefined, optional
        certificate arn selector
    region : str, default is Undefined, required
        Region where this resource will be managed. Defaults to the Region set in the provider configuration.
        Region is the region you'd like your resource to be created in.
    validationRecordFqdns : [str], default is Undefined, optional
        List of FQDNs that implement the validation. Only valid for DNS validation method ACM certificates. If this is set, the resource can implement additional sanity checks and has an explicit dependency on the resource that is implementing the validation
    """


    certificateArn?: str

    certificateArnRef?: AcmAwsmUpboundIoV1beta1CertificateValidationSpecForProviderCertificateArnRef

    certificateArnSelector?: AcmAwsmUpboundIoV1beta1CertificateValidationSpecForProviderCertificateArnSelector

    region: str

    validationRecordFqdns?: [str]



schema AcmAwsmUpboundIoV1beta1CertificateValidationSpecForProviderCertificateArnRef:
    r"""
    Reference to a Certificate in acm to populate certificateArn.

    Attributes
    ----------
    name : str, default is Undefined, required
        Name of the referenced object.
    namespace : str, default is Undefined, optional
        Namespace of the referenced object
    policy : AcmAwsmUpboundIoV1beta1CertificateValidationSpecForProviderCertificateArnRefPolicy, default is Undefined, optional
        policy
    """


    name: str

    namespace?: str

    policy?: AcmAwsmUpboundIoV1beta1CertificateValidationSpecForProviderCertificateArnRefPolicy



schema AcmAwsmUpboundIoV1beta1CertificateValidationSpecForProviderCertificateArnRefPolicy:
    r"""
    Policies for referencing.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"



schema AcmAwsmUpboundIoV1beta1CertificateValidationSpecForProviderCertificateArnSelector:
    r"""
    Selector for a Certificate in acm to populate certificateArn.

    Attributes
    ----------
    matchControllerRef : bool, default is Undefined, optional
        MatchControllerRef ensures an object with the same controller reference
        as the selecting object is selected.
    matchLabels : {str:str}, default is Undefined, optional
        MatchLabels ensures an object with matching labels is selected.
    namespace : str, default is Undefined, optional
        Namespace for the selector
    policy : AcmAwsmUpboundIoV1beta1CertificateValidationSpecForProviderCertificateArnSelectorPolicy, default is Undefined, optional
        policy
    """


    matchControllerRef?: bool

    matchLabels?: {str:str}

    namespace?: str

    policy?: AcmAwsmUpboundIoV1beta1CertificateValidationSpecForProviderCertificateArnSelectorPolicy



schema AcmAwsmUpboundIoV1beta1CertificateValidationSpecForProviderCertificateArnSelectorPolicy:
    r"""
    Policies for selection.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"


schema Route53AwsmUpboundIoV1beta1RecordSpecForProvider:
    r"""
    route53 awsm upbound io v1beta1 record spec for provider

    Attributes
    ----------
    alias : Route53AwsmUpboundIoV1beta1RecordSpecForProviderAlias, default is Undefined, optional
        alias
    allowOverwrite : bool, default is Undefined, optional
        false by default. This configuration is not recommended for most environments.
    cidrRoutingPolicy : Route53AwsmUpboundIoV1beta1RecordSpecForProviderCidrRoutingPolicy, default is Undefined, optional
        cidr routing policy
    failoverRoutingPolicy : Route53AwsmUpboundIoV1beta1RecordSpecForProviderFailoverRoutingPolicy, default is Undefined, optional
        failover routing policy
    geolocationRoutingPolicy : Route53AwsmUpboundIoV1beta1RecordSpecForProviderGeolocationRoutingPolicy, default is Undefined, optional
        geolocation routing policy
    geoproximityRoutingPolicy : Route53AwsmUpboundIoV1beta1RecordSpecForProviderGeoproximityRoutingPolicy, default is Undefined, optional
        geoproximity routing policy
    healthCheckId : str, default is Undefined, optional
        The health check the record should be associated with.
    healthCheckIdRef : Route53AwsmUpboundIoV1beta1RecordSpecForProviderHealthCheckIDRef, default is Undefined, optional
        health check Id ref
    healthCheckIdSelector : Route53AwsmUpboundIoV1beta1RecordSpecForProviderHealthCheckIDSelector, default is Undefined, optional
        health check Id selector
    latencyRoutingPolicy : Route53AwsmUpboundIoV1beta1RecordSpecForProviderLatencyRoutingPolicy, default is Undefined, optional
        latency routing policy
    multivalueAnswerRoutingPolicy : bool, default is Undefined, optional
        Set to true to indicate a multivalue answer routing policy. Conflicts with any other routing policy.
    name : str, default is Undefined, optional
        The name of the record.
    records : [str], default is Undefined, optional
        A string list of records.g., "first255characters\"\"morecharacters").
    recordsRefs : [Route53AwsmUpboundIoV1beta1RecordSpecForProviderRecordsRefsItems0], default is Undefined, optional
        References to EIP in ec2 to populate records.
    recordsSelector : Route53AwsmUpboundIoV1beta1RecordSpecForProviderRecordsSelector, default is Undefined, optional
        records selector
    setIdentifier : str, default is Undefined, optional
        Unique identifier to differentiate records with routing policies from one another. Required if using cidr_routing_policy, failover_routing_policy, geolocation_routing_policy,geoproximity_routing_policy, latency_routing_policy, multivalue_answer_routing_policy, or weighted_routing_policy.
    ttl : float, default is Undefined, optional
        The TTL of the record.
    $type : str, default is Undefined, optional
        The record type. Valid values are A, AAAA, CAA, CNAME, DS, HTTPS, MX, NAPTR, NS, PTR, SOA, SPF, SRV, SSHFP, SVCB, TLSA, and TXT.
    weightedRoutingPolicy : Route53AwsmUpboundIoV1beta1RecordSpecForProviderWeightedRoutingPolicy, default is Undefined, optional
        weighted routing policy
    zoneId : str, default is Undefined, optional
        The ID of the hosted zone to contain this record.
    zoneIdRef : Route53AwsmUpboundIoV1beta1RecordSpecForProviderZoneIDRef, default is Undefined, optional
        zone Id ref
    zoneIdSelector : Route53AwsmUpboundIoV1beta1RecordSpecForProviderZoneIDSelector, default is Undefined, optional
        zone Id selector
    """


    alias?: Route53AwsmUpboundIoV1beta1RecordSpecForProviderAlias

    allowOverwrite?: bool

    cidrRoutingPolicy?: Route53AwsmUpboundIoV1beta1RecordSpecForProviderCidrRoutingPolicy

    failoverRoutingPolicy?: Route53AwsmUpboundIoV1beta1RecordSpecForProviderFailoverRoutingPolicy

    geolocationRoutingPolicy?: Route53AwsmUpboundIoV1beta1RecordSpecForProviderGeolocationRoutingPolicy

    geoproximityRoutingPolicy?: Route53AwsmUpboundIoV1beta1RecordSpecForProviderGeoproximityRoutingPolicy

    healthCheckId?: str

    healthCheckIdRef?: Route53AwsmUpboundIoV1beta1RecordSpecForProviderHealthCheckIDRef

    healthCheckIdSelector?: Route53AwsmUpboundIoV1beta1RecordSpecForProviderHealthCheckIDSelector

    latencyRoutingPolicy?: Route53AwsmUpboundIoV1beta1RecordSpecForProviderLatencyRoutingPolicy

    multivalueAnswerRoutingPolicy?: bool

    name?: str

    records?: [str]

    recordsRefs?: [Route53AwsmUpboundIoV1beta1RecordSpecForProviderRecordsRefsItems0]

    recordsSelector?: Route53AwsmUpboundIoV1beta1RecordSpecForProviderRecordsSelector

    setIdentifier?: str

    ttl?: float

    $type?: str

    weightedRoutingPolicy?: Route53AwsmUpboundIoV1beta1RecordSpecForProviderWeightedRoutingPolicy

    zoneId?: str

    zoneIdRef?: Route53AwsmUpboundIoV1beta1RecordSpecForProviderZoneIDRef

    zoneIdSelector?: Route53AwsmUpboundIoV1beta1RecordSpecForProviderZoneIDSelector



schema Route53AwsmUpboundIoV1beta1RecordSpecForProviderAlias:
    r"""
    An alias block. Conflicts with ttl & records.
    Documented below.

    Attributes
    ----------
    evaluateTargetHealth : bool, default is Undefined, optional
        Set to true if you want Route 53 to determine whether to respond to DNS queries using this resource record set by checking the health of the resource record set. Some resources have special requirements, see related part of documentation.
    name : str, default is Undefined, optional
        The name of the record.
    zoneId : str, default is Undefined, optional
        The ID of the hosted zone to contain this record.
    """


    evaluateTargetHealth?: bool

    name?: str

    zoneId?: str



schema Route53AwsmUpboundIoV1beta1RecordSpecForProviderCidrRoutingPolicy:
    r"""
    A block indicating a routing policy based on the IP network ranges of requestors. Conflicts with any other routing policy. Documented below.

    Attributes
    ----------
    collectionId : str, default is Undefined, optional
        The CIDR collection ID. See the aws_route53_cidr_collection resource for more details.
    locationName : str, default is Undefined, optional
        The CIDR collection location name. See the aws_route53_cidr_location resource for more details. A location_name with an asterisk "*" can be used to create a default CIDR record. collection_id is still required for default record.
    """


    collectionId?: str

    locationName?: str



schema Route53AwsmUpboundIoV1beta1RecordSpecForProviderFailoverRoutingPolicy:
    r"""
    A block indicating the routing behavior when associated health check fails. Conflicts with any other routing policy. Documented below.

    Attributes
    ----------
    $type : str, default is Undefined, optional
        The record type. Valid values are A, AAAA, CAA, CNAME, DS, HTTPS, MX, NAPTR, NS, PTR, SOA, SPF, SRV, SSHFP, SVCB, TLSA, and TXT.
    """


    $type?: str



schema Route53AwsmUpboundIoV1beta1RecordSpecForProviderGeolocationRoutingPolicy:
    r"""
    A block indicating a routing policy based on the geolocation of the requestor. Conflicts with any other routing policy. Documented below.

    Attributes
    ----------
    continent : str, default is Undefined, optional
        A two-letter continent code. See http://docs.aws.amazon.com/Route53/latest/APIReference/API_GetGeoLocation.html for code details. Either continent or country must be specified.
    country : str, default is Undefined, optional
        A two-character country code or * to indicate a default resource record set.
    subdivision : str, default is Undefined, optional
        A subdivision code for a country.
    """


    continent?: str

    country?: str

    subdivision?: str



schema Route53AwsmUpboundIoV1beta1RecordSpecForProviderGeoproximityRoutingPolicy:
    r"""
    A block indicating a routing policy based on the geoproximity of the requestor. Conflicts with any other routing policy. Documented below.

    Attributes
    ----------
    awsRegion : str, default is Undefined, optional
        A AWS region where the resource is present.
    bias : float, default is Undefined, optional
        Route more traffic or less traffic to the resource by specifying a value ranges between -90 to 90. See https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-policy-geoproximity.html for bias details.
    coordinates : [Route53AwsmUpboundIoV1beta1RecordSpecForProviderGeoproximityRoutingPolicyCoordinatesItems0], default is Undefined, optional
        Specify latitude and longitude for routing traffic to non-AWS resources.
    localZoneGroup : str, default is Undefined, optional
        A AWS local zone group where the resource is present. See https://docs.aws.amazon.com/local-zones/latest/ug/available-local-zones.html for local zone group list.
    """


    awsRegion?: str

    bias?: float

    coordinates?: [Route53AwsmUpboundIoV1beta1RecordSpecForProviderGeoproximityRoutingPolicyCoordinatesItems0]

    localZoneGroup?: str



schema Route53AwsmUpboundIoV1beta1RecordSpecForProviderGeoproximityRoutingPolicyCoordinatesItems0:
    r"""
    route53 awsm upbound io v1beta1 record spec for provider geoproximity routing policy coordinates items0

    Attributes
    ----------
    latitude : str, default is Undefined, optional
        latitude
    longitude : str, default is Undefined, optional
        longitude
    """


    latitude?: str

    longitude?: str



schema Route53AwsmUpboundIoV1beta1RecordSpecForProviderHealthCheckIDRef:
    r"""
    Reference to a HealthCheck in route53 to populate healthCheckId.

    Attributes
    ----------
    name : str, default is Undefined, required
        Name of the referenced object.
    namespace : str, default is Undefined, optional
        Namespace of the referenced object
    policy : Route53AwsmUpboundIoV1beta1RecordSpecForProviderHealthCheckIDRefPolicy, default is Undefined, optional
        policy
    """


    name: str

    namespace?: str

    policy?: Route53AwsmUpboundIoV1beta1RecordSpecForProviderHealthCheckIDRefPolicy



schema Route53AwsmUpboundIoV1beta1RecordSpecForProviderHealthCheckIDRefPolicy:
    r"""
    Policies for referencing.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"



schema Route53AwsmUpboundIoV1beta1RecordSpecForProviderHealthCheckIDSelector:
    r"""
    Selector for a HealthCheck in route53 to populate healthCheckId.

    Attributes
    ----------
    matchControllerRef : bool, default is Undefined, optional
        MatchControllerRef ensures an object with the same controller reference
        as the selecting object is selected.
    matchLabels : {str:str}, default is Undefined, optional
        MatchLabels ensures an object with matching labels is selected.
    namespace : str, default is Undefined, optional
        Namespace for the selector
    policy : Route53AwsmUpboundIoV1beta1RecordSpecForProviderHealthCheckIDSelectorPolicy, default is Undefined, optional
        policy
    """


    matchControllerRef?: bool

    matchLabels?: {str:str}

    namespace?: str

    policy?: Route53AwsmUpboundIoV1beta1RecordSpecForProviderHealthCheckIDSelectorPolicy



schema Route53AwsmUpboundIoV1beta1RecordSpecForProviderHealthCheckIDSelectorPolicy:
    r"""
    Policies for selection.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"



schema Route53AwsmUpboundIoV1beta1RecordSpecForProviderLatencyRoutingPolicy:
    r"""
    A block indicating a routing policy based on the latency between the requestor and an AWS region. Conflicts with any other routing policy. Documented below.

    Attributes
    ----------
    region : str, default is Undefined, required
        An AWS region from which to measure latency. See http://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-policy.html#routing-policy-latency
    """


    region: str



schema Route53AwsmUpboundIoV1beta1RecordSpecForProviderRecordsRefsItems0:
    r"""
    A NamespacedReference to a named object.

    Attributes
    ----------
    name : str, default is Undefined, required
        Name of the referenced object.
    namespace : str, default is Undefined, optional
        Namespace of the referenced object
    policy : Route53AwsmUpboundIoV1beta1RecordSpecForProviderRecordsRefsItems0Policy, default is Undefined, optional
        policy
    """


    name: str

    namespace?: str

    policy?: Route53AwsmUpboundIoV1beta1RecordSpecForProviderRecordsRefsItems0Policy



schema Route53AwsmUpboundIoV1beta1RecordSpecForProviderRecordsRefsItems0Policy:
    r"""
    Policies for referencing.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"



schema Route53AwsmUpboundIoV1beta1RecordSpecForProviderRecordsSelector:
    r"""
    Selector for a list of EIP in ec2 to populate records.

    Attributes
    ----------
    matchControllerRef : bool, default is Undefined, optional
        MatchControllerRef ensures an object with the same controller reference
        as the selecting object is selected.
    matchLabels : {str:str}, default is Undefined, optional
        MatchLabels ensures an object with matching labels is selected.
    namespace : str, default is Undefined, optional
        Namespace for the selector
    policy : Route53AwsmUpboundIoV1beta1RecordSpecForProviderRecordsSelectorPolicy, default is Undefined, optional
        policy
    """


    matchControllerRef?: bool

    matchLabels?: {str:str}

    namespace?: str

    policy?: Route53AwsmUpboundIoV1beta1RecordSpecForProviderRecordsSelectorPolicy



schema Route53AwsmUpboundIoV1beta1RecordSpecForProviderRecordsSelectorPolicy:
    r"""
    Policies for selection.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"



schema Route53AwsmUpboundIoV1beta1RecordSpecForProviderWeightedRoutingPolicy:
    r"""
    A block indicating a weighted routing policy. Conflicts with any other routing policy. Documented below.

    Attributes
    ----------
    weight : float, default is Undefined, optional
        A numeric value indicating the relative weight of the record. See http://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-policy.html#routing-policy-weighted.
    """


    weight?: float



schema Route53AwsmUpboundIoV1beta1RecordSpecForProviderZoneIDRef:
    r"""
    Reference to a Zone in route53 to populate zoneId.

    Attributes
    ----------
    name : str, default is Undefined, required
        Name of the referenced object.
    namespace : str, default is Undefined, optional
        Namespace of the referenced object
    policy : Route53AwsmUpboundIoV1beta1RecordSpecForProviderZoneIDRefPolicy, default is Undefined, optional
        policy
    """


    name: str

    namespace?: str

    policy?: Route53AwsmUpboundIoV1beta1RecordSpecForProviderZoneIDRefPolicy



schema Route53AwsmUpboundIoV1beta1RecordSpecForProviderZoneIDRefPolicy:
    r"""
    Policies for referencing.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"



schema Route53AwsmUpboundIoV1beta1RecordSpecForProviderZoneIDSelector:
    r"""
    Selector for a Zone in route53 to populate zoneId.

    Attributes
    ----------
    matchControllerRef : bool, default is Undefined, optional
        MatchControllerRef ensures an object with the same controller reference
        as the selecting object is selected.
    matchLabels : {str:str}, default is Undefined, optional
        MatchLabels ensures an object with matching labels is selected.
    namespace : str, default is Undefined, optional
        Namespace for the selector
    policy : Route53AwsmUpboundIoV1beta1RecordSpecForProviderZoneIDSelectorPolicy, default is Undefined, optional
        policy
    """


    matchControllerRef?: bool

    matchLabels?: {str:str}

    namespace?: str

    policy?: Route53AwsmUpboundIoV1beta1RecordSpecForProviderZoneIDSelectorPolicy



schema Route53AwsmUpboundIoV1beta1RecordSpecForProviderZoneIDSelectorPolicy:
    r"""
    Policies for selection.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"


schema S3AwsmUpboundIoV1beta1BucketSpecForProvider:
    r"""
    s3 awsm upbound io v1beta1 bucket spec for provider

    Attributes
    ----------
    bucketNamespace : str, default is Undefined, optional
        Namespace for the bucket. Determines bucket naming scope. Valid values: account-regional, global. Defaults to global (AWS).
    forceDestroy : bool, default is Undefined, optional
        Boolean that indicates all objects (including any locked objects) should be deleted from the bucket when the bucket is destroyed so that the bucket can be destroyed without error. These objects are not recoverable. This only deletes objects when the bucket is destroyed, not when setting this parameter to true. If setting this field in the same operation that would require replacing the bucket or destroying the bucket, this flag will not work.
    objectLockEnabled : bool, default is Undefined, optional
        Whether this bucket has an Object Lock configuration enabled. Valid values are true or false. This argument is not supported in all regions or partitions.
    region : str, default is Undefined, required
        Region where this resource will be managed. Defaults to the Region set in the provider configuration.
        Region is the region you'd like your resource to be created in.
    tags : {str:str}, default is Undefined, optional
        Key-value map of resource tags.
    """


    bucketNamespace?: str

    forceDestroy?: bool

    objectLockEnabled?: bool

    region: str

    tags?: {str:str}


schema S3AwsmUpboundIoV1beta1BucketPolicySpecForProvider:
    r"""
    s3 awsm upbound io v1beta1 bucket policy spec for provider

    Attributes
    ----------
    bucket : str, default is Undefined, optional
        Name of the bucket to which to apply the policy.
    bucketRef : S3AwsmUpboundIoV1beta1BucketPolicySpecForProviderBucketRef, default is Undefined, optional
        bucket ref
    bucketSelector : S3AwsmUpboundIoV1beta1BucketPolicySpecForProviderBucketSelector, default is Undefined, optional
        bucket selector
    policy : str, default is Undefined, optional
        Text of the policy. Although this is a bucket policy rather than an IAM policy, the aws_iam_policy_document data source may be used, so long as it specifies a principal. Note: Bucket policies are limited to 20 KB in size.
    region : str, default is Undefined, required
        Region where this resource will be managed. Defaults to the Region set in the provider configuration.
        Region is the region you'd like your resource to be created in.
    """


    bucket?: str

    bucketRef?: S3AwsmUpboundIoV1beta1BucketPolicySpecForProviderBucketRef

    bucketSelector?: S3AwsmUpboundIoV1beta1BucketPolicySpecForProviderBucketSelector

    policy?: str

    region: str



schema S3AwsmUpboundIoV1beta1BucketPolicySpecForProviderBucketRef:
    r"""
    Reference to a Bucket in s3 to populate bucket.

    Attributes
    ----------
    name : str, default is Undefined, required
        Name of the referenced object.
    namespace : str, default is Undefined, optional
        Namespace of the referenced object
    policy : S3AwsmUpboundIoV1beta1BucketPolicySpecForProviderBucketRefPolicy, default is Undefined, optional
        policy
    """


    name: str

    namespace?: str

    policy?: S3AwsmUpboundIoV1beta1BucketPolicySpecForProviderBucketRefPolicy



schema S3AwsmUpboundIoV1beta1BucketPolicySpecForProviderBucketRefPolicy:
    r"""
    Policies for referencing.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"



schema S3AwsmUpboundIoV1beta1BucketPolicySpecForProviderBucketSelector:
    r"""
    Selector for a Bucket in s3 to populate bucket.

    Attributes
    ----------
    matchControllerRef : bool, default is Undefined, optional
        MatchControllerRef ensures an object with the same controller reference
        as the selecting object is selected.
    matchLabels : {str:str}, default is Undefined, optional
        MatchLabels ensures an object with matching labels is selected.
    namespace : str, default is Undefined, optional
        Namespace for the selector
    policy : S3AwsmUpboundIoV1beta1BucketPolicySpecForProviderBucketSelectorPolicy, default is Undefined, optional
        policy
    """


    matchControllerRef?: bool

    matchLabels?: {str:str}

    namespace?: str

    policy?: S3AwsmUpboundIoV1beta1BucketPolicySpecForProviderBucketSelectorPolicy



schema S3AwsmUpboundIoV1beta1BucketPolicySpecForProviderBucketSelectorPolicy:
    r"""
    Policies for selection.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"


schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProvider:
    r"""
    cloudfront awsm upbound io v1beta1 distribution spec for provider

    Attributes
    ----------
    aliases : [str], default is Undefined, optional
        Extra CNAMEs (alternate domain names), if any, for this distribution.
    anycastIpListId : str, default is Undefined, optional
        ID of the Anycast static IP list that is associated with the distribution.
    cacheTagConfig : CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderCacheTagConfig, default is Undefined, optional
        cache tag config
    comment : str, default is Undefined, optional
        Any comments you want to include about the distribution.
    connectionFunctionAssociation : CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderConnectionFunctionAssociation, default is Undefined, optional
        connection function association
    continuousDeploymentPolicyId : str, default is Undefined, optional
        Identifier of a continuous deployment policy. This argument should only be set on a production distribution. See the aws_cloudfront_continuous_deployment_policy resource for additional details.
    customErrorResponse : [CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderCustomErrorResponseItems0], default is Undefined, optional
        One or more custom error response elements (multiples allowed).
    defaultCacheBehavior : CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderDefaultCacheBehavior, default is Undefined, optional
        default cache behavior
    defaultRootObject : str, default is Undefined, optional
        Object that you want CloudFront to return (for example, index.html) when an end user requests the root URL.
    enabled : bool, default is Undefined, optional
        Whether the distribution is enabled to accept end user requests for content.
    httpVersion : str, default is Undefined, optional
        Maximum HTTP version to support on the distribution. Allowed values are http1.1, http2, http2and3 and http3. The default is http2.
    isIpv6Enabled : bool, default is Undefined, optional
        Whether the IPv6 is enabled for the distribution.
    loggingConfig : CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderLoggingConfig, default is Undefined, optional
        logging config
    orderedCacheBehavior : [CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0], default is Undefined, optional
        Ordered list of cache behaviors resource for this distribution. List from top to bottom in order of precedence. The topmost cache behavior will have precedence 0.
    origin : [CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0], default is Undefined, optional
        One or more origins for this distribution (multiples allowed).
    originGroup : [CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginGroupItems0], default is Undefined, optional
        One or more origin_group for this distribution (multiples allowed).
    priceClass : str, default is Undefined, optional
        Price class for this distribution. One of PriceClass_All, PriceClass_200, PriceClass_100.
    restrictions : CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderRestrictions, default is Undefined, optional
        restrictions
    retainOnDelete : bool, default is Undefined, optional
        If this is set, the distribution needs to be deleted manually afterwards. Default: false.
    staging : bool, default is Undefined, optional
        A Boolean that indicates whether this is a staging distribution. Defaults to false.
    tags : {str:str}, default is Undefined, optional
        Key-value map of resource tags.
    viewerCertificate : CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderViewerCertificate, default is Undefined, optional
        viewer certificate
    viewerMtlsConfig : CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderViewerMtlsConfig, default is Undefined, optional
        viewer mtls config
    waitForDeployment : bool, default is Undefined, optional
        If enabled, the resource will wait for the distribution status to change from InProgress to Deployed. Setting this tofalse will skip the process. Default: true.
    webAclId : str, default is Undefined, optional
        Unique identifier that specifies the AWS WAF web ACL, if any, to associate with this distribution. To specify a web ACL created using the latest version of AWS WAF (WAFv2), use the ACL ARN, for example aws_wafv2_web_acl.example.arn. To specify a web ACL created using AWS WAF Classic, use the ACL ID, for example aws_waf_web_acl.example.id. The WAF Web ACL must exist in the WAF Global (CloudFront) region and the credentials configuring this argument must have waf:GetWebACL permissions assigned.
    """


    aliases?: [str]

    anycastIpListId?: str

    cacheTagConfig?: CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderCacheTagConfig

    comment?: str

    connectionFunctionAssociation?: CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderConnectionFunctionAssociation

    continuousDeploymentPolicyId?: str

    customErrorResponse?: [CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderCustomErrorResponseItems0]

    defaultCacheBehavior?: CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderDefaultCacheBehavior

    defaultRootObject?: str

    enabled?: bool

    httpVersion?: str

    isIpv6Enabled?: bool

    loggingConfig?: CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderLoggingConfig

    orderedCacheBehavior?: [CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0]

    origin?: [CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0]

    originGroup?: [CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginGroupItems0]

    priceClass?: str

    restrictions?: CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderRestrictions

    retainOnDelete?: bool

    staging?: bool

    tags?: {str:str}

    viewerCertificate?: CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderViewerCertificate

    viewerMtlsConfig?: CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderViewerMtlsConfig

    waitForDeployment?: bool

    webAclId?: str



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderCacheTagConfig:
    r"""
    Cache tag configuration block for cache tag extraction from origin responses (maximum one). See the AWS documentation for more information about cache tags.

    Attributes
    ----------
    headerName : str, default is Undefined, optional
        Name of the HTTP header to extract cache tags. The header value must contain comma-separated tag values.
    """


    headerName?: str



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderConnectionFunctionAssociation:
    r"""
    A connection function association configuration block (maximum one).

    Attributes
    ----------
    id : str, default is Undefined, optional
        Identifier of the connection function to associate with the distribution.
    """


    id?: str



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderCustomErrorResponseItems0:
    r"""
    cloudfront awsm upbound io v1beta1 distribution spec for provider custom error response items0

    Attributes
    ----------
    errorCachingMinTtl : float, default is Undefined, optional
        Minimum amount of time you want HTTP error codes to stay in CloudFront caches before CloudFront queries your origin to see whether the object has been updated.
    errorCode : float, default is Undefined, optional
        4xx or 5xx HTTP status code that you want to customize.
    responseCode : float, default is Undefined, optional
        HTTP status code that you want CloudFront to return with the custom error page to the viewer.
    responsePagePath : str, default is Undefined, optional
        Path of the custom error page (for example, /custom_404.html).
    """


    errorCachingMinTtl?: float

    errorCode?: float

    responseCode?: float

    responsePagePath?: str



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderDefaultCacheBehavior:
    r"""
    Default cache behavior for this distribution (maximum one). Requires either cache_policy_id (preferred) or forwarded_values (deprecated) be set.

    Attributes
    ----------
    allowedMethods : [str], default is Undefined, optional
        Controls which HTTP methods CloudFront processes and forwards to your Amazon S3 bucket or your custom origin.
    cachePolicyId : str, default is Undefined, optional
        Unique identifier of the cache policy that is attached to the cache behavior. If configuring the default_cache_behavior either cache_policy_id or forwarded_values must be set.
    cachedMethods : [str], default is Undefined, optional
        Controls whether CloudFront caches the response to requests using the specified HTTP methods.
    compress : bool, default is Undefined, optional
        Whether you want CloudFront to automatically compress content for web requests that include Accept-Encoding: gzip in the request header (default: false).
    defaultTtl : float, default is Undefined, optional
        Default amount of time (in seconds) that an object is in a CloudFront cache before CloudFront forwards another request in the absence of an Cache-Control max-age or Expires header. The TTL defined in Cache Policy overrides this configuration.
    fieldLevelEncryptionId : str, default is Undefined, optional
        Field level encryption configuration ID.
    forwardedValues : CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderDefaultCacheBehaviorForwardedValues, default is Undefined, optional
        forwarded values
    functionAssociation : [CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderDefaultCacheBehaviorFunctionAssociationItems0], default is Undefined, optional
        A config block that triggers a cloudfront function with specific actions (maximum 2).
    grpcConfig : CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderDefaultCacheBehaviorGrpcConfig, default is Undefined, optional
        grpc config
    lambdaFunctionAssociation : [CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderDefaultCacheBehaviorLambdaFunctionAssociationItems0], default is Undefined, optional
        A config block that triggers a lambda function with specific actions (maximum 4).
    maxTtl : float, default is Undefined, optional
        Maximum amount of time (in seconds) that an object is in a CloudFront cache before CloudFront forwards another request to your origin to determine whether the object has been updated. Only effective in the presence of Cache-Control max-age, Cache-Control s-maxage, and Expires headers. The TTL defined in Cache Policy overrides this configuration.
    minTtl : float, default is Undefined, optional
        Minimum amount of time that you want objects to stay in CloudFront caches before CloudFront queries your origin to see whether the object has been updated. Defaults to 0 seconds. The TTL defined in Cache Policy overrides this configuration.
    originRequestPolicyId : str, default is Undefined, optional
        Unique identifier of the origin request policy that is attached to the behavior.
    realtimeLogConfigArn : str, default is Undefined, optional
        ARN of the real-time log configuration that is attached to this cache behavior.
    responseHeadersPolicyId : str, default is Undefined, optional
        Identifier for a response headers policy.
    smoothStreaming : bool, default is Undefined, optional
        Indicates whether you want to distribute media files in Microsoft Smooth Streaming format using the origin that is associated with this cache behavior.
    targetOriginId : str, default is Undefined, optional
        Value of ID for the origin that you want CloudFront to route requests to when a request matches the path pattern either for a cache behavior or for the default cache behavior.
    trustedKeyGroups : [str], default is Undefined, optional
        List of key group IDs that CloudFront can use to validate signed URLs or signed cookies. See the CloudFront User Guide for more information about this feature.
    trustedSigners : [str], default is Undefined, optional
        List of AWS account IDs (or self) that you want to allow to create signed URLs for private content. See the CloudFront User Guide for more information about this feature.
    viewerProtocolPolicy : str, default is Undefined, optional
        Use this element to specify the protocol that users can use to access the files in the origin specified by TargetOriginId when a request matches the path pattern in PathPattern. One of allow-all, https-only, or redirect-to-https.
    """


    allowedMethods?: [str]

    cachePolicyId?: str

    cachedMethods?: [str]

    compress?: bool

    defaultTtl?: float

    fieldLevelEncryptionId?: str

    forwardedValues?: CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderDefaultCacheBehaviorForwardedValues

    functionAssociation?: [CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderDefaultCacheBehaviorFunctionAssociationItems0]

    grpcConfig?: CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderDefaultCacheBehaviorGrpcConfig

    lambdaFunctionAssociation?: [CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderDefaultCacheBehaviorLambdaFunctionAssociationItems0]

    maxTtl?: float

    minTtl?: float

    originRequestPolicyId?: str

    realtimeLogConfigArn?: str

    responseHeadersPolicyId?: str

    smoothStreaming?: bool

    targetOriginId?: str

    trustedKeyGroups?: [str]

    trustedSigners?: [str]

    viewerProtocolPolicy?: str



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderDefaultCacheBehaviorForwardedValues:
    r"""
    The forwarded values configuration that specifies how CloudFront handles query strings, cookies and headers (maximum one).

    Attributes
    ----------
    cookies : CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderDefaultCacheBehaviorForwardedValuesCookies, default is Undefined, optional
        cookies
    headers : [str], default is Undefined, optional
        Headers, if any, that you want CloudFront to vary upon for this cache behavior. Specify * to include all headers.
    queryString : bool, default is Undefined, optional
        Indicates whether you want CloudFront to forward query strings to the origin that is associated with this cache behavior.
    queryStringCacheKeys : [str], default is Undefined, optional
        When specified, along with a value of true for query_string, all query strings are forwarded, however only the query string keys listed in this argument are cached. When omitted with a value of true for query_string, all query string keys are cached.
    """


    cookies?: CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderDefaultCacheBehaviorForwardedValuesCookies

    headers?: [str]

    queryString?: bool

    queryStringCacheKeys?: [str]



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderDefaultCacheBehaviorForwardedValuesCookies:
    r"""
    The forwarded values cookies that specifies how CloudFront handles cookies (maximum one).

    Attributes
    ----------
    forward : str, default is Undefined, optional
        Whether you want CloudFront to forward cookies to the origin that is associated with this cache behavior. You can specify all, none or whitelist. If whitelist, you must include the subsequent whitelisted_names.
    whitelistedNames : [str], default is Undefined, optional
        If you have specified whitelist to forward, the whitelisted cookies that you want CloudFront to forward to your origin.
    """


    forward?: str

    whitelistedNames?: [str]



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderDefaultCacheBehaviorFunctionAssociationItems0:
    r"""
    cloudfront awsm upbound io v1beta1 distribution spec for provider default cache behavior function association items0

    Attributes
    ----------
    eventType : str, default is Undefined, optional
        Specific event to trigger this function. Valid values: viewer-request, origin-request, viewer-response, origin-response.
    functionArn : str, default is Undefined, optional
        ARN of the CloudFront function.
    """


    eventType?: str

    functionArn?: str



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderDefaultCacheBehaviorGrpcConfig:
    r"""
    A config block that sets the grpc config.

    Attributes
    ----------
    enabled : bool, default is Undefined, optional
        Whether the distribution is enabled to accept end user requests for content.
    """


    enabled?: bool



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderDefaultCacheBehaviorLambdaFunctionAssociationItems0:
    r"""
    cloudfront awsm upbound io v1beta1 distribution spec for provider default cache behavior lambda function association items0

    Attributes
    ----------
    eventType : str, default is Undefined, optional
        Specific event to trigger this function. Valid values: viewer-request, origin-request, viewer-response, origin-response.
    includeBody : bool, default is Undefined, optional
        When set to true it exposes the request body to the lambda function. Defaults to false. Valid values: true, false.
    lambdaArn : str, default is Undefined, optional
        ARN of the Lambda function.
    """


    eventType?: str

    includeBody?: bool

    lambdaArn?: str



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderLoggingConfig:
    r"""
    The logging configuration that controls how logs are written to your distribution (maximum one). AWS provides two versions of access logs for CloudFront: Legacy and v2. This argument configures legacy version standard logs.

    Attributes
    ----------
    bucket : str, default is Undefined, optional
        Amazon S3 bucket for V1 logging where access logs are stored, for example, myawslogbucket.s3.amazonaws.com. V1 logging is enabled when this argument is specified. The bucket must have correct ACL attached with "FULL_CONTROL" permission for "awslogsdelivery" account (Canonical ID: "c4c1ede66af53448b93c283ce9448c4ba468c9432aa01d700d3878632f77d2d0") for log transfer to work.
    includeCookies : bool, default is Undefined, optional
        Whether to include cookies in access logs (default: false). This argument applies to both V1 and V2 logging.
    prefix : str, default is Undefined, optional
        Prefix added to the access log file names for V1 logging, for example, myprefix/. This argument is effective only when V1 logging is enabled.
    """


    bucket?: str

    includeCookies?: bool

    prefix?: str



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0:
    r"""
    cloudfront awsm upbound io v1beta1 distribution spec for provider ordered cache behavior items0

    Attributes
    ----------
    allowedMethods : [str], default is Undefined, optional
        Controls which HTTP methods CloudFront processes and forwards to your Amazon S3 bucket or your custom origin.
    cachePolicyId : str, default is Undefined, optional
        Unique identifier of the cache policy that is attached to the cache behavior. If configuring the default_cache_behavior either cache_policy_id or forwarded_values must be set.
    cachedMethods : [str], default is Undefined, optional
        Controls whether CloudFront caches the response to requests using the specified HTTP methods.
    compress : bool, default is Undefined, optional
        Whether you want CloudFront to automatically compress content for web requests that include Accept-Encoding: gzip in the request header (default: false).
    defaultTtl : float, default is Undefined, optional
        Default amount of time (in seconds) that an object is in a CloudFront cache before CloudFront forwards another request in the absence of an Cache-Control max-age or Expires header. The TTL defined in Cache Policy overrides this configuration.
    fieldLevelEncryptionId : str, default is Undefined, optional
        Field level encryption configuration ID.
    forwardedValues : CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0ForwardedValues, default is Undefined, optional
        forwarded values
    functionAssociation : [CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0FunctionAssociationItems0], default is Undefined, optional
        A config block that triggers a cloudfront function with specific actions (maximum 2).
    grpcConfig : CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0GrpcConfig, default is Undefined, optional
        grpc config
    lambdaFunctionAssociation : [CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0LambdaFunctionAssociationItems0], default is Undefined, optional
        A config block that triggers a lambda function with specific actions (maximum 4).
    maxTtl : float, default is Undefined, optional
        Maximum amount of time (in seconds) that an object is in a CloudFront cache before CloudFront forwards another request to your origin to determine whether the object has been updated. Only effective in the presence of Cache-Control max-age, Cache-Control s-maxage, and Expires headers. The TTL defined in Cache Policy overrides this configuration.
    minTtl : float, default is Undefined, optional
        Minimum amount of time that you want objects to stay in CloudFront caches before CloudFront queries your origin to see whether the object has been updated. Defaults to 0 seconds. The TTL defined in Cache Policy overrides this configuration.
    originRequestPolicyId : str, default is Undefined, optional
        Unique identifier of the origin request policy that is attached to the behavior.
    pathPattern : str, default is Undefined, optional
        Pattern (for example, images/*.jpg) that specifies which requests you want this cache behavior to apply to.
    realtimeLogConfigArn : str, default is Undefined, optional
        ARN of the real-time log configuration that is attached to this cache behavior.
    responseHeadersPolicyId : str, default is Undefined, optional
        Identifier for a response headers policy.
    smoothStreaming : bool, default is Undefined, optional
        Indicates whether you want to distribute media files in Microsoft Smooth Streaming format using the origin that is associated with this cache behavior.
    targetOriginId : str, default is Undefined, optional
        Value of ID for the origin that you want CloudFront to route requests to when a request matches the path pattern either for a cache behavior or for the default cache behavior.
    trustedKeyGroups : [str], default is Undefined, optional
        List of key group IDs that CloudFront can use to validate signed URLs or signed cookies. See the CloudFront User Guide for more information about this feature.
    trustedSigners : [str], default is Undefined, optional
        List of AWS account IDs (or self) that you want to allow to create signed URLs for private content. See the CloudFront User Guide for more information about this feature.
    viewerProtocolPolicy : str, default is Undefined, optional
        Use this element to specify the protocol that users can use to access the files in the origin specified by TargetOriginId when a request matches the path pattern in PathPattern. One of allow-all, https-only, or redirect-to-https.
    """


    allowedMethods?: [str]

    cachePolicyId?: str

    cachedMethods?: [str]

    compress?: bool

    defaultTtl?: float

    fieldLevelEncryptionId?: str

    forwardedValues?: CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0ForwardedValues

    functionAssociation?: [CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0FunctionAssociationItems0]

    grpcConfig?: CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0GrpcConfig

    lambdaFunctionAssociation?: [CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0LambdaFunctionAssociationItems0]

    maxTtl?: float

    minTtl?: float

    originRequestPolicyId?: str

    pathPattern?: str

    realtimeLogConfigArn?: str

    responseHeadersPolicyId?: str

    smoothStreaming?: bool

    targetOriginId?: str

    trustedKeyGroups?: [str]

    trustedSigners?: [str]

    viewerProtocolPolicy?: str



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0ForwardedValues:
    r"""
    The forwarded values configuration that specifies how CloudFront handles query strings, cookies and headers (maximum one).

    Attributes
    ----------
    cookies : CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0ForwardedValuesCookies, default is Undefined, optional
        cookies
    headers : [str], default is Undefined, optional
        Headers, if any, that you want CloudFront to vary upon for this cache behavior. Specify * to include all headers.
    queryString : bool, default is Undefined, optional
        Indicates whether you want CloudFront to forward query strings to the origin that is associated with this cache behavior.
    queryStringCacheKeys : [str], default is Undefined, optional
        When specified, along with a value of true for query_string, all query strings are forwarded, however only the query string keys listed in this argument are cached. When omitted with a value of true for query_string, all query string keys are cached.
    """


    cookies?: CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0ForwardedValuesCookies

    headers?: [str]

    queryString?: bool

    queryStringCacheKeys?: [str]



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0ForwardedValuesCookies:
    r"""
    The forwarded values cookies that specifies how CloudFront handles cookies (maximum one).

    Attributes
    ----------
    forward : str, default is Undefined, optional
        Whether you want CloudFront to forward cookies to the origin that is associated with this cache behavior. You can specify all, none or whitelist. If whitelist, you must include the subsequent whitelisted_names.
    whitelistedNames : [str], default is Undefined, optional
        If you have specified whitelist to forward, the whitelisted cookies that you want CloudFront to forward to your origin.
    """


    forward?: str

    whitelistedNames?: [str]



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0FunctionAssociationItems0:
    r"""
    cloudfront awsm upbound io v1beta1 distribution spec for provider ordered cache behavior items0 function association items0

    Attributes
    ----------
    eventType : str, default is Undefined, optional
        Specific event to trigger this function. Valid values: viewer-request, origin-request, viewer-response, origin-response.
    functionArn : str, default is Undefined, optional
        ARN of the CloudFront function.
    functionArnRef : CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0FunctionAssociationItems0FunctionArnRef, default is Undefined, optional
        function arn ref
    functionArnSelector : CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0FunctionAssociationItems0FunctionArnSelector, default is Undefined, optional
        function arn selector
    """


    eventType?: str

    functionArn?: str

    functionArnRef?: CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0FunctionAssociationItems0FunctionArnRef

    functionArnSelector?: CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0FunctionAssociationItems0FunctionArnSelector



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0FunctionAssociationItems0FunctionArnRef:
    r"""
    Reference to a Function in cloudfront to populate functionArn.

    Attributes
    ----------
    name : str, default is Undefined, required
        Name of the referenced object.
    namespace : str, default is Undefined, optional
        Namespace of the referenced object
    policy : CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0FunctionAssociationItems0FunctionArnRefPolicy, default is Undefined, optional
        policy
    """


    name: str

    namespace?: str

    policy?: CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0FunctionAssociationItems0FunctionArnRefPolicy



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0FunctionAssociationItems0FunctionArnRefPolicy:
    r"""
    Policies for referencing.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0FunctionAssociationItems0FunctionArnSelector:
    r"""
    Selector for a Function in cloudfront to populate functionArn.

    Attributes
    ----------
    matchControllerRef : bool, default is Undefined, optional
        MatchControllerRef ensures an object with the same controller reference
        as the selecting object is selected.
    matchLabels : {str:str}, default is Undefined, optional
        MatchLabels ensures an object with matching labels is selected.
    namespace : str, default is Undefined, optional
        Namespace for the selector
    policy : CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0FunctionAssociationItems0FunctionArnSelectorPolicy, default is Undefined, optional
        policy
    """


    matchControllerRef?: bool

    matchLabels?: {str:str}

    namespace?: str

    policy?: CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0FunctionAssociationItems0FunctionArnSelectorPolicy



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0FunctionAssociationItems0FunctionArnSelectorPolicy:
    r"""
    Policies for selection.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0GrpcConfig:
    r"""
    A config block that sets the grpc config.

    Attributes
    ----------
    enabled : bool, default is Undefined, optional
        Whether the distribution is enabled to accept end user requests for content.
    """


    enabled?: bool



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0LambdaFunctionAssociationItems0:
    r"""
    cloudfront awsm upbound io v1beta1 distribution spec for provider ordered cache behavior items0 lambda function association items0

    Attributes
    ----------
    eventType : str, default is Undefined, optional
        Specific event to trigger this function. Valid values: viewer-request, origin-request, viewer-response, origin-response.
    includeBody : bool, default is Undefined, optional
        When set to true it exposes the request body to the lambda function. Defaults to false. Valid values: true, false.
    lambdaArn : str, default is Undefined, optional
        ARN of the Lambda function.
    lambdaArnRef : CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0LambdaFunctionAssociationItems0LambdaArnRef, default is Undefined, optional
        lambda arn ref
    lambdaArnSelector : CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0LambdaFunctionAssociationItems0LambdaArnSelector, default is Undefined, optional
        lambda arn selector
    """


    eventType?: str

    includeBody?: bool

    lambdaArn?: str

    lambdaArnRef?: CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0LambdaFunctionAssociationItems0LambdaArnRef

    lambdaArnSelector?: CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0LambdaFunctionAssociationItems0LambdaArnSelector



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0LambdaFunctionAssociationItems0LambdaArnRef:
    r"""
    Reference to a Function in lambda to populate lambdaArn.

    Attributes
    ----------
    name : str, default is Undefined, required
        Name of the referenced object.
    namespace : str, default is Undefined, optional
        Namespace of the referenced object
    policy : CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0LambdaFunctionAssociationItems0LambdaArnRefPolicy, default is Undefined, optional
        policy
    """


    name: str

    namespace?: str

    policy?: CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0LambdaFunctionAssociationItems0LambdaArnRefPolicy



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0LambdaFunctionAssociationItems0LambdaArnRefPolicy:
    r"""
    Policies for referencing.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0LambdaFunctionAssociationItems0LambdaArnSelector:
    r"""
    Selector for a Function in lambda to populate lambdaArn.

    Attributes
    ----------
    matchControllerRef : bool, default is Undefined, optional
        MatchControllerRef ensures an object with the same controller reference
        as the selecting object is selected.
    matchLabels : {str:str}, default is Undefined, optional
        MatchLabels ensures an object with matching labels is selected.
    namespace : str, default is Undefined, optional
        Namespace for the selector
    policy : CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0LambdaFunctionAssociationItems0LambdaArnSelectorPolicy, default is Undefined, optional
        policy
    """


    matchControllerRef?: bool

    matchLabels?: {str:str}

    namespace?: str

    policy?: CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0LambdaFunctionAssociationItems0LambdaArnSelectorPolicy



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOrderedCacheBehaviorItems0LambdaFunctionAssociationItems0LambdaArnSelectorPolicy:
    r"""
    Policies for selection.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginGroupItems0:
    r"""
    cloudfront awsm upbound io v1beta1 distribution spec for provider origin group items0

    Attributes
    ----------
    failoverCriteria : CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginGroupItems0FailoverCriteria, default is Undefined, optional
        failover criteria
    member : [CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginGroupItems0MemberItems0], default is Undefined, optional
        Ordered member configuration blocks assigned to the origin group, where the first member is the primary origin. You must specify two members.
    originId : str, default is Undefined, optional
        Unique identifier for the origin.
    """


    failoverCriteria?: CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginGroupItems0FailoverCriteria

    member?: [CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginGroupItems0MemberItems0]

    originId?: str



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginGroupItems0FailoverCriteria:
    r"""
    The failover criteria for when to failover to the secondary origin.

    Attributes
    ----------
    statusCodes : [float], default is Undefined, optional
        List of HTTP status codes for the origin group.
    """


    statusCodes?: [float]



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginGroupItems0MemberItems0:
    r"""
    cloudfront awsm upbound io v1beta1 distribution spec for provider origin group items0 member items0

    Attributes
    ----------
    originId : str, default is Undefined, optional
        Unique identifier for the origin.
    """


    originId?: str



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0:
    r"""
    cloudfront awsm upbound io v1beta1 distribution spec for provider origin items0

    Attributes
    ----------
    connectionAttempts : float, default is Undefined, optional
        Number of times that CloudFront attempts to connect to the origin. Must be between 1-3. Defaults to 3.
    connectionTimeout : float, default is Undefined, optional
        Number of seconds that CloudFront waits when trying to establish a connection to the origin. Must be between 1-10. Defaults to 10.
    customHeader : [CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0CustomHeaderItems0], default is Undefined, optional
        One or more sub-resources with name and value parameters that specify header data that will be sent to the origin (multiples allowed).
    customOriginConfig : CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0CustomOriginConfig, default is Undefined, optional
        custom origin config
    domainName : str, default is Undefined, optional
        DNS domain name of either the S3 bucket, or web site of your custom origin.
    originAccessControlId : str, default is Undefined, optional
        Unique identifier of a CloudFront origin access control for this origin.
    originAccessControlIdRef : CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0OriginAccessControlIDRef, default is Undefined, optional
        origin access control Id ref
    originAccessControlIdSelector : CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0OriginAccessControlIDSelector, default is Undefined, optional
        origin access control Id selector
    originId : str, default is Undefined, optional
        Unique identifier for the origin.
    originPath : str, default is Undefined, optional
        Optional element that causes CloudFront to request your content from a directory in your Amazon S3 bucket or your custom origin.
    originShield : CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0OriginShield, default is Undefined, optional
        origin shield
    responseCompletionTimeout : float, default is Undefined, optional
        Time (in seconds) that a request from CloudFront to the origin can stay open and wait for a response. Must be integer greater than or equal to the value of origin_read_timeout. If omitted or explicitly set to 0, no maximum value is enforced.
    s3OriginConfig : CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0S3OriginConfig, default is Undefined, optional
        s3 origin config
    vpcOriginConfig : CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0VpcOriginConfig, default is Undefined, optional
        vpc origin config
    """


    connectionAttempts?: float

    connectionTimeout?: float

    customHeader?: [CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0CustomHeaderItems0]

    customOriginConfig?: CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0CustomOriginConfig

    domainName?: str

    originAccessControlId?: str

    originAccessControlIdRef?: CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0OriginAccessControlIDRef

    originAccessControlIdSelector?: CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0OriginAccessControlIDSelector

    originId?: str

    originPath?: str

    originShield?: CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0OriginShield

    responseCompletionTimeout?: float

    s3OriginConfig?: CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0S3OriginConfig

    vpcOriginConfig?: CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0VpcOriginConfig



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0CustomHeaderItems0:
    r"""
    cloudfront awsm upbound io v1beta1 distribution spec for provider origin items0 custom header items0

    Attributes
    ----------
    name : str, default is Undefined, optional
        name
    value : str, default is Undefined, optional
        value
    """


    name?: str

    value?: str



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0CustomOriginConfig:
    r"""
    The CloudFront custom origin configuration information. If an S3 origin is required, use origin_access_control_id or s3_origin_config instead.

    Attributes
    ----------
    httpPort : float, default is Undefined, optional
        HTTP port the custom origin listens on.
    httpsPort : float, default is Undefined, optional
        HTTPS port the custom origin listens on.
    ipAddressType : str, default is Undefined, optional
        IP protocol CloudFront uses when connecting to your origin. Valid values: ipv4, ipv6, dualstack.
    originKeepaliveTimeout : float, default is Undefined, optional
        The Custom KeepAlive timeout, in seconds. By default, AWS enforces an upper limit of 60. But you can request an increase. Defaults to 5.
    originMtlsConfig : CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0CustomOriginConfigOriginMtlsConfig, default is Undefined, optional
        origin mtls config
    originProtocolPolicy : str, default is Undefined, optional
        Origin protocol policy to apply to your origin. One of http-only, https-only, or match-viewer.
    originReadTimeout : float, default is Undefined, optional
        The Custom Read timeout, in seconds. By default, AWS enforces an upper limit of 60. But you can request an increase. Defaults to 30.
    originSslProtocols : [str], default is Undefined, optional
        List of SSL/TLS protocols that CloudFront can use when connecting to your origin over HTTPS. Valid values: SSLv3, TLSv1, TLSv1.1, TLSv1.2. For more information, see Minimum Origin SSL Protocol in the Amazon CloudFront Developer Guide.
    """


    httpPort?: float

    httpsPort?: float

    ipAddressType?: str

    originKeepaliveTimeout?: float

    originMtlsConfig?: CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0CustomOriginConfigOriginMtlsConfig

    originProtocolPolicy?: str

    originReadTimeout?: float

    originSslProtocols?: [str]



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0CustomOriginConfigOriginMtlsConfig:
    r"""
    The origin mTLS configuration for mutual TLS authentication between CloudFront and your origin.

    Attributes
    ----------
    clientCertificateArn : str, default is Undefined, optional
        ARN of the ACM certificate to use for mutual TLS authentication with the origin. The certificate must have Extended Key Usage set to TLS Client Authentication.
    """


    clientCertificateArn?: str



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0OriginAccessControlIDRef:
    r"""
    Reference to a OriginAccessControl in cloudfront to populate originAccessControlId.

    Attributes
    ----------
    name : str, default is Undefined, required
        Name of the referenced object.
    namespace : str, default is Undefined, optional
        Namespace of the referenced object
    policy : CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0OriginAccessControlIDRefPolicy, default is Undefined, optional
        policy
    """


    name: str

    namespace?: str

    policy?: CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0OriginAccessControlIDRefPolicy



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0OriginAccessControlIDRefPolicy:
    r"""
    Policies for referencing.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0OriginAccessControlIDSelector:
    r"""
    Selector for a OriginAccessControl in cloudfront to populate originAccessControlId.

    Attributes
    ----------
    matchControllerRef : bool, default is Undefined, optional
        MatchControllerRef ensures an object with the same controller reference
        as the selecting object is selected.
    matchLabels : {str:str}, default is Undefined, optional
        MatchLabels ensures an object with matching labels is selected.
    namespace : str, default is Undefined, optional
        Namespace for the selector
    policy : CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0OriginAccessControlIDSelectorPolicy, default is Undefined, optional
        policy
    """


    matchControllerRef?: bool

    matchLabels?: {str:str}

    namespace?: str

    policy?: CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0OriginAccessControlIDSelectorPolicy



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0OriginAccessControlIDSelectorPolicy:
    r"""
    Policies for selection.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0OriginShield:
    r"""
    CloudFront Origin Shield configuration information. Using Origin Shield can help reduce the load on your origin. For more information, see Using Origin Shield in the Amazon CloudFront Developer Guide.

    Attributes
    ----------
    enabled : bool, default is Undefined, optional
        Whether the distribution is enabled to accept end user requests for content.
    originShieldRegion : str, default is Undefined, optional
        AWS Region for Origin Shield. To specify a region, use the region code, not the region name. For example, specify the US East (Ohio) region as us-east-2.
    """


    enabled?: bool

    originShieldRegion?: str



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0S3OriginConfig:
    r"""
    CloudFront S3 origin configuration information. If a custom origin is required, use custom_origin_config instead.

    Attributes
    ----------
    originAccessIdentity : str, default is Undefined, optional
        The CloudFront origin access identity to associate with the origin.
    originAccessIdentityRef : CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0S3OriginConfigOriginAccessIdentityRef, default is Undefined, optional
        origin access identity ref
    originAccessIdentitySelector : CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0S3OriginConfigOriginAccessIdentitySelector, default is Undefined, optional
        origin access identity selector
    """


    originAccessIdentity?: str

    originAccessIdentityRef?: CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0S3OriginConfigOriginAccessIdentityRef

    originAccessIdentitySelector?: CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0S3OriginConfigOriginAccessIdentitySelector



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0S3OriginConfigOriginAccessIdentityRef:
    r"""
    Reference to a OriginAccessIdentity in cloudfront to populate originAccessIdentity.

    Attributes
    ----------
    name : str, default is Undefined, required
        Name of the referenced object.
    namespace : str, default is Undefined, optional
        Namespace of the referenced object
    policy : CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0S3OriginConfigOriginAccessIdentityRefPolicy, default is Undefined, optional
        policy
    """


    name: str

    namespace?: str

    policy?: CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0S3OriginConfigOriginAccessIdentityRefPolicy



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0S3OriginConfigOriginAccessIdentityRefPolicy:
    r"""
    Policies for referencing.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0S3OriginConfigOriginAccessIdentitySelector:
    r"""
    Selector for a OriginAccessIdentity in cloudfront to populate originAccessIdentity.

    Attributes
    ----------
    matchControllerRef : bool, default is Undefined, optional
        MatchControllerRef ensures an object with the same controller reference
        as the selecting object is selected.
    matchLabels : {str:str}, default is Undefined, optional
        MatchLabels ensures an object with matching labels is selected.
    namespace : str, default is Undefined, optional
        Namespace for the selector
    policy : CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0S3OriginConfigOriginAccessIdentitySelectorPolicy, default is Undefined, optional
        policy
    """


    matchControllerRef?: bool

    matchLabels?: {str:str}

    namespace?: str

    policy?: CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0S3OriginConfigOriginAccessIdentitySelectorPolicy



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0S3OriginConfigOriginAccessIdentitySelectorPolicy:
    r"""
    Policies for selection.

    Attributes
    ----------
    resolution : str, default is "Required", optional
        Resolution specifies whether resolution of this reference is required.
        The default is 'Required', which means the reconcile will fail if the
        reference cannot be resolved. 'Optional' means this reference will be
        a no-op if it cannot be resolved.
    resolve : str, default is Undefined, optional
        Resolve specifies when this reference should be resolved. The default
        is 'IfNotPresent', which will attempt to resolve the reference only when
        the corresponding field is not present. Use 'Always' to resolve the
        reference on every reconcile.
    """


    resolution?: "Required" | "Optional" = "Required"

    resolve?: "Always" | "IfNotPresent"



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderOriginItems0VpcOriginConfig:
    r"""
    The VPC origin configuration.

    Attributes
    ----------
    originKeepaliveTimeout : float, default is Undefined, optional
        The Custom KeepAlive timeout, in seconds. By default, AWS enforces an upper limit of 60. But you can request an increase. Defaults to 5.
    originReadTimeout : float, default is Undefined, optional
        The Custom Read timeout, in seconds. By default, AWS enforces an upper limit of 60. But you can request an increase. Defaults to 30.
    ownerAccountId : str, default is Undefined, optional
        The AWS account ID that owns the VPC origin. Required when referencing a VPC origin from a different AWS account for cross-account VPC origin access.
    vpcOriginId : str, default is Undefined, optional
        The VPC origin ID.
    """


    originKeepaliveTimeout?: float

    originReadTimeout?: float

    ownerAccountId?: str

    vpcOriginId?: str



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderRestrictions:
    r"""
    The restriction configuration for this distribution (maximum one).

    Attributes
    ----------
    geoRestriction : CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderRestrictionsGeoRestriction, default is Undefined, optional
        geo restriction
    """


    geoRestriction?: CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderRestrictionsGeoRestriction



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderRestrictionsGeoRestriction:
    r"""
    cloudfront awsm upbound io v1beta1 distribution spec for provider restrictions geo restriction

    Attributes
    ----------
    locations : [str], default is Undefined, optional
        ISO 3166-1-alpha-2 codes for which you want CloudFront either to distribute your content (whitelist) or not distribute your content (blacklist). If the type is specified as none an empty array can be used.
    restrictionType : str, default is Undefined, optional
        Method that you want to use to restrict distribution of your content by country: none, whitelist, or blacklist.
    """


    locations?: [str]

    restrictionType?: str



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderViewerCertificate:
    r"""
    The SSL configuration for this distribution (maximum one).

    Attributes
    ----------
    acmCertificateArn : str, default is Undefined, optional
        ARN of the AWS Certificate Manager certificate that you wish to use with this distribution. Specify this, cloudfront_default_certificate, or iam_certificate_id.  The ACM certificate must be in  US-EAST-1.
    cloudfrontDefaultCertificate : bool, default is Undefined, optional
        true if you want viewers to use HTTPS to request your objects and you're using the CloudFront domain name for your distribution. Specify this, acm_certificate_arn, or iam_certificate_id.
    iamCertificateId : str, default is Undefined, optional
        IAM certificate identifier of the custom viewer certificate for this distribution if you are using a custom domain. Specify this, acm_certificate_arn, or cloudfront_default_certificate.
    minimumProtocolVersion : str, default is Undefined, optional
        Minimum version of the SSL protocol that you want CloudFront to use for HTTPS connections. Can only be set if cloudfront_default_certificate = false. See all possible values in this table under "Security policy." Some examples include: TLSv1.2_2019 and TLSv1.2_2021. Default: TLSv1. NOTE: If you are using a custom certificate (specified with acm_certificate_arn or iam_certificate_id), and have specified sni-only in ssl_support_method, TLSv1 or later must be specified. If you have specified vip in ssl_support_method, only SSLv3 or TLSv1 can be specified. If you have specified cloudfront_default_certificate, TLSv1 must be specified.
    sslSupportMethod : str, default is Undefined, optional
        How you want CloudFront to serve HTTPS requests. One of vip, sni-only, or static-ip. Required if you specify acm_certificate_arn or iam_certificate_id. NOTE: vip causes CloudFront to use a dedicated IP address and may incur extra charges.
    """


    acmCertificateArn?: str

    cloudfrontDefaultCertificate?: bool

    iamCertificateId?: str

    minimumProtocolVersion?: str

    sslSupportMethod?: str



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderViewerMtlsConfig:
    r"""
    The viewer mTLS configuration for this distribution (maximum one).

    Attributes
    ----------
    mode : str, default is Undefined, optional
        The mode for viewer mTLS. Valid values: required, optional.
    trustStoreConfig : CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderViewerMtlsConfigTrustStoreConfig, default is Undefined, optional
        trust store config
    """


    mode?: str

    trustStoreConfig?: CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderViewerMtlsConfigTrustStoreConfig



schema CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProviderViewerMtlsConfigTrustStoreConfig:
    r"""
    The trust store configuration for viewer mTLS (maximum one).

    Attributes
    ----------
    advertiseTrustStoreCaNames : bool, default is Undefined, optional
        Whether to advertise the trust store CA names to clients. Defaults to false.
    ignoreCertificateExpiry : bool, default is Undefined, optional
        Whether to ignore certificate expiry for viewer mTLS. Defaults to false.
    trustStoreId : str, default is Undefined, optional
        Identifier of the trust store to use for viewer mTLS.
    """


    advertiseTrustStoreCaNames?: bool

    ignoreCertificateExpiry?: bool

    trustStoreId?: str


