import .staticwebsite

_siteBaseSpec = {
    bucketName = "my-website-bucket"
    domainName = "www.example.com"
    region = "us-east-2"
    zoneId = "Z123456ABCDEFG"
}

test_site_cold_start_requests_bucket_policy_and_nested_certificate = lambda {
    oxr = {spec = _siteBaseSpec}
    ocds = {}

    result = staticwebsite.composeStaticWebsite(oxr, ocds)

    assert len(result) == 3
    bucket = result[0]
    assert bucket.kind == "Bucket"
    assert bucket.spec.forProvider.region == "us-east-2"

    policy = result[1]
    assert policy.kind == "BucketPolicy"
    assert policy.spec.forProvider.bucket == "my-website-bucket"

    cert = result[2]
    assert cert.kind == "DnsValidatedCertificate"
    assert cert.spec.domainName == "www.example.com"
    assert cert.spec.zoneId == "Z123456ABCDEFG"
    # CloudFront requires ACM certs in us-east-1 regardless of the bucket's region
    assert cert.spec.region == "us-east-1"
}

test_site_waits_for_the_nested_certificate_before_building_the_distribution = lambda {
    oxr = {spec = _siteBaseSpec}
    ocds = {
        "certificate" = {Resource = {status = {}}}
    }

    result = staticwebsite.composeStaticWebsite(oxr, ocds)

    assert len(result) == 3
}

test_site_builds_distribution_once_the_nested_certificate_is_validated = lambda {
    oxr = {spec = _siteBaseSpec}
    ocds = {
        "certificate" = {
            Resource = {status = {certificateArn = "arn:aws:acm:us-east-1:123456789012:certificate/abc"}}
        }
    }

    result = staticwebsite.composeStaticWebsite(oxr, ocds)

    assert len(result) == 4
    distribution = result[3]
    assert distribution.kind == "Distribution"
    assert distribution.spec.forProvider.aliases == ["www.example.com"]
    assert distribution.spec.forProvider.viewerCertificate.acmCertificateArn == "arn:aws:acm:us-east-1:123456789012:certificate/abc"
    origin = distribution.spec.forProvider.origin[0]
    assert origin.domainName == "my-website-bucket.s3.us-east-2.amazonaws.com"
}

test_site_creates_alias_record_and_surfaces_domain_once_distribution_is_observed = lambda {
    oxr = {
        apiVersion = "platform.kcl-first.io/v1alpha1"
        kind = "StaticWebsite"
        metadata = {name = "example-site"}
        spec = _siteBaseSpec
    }
    ocds = {
        "certificate" = {
            Resource = {status = {certificateArn = "arn:aws:acm:us-east-1:123456789012:certificate/abc"}}
        }
        "distribution" = {
            Resource = {status = {atProvider = {domainName = "d123.cloudfront.net"}}}
        }
    }

    result = staticwebsite.composeStaticWebsite(oxr, ocds)

    assert len(result) == 6
    record = result[4]
    assert record.kind == "Record"
    assert record.spec.forProvider.zoneId == "Z123456ABCDEFG"
    assert record.spec.forProvider.name == "www.example.com"
    assert record.spec.forProvider.alias.name == "d123.cloudfront.net"
    assert record.spec.forProvider.alias.zoneId == "Z2FDTNDATAQYW2"

    dxr = result[5]
    assert dxr.kind == "StaticWebsite"
    assert dxr.status.cloudFrontDomainName == "d123.cloudfront.net"
}

test_site_tolerates_extra_fields_the_real_control_plane_injects_into_observed_spec = lambda {
    oxr = {
        spec = {
            bucketName = "my-website-bucket"
            domainName = "www.example.com"
            region = "us-east-2"
            zoneId = "Z123456ABCDEFG"
            crossplane = {compositionRef = {name = "staticwebsite-kcl-first"}}
        }
    }
    ocds = {}

    result = staticwebsite.composeStaticWebsite(oxr, ocds)

    assert len(result) == 3
}
