import .dnsvalidatedcertificate

_certBaseSpec = {
    domainName = "example.com"
    region = "us-east-1"
    zoneId = "Z123456ABCDEFG"
}

test_cert_cold_start_only_requests_the_certificate = lambda {
    oxr = {spec = _certBaseSpec}
    ocds = {}

    result = dnsvalidatedcertificate.composeDnsValidatedCertificate(oxr, ocds)

    assert len(result) == 1
    cert = result[0]
    assert cert.kind == "Certificate"
    assert cert.spec.forProvider.domainName == "example.com"
    assert cert.spec.forProvider.validationMethod == "DNS"
}

_certBaseOxr = {
    apiVersion = "platform.kcl-first.io/v1alpha1"
    kind = "DnsValidatedCertificate"
    metadata = {name = "example-cert"}
    spec = _certBaseSpec
}

test_cert_surfaces_arn_once_observed_but_before_validation_options_exist = lambda {
    ocds = {
        "certificate" = {
            Resource = {status = {atProvider = {arn = "arn:aws:acm:us-east-1:123456789012:certificate/abc"}}}
        }
    }

    result = dnsvalidatedcertificate.composeDnsValidatedCertificate(_certBaseOxr, ocds)

    assert len(result) == 2
    dxr = result[1]
    assert dxr.kind == "DnsValidatedCertificate"
    assert dxr.status.certificateArn == "arn:aws:acm:us-east-1:123456789012:certificate/abc"
}

test_cert_creates_the_validation_record_and_waits_for_validation_once_options_are_known = lambda {
    ocds = {
        "certificate" = {
            Resource = {
                status = {
                    atProvider = {
                        arn = "arn:aws:acm:us-east-1:123456789012:certificate/abc"
                        domainValidationOptions = [{
                            domainName = "example.com"
                            resourceRecordName = "_acme.example.com."
                            resourceRecordType = "CNAME"
                            resourceRecordValue = "_xyz.acm-validations.aws."
                        }]
                    }
                }
            }
        }
    }

    result = dnsvalidatedcertificate.composeDnsValidatedCertificate(_certBaseOxr, ocds)

    assert len(result) == 4
    record = result[1]
    assert record.kind == "Record"
    assert record.spec.forProvider.zoneId == "Z123456ABCDEFG"
    assert record.spec.forProvider.name == "_acme.example.com."
    assert record.spec.forProvider.$type == "CNAME"
    assert record.spec.forProvider.records == ["_xyz.acm-validations.aws."]

    validation = result[2]
    assert validation.kind == "CertificateValidation"
    assert validation.spec.forProvider.certificateArn == "arn:aws:acm:us-east-1:123456789012:certificate/abc"
    assert validation.spec.forProvider.validationRecordFqdns == ["_acme.example.com."]

    dxr = result[3]
    assert dxr.status.certificateArn == "arn:aws:acm:us-east-1:123456789012:certificate/abc"
}

test_cert_tolerates_extra_fields_the_real_control_plane_injects_into_observed_spec = lambda {
    oxr = {
        spec = {
            domainName = "example.com"
            region = "us-east-1"
            zoneId = "Z123456ABCDEFG"
            crossplane = {compositionRef = {name = "dnsvalidatedcertificate-kcl-first"}}
        }
    }
    ocds = {}

    result = dnsvalidatedcertificate.composeDnsValidatedCertificate(oxr, ocds)

    assert len(result) == 1
}
