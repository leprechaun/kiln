import json

import .schemas_compositions
import .schemas_providers

composeStaticWebsite = lambda oxr, ocds -> [any] {
    spec: schemas_compositions.StaticWebsiteSpec = oxr.spec

    _bucketForProvider: schemas_providers.S3AwsmUpboundIoV1beta1BucketSpecForProvider = {
        region = spec.region
        tags = spec.tags
    }

    _bucket = {
        apiVersion = "s3.aws.m.upbound.io/v1beta1"
        kind = "Bucket"
        metadata.annotations = {
            "crossplane.io/external-name" = spec.bucketName
            "krm.kcl.dev/composition-resource-name" = "bucket"
        }
        spec.forProvider = _bucketForProvider
    }

    _publicReadPolicy = json.encode({
        Version = "2012-10-17"
        Statement = [{
            Effect = "Allow"
            Principal = "*"
            Action = "s3:GetObject"
            Resource = "arn:aws:s3:::${spec.bucketName}/*"
        }]
    })

    _bucketPolicyForProvider: schemas_providers.S3AwsmUpboundIoV1beta1BucketPolicySpecForProvider = {
        region = spec.region
        bucket = spec.bucketName
        policy = _publicReadPolicy
    }

    _bucketPolicy = {
        apiVersion = "s3.aws.m.upbound.io/v1beta1"
        kind = "BucketPolicy"
        metadata.annotations = {
            "krm.kcl.dev/composition-resource-name" = "bucket-policy"
        }
        spec.forProvider = _bucketPolicyForProvider
    }

    # CloudFront only accepts ACM certificates issued in us-east-1, regardless
    # of which region the rest of this site's resources live in.
    _certificateSpec: schemas_compositions.DnsValidatedCertificateSpec = {
        domainName = spec.domainName
        region = "us-east-1"
        zoneId = spec.zoneId
    }

    _certificate = {
        apiVersion = "platform.kcl-first.io/v1alpha1"
        kind = "DnsValidatedCertificate"
        metadata.annotations = {
            "krm.kcl.dev/composition-resource-name" = "certificate"
        }
        spec = _certificateSpec
    }

    _certificateArn = ocds["certificate"]?.Resource?.status?.certificateArn

    _distributionForProvider: schemas_providers.CloudfrontAwsmUpboundIoV1beta1DistributionSpecForProvider = {
        enabled = True
        aliases = [spec.domainName]
        origin = [{
            domainName = "${spec.bucketName}.s3.${spec.region}.amazonaws.com"
            originId = "s3-origin"
            s3OriginConfig = {originAccessIdentity = ""}
        }]
        defaultCacheBehavior = {
            targetOriginId = "s3-origin"
            viewerProtocolPolicy = "redirect-to-https"
            allowedMethods = ["GET", "HEAD"]
            cachedMethods = ["GET", "HEAD"]
            forwardedValues = {queryString = False, cookies = {forward = "none"}}
        }
        restrictions = {geoRestriction = {restrictionType = "none"}}
        viewerCertificate = {acmCertificateArn = _certificateArn, sslSupportMethod = "sni-only"}
        tags = spec.tags
    } if _certificateArn else None

    _distribution = {
        apiVersion = "cloudfront.aws.m.upbound.io/v1beta1"
        kind = "Distribution"
        metadata.annotations = {
            "krm.kcl.dev/composition-resource-name" = "distribution"
        }
        spec.forProvider = _distributionForProvider
    } if _certificateArn else None

    _distributionDomain = ocds["distribution"]?.Resource?.status?.atProvider?.domainName

    _aliasRecord = {
        apiVersion = "route53.aws.m.upbound.io/v1beta1"
        kind = "Record"
        metadata.annotations = {
            "krm.kcl.dev/composition-resource-name" = "alias-record"
        }
        spec.forProvider = schemas_providers.Route53AwsmUpboundIoV1beta1RecordSpecForProvider {
            zoneId = spec.zoneId
            name = spec.domainName
            $type = "A"
            alias = {name = _distributionDomain, zoneId = "Z2FDTNDATAQYW2", evaluateTargetHealth = False}
        }
    } if _distributionDomain else None

    _dxr = {
        apiVersion = oxr.apiVersion
        kind = oxr.kind
        metadata = oxr.metadata
        status.cloudFrontDomainName = _distributionDomain
    } if _distributionDomain else None

    _resources = [_bucket, _bucketPolicy, _certificate] + ([_distribution] if _distribution else []) + ([_aliasRecord] if _aliasRecord else []) + ([_dxr] if _dxr else [])

    _resources
}
