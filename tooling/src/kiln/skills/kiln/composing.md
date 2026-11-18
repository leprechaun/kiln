# Composing

Design the XR's spec and status schemas, then write the compose function that turns an XR into
resources. Write each piece test first ([`testing.md`](testing.md)); KCL syntax is in the
`kcl-primer` skill.

## Design the XR spec

In `kcl-scripts/schemas_compositions.k`, add a schema named `<Kind>Spec`, designed from the
consumer's side (what should someone configuring this actually choose?), not by mirroring every
cloud field:

```kcl
schema ObjectStoreSpec:
    bucketName: str
    region: str = "us-east-1"
    tags?: {str:str}
```

The spec schema is closed: a field it does not declare is an error, so a misspelt field in a test
fails in `kcl test`, and the XRD rejects it from consumers. On a cluster, a real XR's spec also
carries fields Crossplane adds (`spec.crossplane`); the generated Composition passes your function
only the fields your schema declares, so it never sees them. Do not name a spec field after one of
Crossplane's (such as `crossplane`).

### Spec rules

A rule that spans fields (aliases need a certificate, `min <= max`) goes in a `check:` block, so an
XR that breaks it fails with your message instead of producing resources the cloud rejects:

```kcl
schema SiteSpec:
    aliases?: [str]
    certificateArn?: str

    check:
        not aliases or certificateArn, "aliases need certificateArn"
```

`kcl test` cannot assert that something fails, so cover each rule with an `invalid-<case>.yaml`
render fixture ([`rendering.md`](rendering.md)) and keep the passing side in `kcl test`.

### Status

To report status back to consumers, add an optional `<Kind>Status` schema
(`schema ObjectStoreStatus:` with optional fields such as `bucketArn?: str`). Keep it closed:
that is what makes a misspelt status field a compile error. When it exists, Kiln puts it in the
XRD under `status`. Without one the XRD declares no status, and a real API server may drop
status fields you set.

## Write the compose function

Create `kcl-scripts/<kind lowercased>.k` (for `ObjectStore`, `objectstore.k`) holding one
function named `compose<Kind>` with exactly this signature:

```kcl
import .schemas_compositions
import .schemas_providers

composeObjectStore = lambda oxr, ocds -> [any] {
    spec: schemas_compositions.ObjectStoreSpec = oxr.spec

    _bucketName = "bucket"

    _bucketForProvider: schemas_providers.S3AwsmUpboundIoV1beta1BucketSpecForProvider = {
        region = spec.region
        tags = spec.tags
    }

    _bucket = {
        apiVersion = "s3.aws.m.upbound.io/v1beta1"
        kind = "Bucket"
        metadata.annotations = {
            "crossplane.io/external-name" = spec.bucketName
            "krm.kcl.dev/composition-resource-name" = _bucketName
        }
        spec.forProvider = _bucketForProvider
    }

    [_bucket]
}
```

- The function returns the list of resources to compose. Kiln finds your kinds by looking for
  `compose<Kind> = lambda oxr, ocds` in `kcl-scripts/*.k` (files starting with `schemas_` or
  ending in `_test.k` are skipped).
- Every composed resource needs a unique `krm.kcl.dev/composition-resource-name` annotation.
  That name is how you find it again in `ocds`. Define each name once as a constant and use it
  for both the annotation and the lookup.
- `crossplane.io/external-name` sets the cloud object's own name.
- **Build every `forProvider` through its imported schema** (as above), so a misspelt, misshapen
  or missing field fails `kcl test` in seconds. A resource built as a plain dict skips that
  check; `kiln render` still validates it against the CRD, but only after a Docker round trip.
- Bind XR values to locals (`spec`, `_region`) before building resource dicts. Inside a dict with
  its own `spec.<x>` key, `spec.<y>` means that dict's `spec` (see `kcl-primer`).
- Leave `spec.providerConfigRef` unset unless a resource needs a different one; set the project
  default with `providerConfig` in `kiln.toml` ([`configuration.md`](configuration.md)).
- The function may only import `.schemas_compositions`, `.schemas_providers`, and the KCL
  standard library (for example `import json`). The generated Composition flattens these files
  into one source string, so an import of another file of your own breaks it.

## Resources that depend on observed state

Many resources can only be built once an earlier one reports something (an ARN, a domain name).
Read it from `ocds`, and emit the dependent resource only when the value exists. Build
schema-typed values *inside* the same `if` that gates the resource, because a schema with
required fields fails when constructed from a missing value:

