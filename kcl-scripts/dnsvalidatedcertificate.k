import .schemas_compositions
import .schemas_providers

composeDnsValidatedCertificate = lambda oxr, ocds -> [any] {
    spec: schemas_compositions.DnsValidatedCertificateSpec = oxr.spec

    _certificateForProvider: schemas_providers.AcmAwsmUpboundIoV1beta1CertificateSpecForProvider = {
        region = spec.region
        domainName = spec.domainName
        subjectAlternativeNames = spec.subjectAlternativeNames
        tags = spec.tags
        validationMethod = "DNS"
    }

    _certificate = {
        apiVersion = "acm.aws.m.upbound.io/v1beta1"
        kind = "Certificate"
        metadata.annotations = {
            "krm.kcl.dev/composition-resource-name" = "certificate"
        }
        spec.forProvider = _certificateForProvider
    }

    _validationOptions = ocds["certificate"]?.Resource?.status?.atProvider?.domainValidationOptions
    _validationOption = _validationOptions[0] if _validationOptions else None

    _record = {
        apiVersion = "route53.aws.m.upbound.io/v1beta1"
        kind = "Record"
        metadata.annotations = {
            "krm.kcl.dev/composition-resource-name" = "validation-record"
        }
        spec.forProvider = schemas_providers.Route53AwsmUpboundIoV1beta1RecordSpecForProvider {
            zoneId = spec.zoneId
            name = _validationOption.resourceRecordName
            $type = _validationOption.resourceRecordType
            records = [_validationOption.resourceRecordValue]
            ttl = 300
        }
    } if _validationOption else None

    _certificateValidation = {
        apiVersion = "acm.aws.m.upbound.io/v1beta1"
        kind = "CertificateValidation"
        metadata.annotations = {
            "krm.kcl.dev/composition-resource-name" = "certificate-validation"
        }
        spec.forProvider = schemas_providers.AcmAwsmUpboundIoV1beta1CertificateValidationSpecForProvider {
            region = spec.region
            certificateArn = ocds["certificate"]?.Resource?.status?.atProvider?.arn
            validationRecordFqdns = [_validationOption.resourceRecordName]
        }
    } if _validationOption else None

    _observedArn = ocds["certificate"]?.Resource?.status?.atProvider?.arn
    _dxr = {
        apiVersion = oxr.apiVersion
        kind = oxr.kind
        metadata = oxr.metadata
        status.certificateArn = _observedArn
    } if _observedArn else None

    _resources = [_certificate] + ([_record] if _record else []) + ([_certificateValidation] if _certificateValidation else []) + ([_dxr] if _dxr else [])

    _resources
}
