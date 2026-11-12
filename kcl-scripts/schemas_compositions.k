schema IAMRoleSpec:
    r"""
    Consumer-facing spec for an IAMRole composite resource: an AWS IAM role
    trusted by a single AWS service principal, with optional managed policy
    attachments.
    """
    roleName: str
    trustedService: str
    managedPolicyArns?: [str]
    description?: str
    tags?: {str:str}
    # Real Crossplane XRs carry runtime-injected metadata (e.g. `crossplane`)
    # alongside the fields below -- keep this schema open so validating
    # `oxr.spec` against it doesn't reject fields we don't declare.
    [str]: any

schema LambdaCode:
    r"""
    Where the function's deployment package lives in S3.
    """
    s3Bucket: str
    s3Key: str

schema LambdaFunctionSpec:
    r"""
    Consumer-facing spec for a LambdaFunction composite resource: an AWS
    Lambda function with an optional public Function URL.
    """
    functionName: str
    region: str
    role: str
    handler: str
    runtime: str
    code: LambdaCode
    memorySize?: int
    timeout?: int
    environmentVariables?: {str:str}
    description?: str
    tags?: {str:str}
    enableFunctionUrl?: bool
    [str]: any

schema DnsValidatedCertificateSpec:
    r"""
    Consumer-facing spec for a DnsValidatedCertificate composite resource: an
    ACM certificate validated via a DNS record in an existing Route53 zone.
    """
    domainName: str
    region: str
    zoneId: str
    subjectAlternativeNames?: [str]
    tags?: {str:str}
    [str]: any

schema StaticWebsiteSpec:
    r"""
    Consumer-facing spec for a StaticWebsite composite resource: an S3
    bucket served over a custom domain through CloudFront, with a
    DNS-validated ACM certificate.
    """
    bucketName: str
    domainName: str
    region: str
    zoneId: str
    tags?: {str:str}
    [str]: any
