# Provider schemas

Pull the providers' CRDs, pick the right API group, and import typed KCL schemas for the
resources your function uses.

## Pull CRDs

```bash
kiln pull-crds
```

Downloads every CRD of the providers in `manifests/crossplane-providers/` into
`crds/<group>/<version>/<kind>.yaml`. No cluster or credentials needed. Repeat it only to add a
provider or bump a provider's version. Check `ls crds/<group>/` for the versions available.

## Choose the `.m.` group

Each Upbound AWS service ships two groups, for example `s3.aws.m.upbound.io` and
`s3.aws.upbound.io`. Use the `.m.` one: it is namespaced, and its resources use
`apiVersion: s3.aws.m.upbound.io/v1beta1`.

The legacy (non-`.m.`) groups are cluster-scoped, and a namespaced XR cannot compose them: the
cluster rejects it with `cannot apply cluster scoped composed resource ... for a namespaced
composite resource`. Only a `Cluster`-scoped XR can compose them ([`configuration.md`](configuration.md)).
`kiln import` warns when you import a cluster-scoped CRD into a namespaced project, and
`kiln render` fails if one is composed.

Their shapes also differ, so take every field shape from the imported `.m.` schema, never from an
example written for a legacy group:

| Legacy group | `.m.` group |
|--------------|-------------|
| a nested block is a one-item list: `viewerCertificate = [{...}]` | a nested block is an object: `viewerCertificate = {...}` |
| a policy document may be an object | a policy document such as BucketPolicy `policy` is a JSON string: `json.encode({...})` |
| Bucket has `forProvider.bucket` | Bucket has no `forProvider.bucket`; the name comes from `crossplane.io/external-name` |

## Import the schemas you use

Import only the resources your function will create or read, not everything in `crds/`:

```bash
kiln import crds/s3.aws.m.upbound.io/v1beta1/bucket.yaml
```

This appends curated KCL schemas to `kcl-scripts/schemas_providers.k`: the resource's
`SpecForProvider` (what you set) and `StatusAtProvider` (what you can read back), plus the nested
types they use. Names are prefixed with the group and version, for example
`S3AwsmUpboundIoV1beta1BucketSpecForProvider` and `S3AwsmUpboundIoV1beta1BucketStatusAtProvider`.
Read the file (or `kiln import --print <crd>`) for the real field names and docs before you use
them.

- Importing is safe to repeat: a resource's schemas are replaced in place, and ones the provider
  no longer generates are dropped. After a provider version bump, re-run `kiln pull-crds` and then
  `kiln import` for each resource.
- Leave imported schemas exactly as imported: the next import overwrites them, and they are what
  type-checks your `forProvider` values.
- `type` is a reserved word in KCL, so a field called `type` is written `$type`. It serializes
  back to `type` in the YAML.
- The `StatusAtProvider` schemas are closed (unknown fields are an error).

## Composition size

Kubernetes caps an object's annotations at 262144 bytes (256 KB), and `kubectl apply`
(client-side) stores the whole Composition in one, failing with
`metadata.annotations: Too long: may not be more than 262144 bytes`.

Generation already keeps the Composition small: it includes only the schemas your function
reaches (directly or through other schemas) and drops docstrings and blank lines, so a
composition using several providers is typically tens of KB, far below the limit. With
server-side apply the limit is the object size (about 1.5 MB). The schema files keep everything,
so import freely.

**Use the imported schemas, never hand-written narrow copies of them.** Size is not a reason to
trim `schemas_providers.k` or to write your own smaller `forProvider` schema: tens of KB is
fine, and a hand-written copy does not follow `kiln import` when the provider changes, so it
drifts. If you already have one, `kiln render` checks every rendered resource against the
current CRDs, which catches fields the copy gets wrong in what you emit, but not the fields it
leaves out.

`kiln generate` warns when a Composition passes 80% of the limit and lists the largest parts of
its source. If it does: reduce what the function references, split the kind, or apply with
server-side apply (`kubectl apply --server-side`, or ArgoCD's `ServerSideApply=true`), which
stores no such annotation.
