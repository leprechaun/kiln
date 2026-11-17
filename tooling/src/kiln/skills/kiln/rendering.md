# Rendering

Generate the Composition and XRD, then render them against sample XRs and observed stages.

## Generate

```bash
kiln generate ObjectStore       # one kind
kiln generate-all               # every kind found in kcl-scripts/
```

This writes `composition.yaml` and `xrd.yaml` under
`manifests/crossplane-compositions/<kind lowercased>/` (other files in jsonnet mode; see
[`configuration.md`](configuration.md)). It expects the spec schema `<Kind>Spec` (and optionally `<Kind>Status`);
the XRD's plural is the lowercased kind plus `s`, its version is `v1alpha1`, and its API group
comes from `kiln.toml`. It warns if the Composition nears the Kubernetes size limit (see "Composition size" in
[`provider-schemas.md`](provider-schemas.md)).

## Render

Write a sample XR in
`render-fixtures/<kind lowercased>/xr.yaml`:

```yaml
apiVersion: platform.example.com/v1alpha1
kind: ObjectStore
metadata:
  name: example-store
spec:
  bucketName: my-bucket
  region: eu-west-1
```

```bash
kiln render ObjectStore
```

Rendering runs the generated source inside the real function runtime, so it catches mistakes
`kcl test` cannot: flattening problems, a closed spec schema, and wrong observed shapes. Then
Kiln checks what it rendered.

## What render checks

After `crossplane render` succeeds, Kiln checks every composed resource in the output against its
CRD in `crds/` (or, for a child XR of your own, its generated `xrd.yaml`), and fails if:

- a namespaced XR composes a cluster-scoped kind (the error names the `.m.` group to use);
- a field is not declared in the schema (`.spec.forProvider.bucket: field not declared in schema`);
- a value has the wrong type, such as a one-item list where the API takes an object, or an object
  where it takes a JSON string;
- a required field is missing, including provider parameters such as `region`;
- the kind has no CRD in `crds/` (wrong `apiVersion`, or a provider that is not pulled yet).

These are the errors the cluster would give you on apply, minus the deploy. Fix the function, not
the check. `--no-validate` (on `render` and `render-all`) skips it, for example while `crds/` is
out of date.

## Observed stages

For a function that reacts to observed state, mock the composed resources it reads. Each one's
`crossplane.io/composition-resource-name` annotation must equal the name you used in `ocds`:

```yaml
apiVersion: s3.aws.m.upbound.io/v1beta1
kind: Bucket
metadata:
  name: example-store-1a2b3c
  annotations:
    crossplane.io/composition-resource-name: bucket
status:
  atProvider:
    arn: arn:aws:s3:::my-bucket
```

Put them in `render-fixtures/<kind>/observed-<stage>.yaml`, one file per stage, each holding
**every** resource observed at that point (a snapshot, not a delta). Number the files to follow
the order resources come up:

```
render-fixtures/objectstore/
  xr.yaml                      # cold start: nothing observed
  observed-1-bucket.yaml       # the bucket exists
  observed-2-all.yaml          # everything exists; status is reported
```

`kiln render-all` renders each kind cold (only `xr.yaml`), then once per `observed-*.yaml` file in
name order, checks every render, and prints a line for each. Without these files it never
exercises the resources gated on observed state. To render one stage by hand:

```bash
kiln render ObjectStore --observed-resources render-fixtures/objectstore/observed-1-bucket.yaml
kiln render ObjectStore --observed-resources path/to/dir/   # every .yaml/.yml in it, together
```

`--observed-resources` takes a multi-document YAML file, or a directory whose `.yaml`/`.yml` files
are all loaded together. A path that does not exist is an error.