```kcl
_observedAtProvider = ocds[_bucketName]?.Resource?.status?.atProvider
```

Read `atProvider` through its imported `StatusAtProvider` schema so a misspelt field is a compile
error and not a silent `None`. Build the typed value only once an `atProvider` exists; before
that (cold start) the whole chain is `None`, and every use must stay guarded with `if` or `?.`:

```kcl
_bucketStatus = lambda atProvider -> schemas_providers.S3AwsmUpboundIoV1beta1BucketStatusAtProvider {
    _status: schemas_providers.S3AwsmUpboundIoV1beta1BucketStatusAtProvider = atProvider
    _status
}
_observedBucket = _bucketStatus(_observedAtProvider) if _observedAtProvider else None
_bucketArn = _observedBucket?.arn
```

`status.atProvider` can lag reality by one provider poll. When a resource exists to signal
readiness (ACM `CertificateValidation`), gate on its Ready condition instead; the
`crossplane-intro` skill shows how.

A child XR of your own reports its observed state differently; see "Child XRs" below.

## Report status

To set status on your own XR, add one more item to the returned list: the XR itself, with
`apiVersion`, `kind` and `metadata` copied from `oxr`. Emit it only when there is something to
report, and type the status:

```kcl
_xr = {
    apiVersion = oxr.apiVersion
    kind = oxr.kind
    metadata = oxr.metadata
    status = schemas_compositions.ObjectStoreStatus {bucketArn = _bucketArn}
} if _bucketArn else None

[_bucket] + ([_xr] if _xr else [])
```

## Child XRs

One kind can compose another kind of this project, the way it composes a managed resource. Here
a `Website` composes a `TlsCertificate` and waits for it to report a validated certificate.

**The child reports an explicit status field.** Give the child a status field that answers the
parent's question directly, and set it in the child's own function, for example from a
Ready condition:

```kcl
schema TlsCertificateStatus:
    certificateArn?: str
    validated?: bool
```

```kcl
    # in composeTlsCertificate
    _validationConditions = ocds[_validationName]?.Resource?.status?.conditions or []
    _validated = any_true([c.type == "Ready" and c.status == "True" for c in _validationConditions])
    # ... status = schemas_compositions.TlsCertificateStatus {certificateArn = _certificateArn, validated = _validated}
```

The parent then reads one boolean and never parses conditions.

**The parent emits the child** with an `apiVersion` and `kind` in this project's group, a
composition-resource-name annotation, and a `spec` typed by the child's spec schema:

```kcl
composeWebsite = lambda oxr, ocds -> [any] {
    spec: schemas_compositions.WebsiteSpec = oxr.spec
    _domainName = spec.domainName

    _certificateName = "certificate"

    _certificate = {
        apiVersion = "platform.example.com/v1alpha1"
        kind = "TlsCertificate"
        metadata.annotations = {"krm.kcl.dev/composition-resource-name" = _certificateName}
        spec = schemas_compositions.TlsCertificateSpec {domainName = _domainName}
    }

    _certificateStatus = ocds[_certificateName]?.Resource?.status
    _certificateArn = _certificateStatus?.certificateArn if _certificateStatus?.validated else None

    _xr = {
        apiVersion = oxr.apiVersion
        kind = oxr.kind
        metadata = oxr.metadata
        status = schemas_compositions.WebsiteStatus {certificateArn = _certificateArn}
    } if _certificateArn else None

    [_certificate] + ([_xr] if _xr else [])
}
```

**The parent reads the child's status uncast**, from `ocds["<name>"].Resource.status` with plain
`?.`. Unlike a provider's `atProvider`, a real XR's status also carries fields Crossplane adds
(such as `conditions`), and a cast to the child's closed status schema fails on them with
`Cannot add member 'conditions'`.

In tests, give the observed child a status with `conditions` as well as your own fields, so a
cast would fail there too:

```kcl
ocds = {certificate = {Resource = {status = {
    certificateArn = "arn:aws:acm:us-east-1:111111111111:certificate/example"
    validated = True
    conditions = [{"type" = "Ready", status = "True"}]
}}}}
```

Run `kiln generate` for the child before rendering the parent: `kiln render` checks the child it
emits against the child's generated `xrd.yaml`. The render fixture for an observed child, and what
rendering can and cannot confirm, are in "Child XRs" in [`rendering.md`](rendering.md).
