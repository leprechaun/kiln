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
    [str]: any
```

**End every spec schema with `[str]: any`.** A real XR carries extra control-plane fields (such
as `spec.crossplane`) that your schema does not declare, and a closed schema rejects them.
`kcl test` fixtures never include those fields, so only a real render shows the failure.
Generation strips this from the XRD, so it does not widen your public API.

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

If you compose another XR of your own as a child, its observed state is that XR's status, not an
`atProvider`. Read it with plain `?.` and keep it uncast: Crossplane adds its own fields (such as
`conditions`) to a real XR's status, which a closed status schema would reject.

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
