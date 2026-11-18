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
`kcl test` cannot: flattening problems and wrong observed shapes. Then
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
name order, then each `invalid-*.yaml` (below); it checks every render and prints a line for each. Without these files it never
exercises the resources gated on observed state. To render one stage by hand:

```bash
kiln render ObjectStore --observed-resources render-fixtures/objectstore/observed-1-bucket.yaml
kiln render ObjectStore --observed-resources path/to/dir/   # every .yaml/.yml in it, together
```

`--observed-resources` takes a multi-document YAML file, or a directory whose `.yaml`/`.yml` files
are all loaded together. A path that does not exist is an error.

## Child XRs

An observed child XR (one of your own kinds, composed by this one; see "Child XRs" in
[`composing.md`](composing.md)) is mocked like any other observed resource: its own
`apiVersion` and `kind`, and the composition-resource-name annotation the parent used. Give it
the status your parent reads:

```yaml
apiVersion: platform.example.com/v1alpha1
kind: TlsCertificate
metadata:
  name: example-site-certificate
  annotations:
    crossplane.io/composition-resource-name: certificate
status:
  certificateArn: arn:aws:acm:us-east-1:111111111111:certificate/example
  validated: true
  conditions:
    - type: Ready
      status: "True"
```

That status is an **assumption**: you wrote it, so it shows how the parent reacts to the shape you
expect, not the shape Crossplane returns. Only a live cluster confirms the real one
(`kubectl get <kind> <name> -o yaml`); when you have it, copy it into the fixture.

What rendering the parent confirms, and what it does not:

| Confirmed | Not confirmed |
|-----------|---------------|
| The parent compiles in the real runtime and emits the child | The child's own Composition: rendering runs only the parent's function; render the child separately |
| The emitted child matches the child's generated `xrd.yaml` (required fields, types, scope) | That the child's XRD and Composition are installed on the cluster |
| How the parent reacts to the status in your fixture | The status the child really reports, or how long it takes to get there |

## Invalid XRs

For each spec rule (a `check:` block, see [`composing.md`](composing.md)), add an XR that breaks
it as `render-fixtures/<kind>/invalid-<case>.yaml`, starting with a comment naming the error it
must fail with:

```yaml
# expect-error: aliases need certificateArn
apiVersion: platform.example.com/v1alpha1
kind: Site
metadata:
  name: alias-without-certificate
spec:
  aliases: [www.example.com]
```

`kiln render-all` renders each one and passes it only if the render fails **and** the output
contains the `expect-error` text, so a fixture that fails for another reason (a typo in the
`apiVersion`, Docker not running) does not count as a pass. A fixture without the comment fails.
To render one by hand:

```bash
kiln render Site --xr render-fixtures/site/invalid-alias-without-certificate.yaml
```
