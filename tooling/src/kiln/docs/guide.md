# Kiln guide

Kiln builds Crossplane compositions from KCL. You write two things by hand: the
API your consumers see (an XR spec schema) and a function that turns it into
cloud resources. Kiln generates everything else: typed provider schemas, the
`Composition`, and the `CompositeResourceDefinition` (XRD).

Terms: an **XR** is the composite resource a consumer creates (it has `spec` and
`status`). An **MR** is one real cloud object a provider manages (its `spec.forProvider`
is what you want, its `status.atProvider` is what exists). `oxr` is the observed XR
passed into your function; `ocds` is a map of the composed resources observed so far.

## Ground rules

1. **Tests are part of the deliverable.** For every kind you create, write
   `kcl-scripts/<kind>_test.k` and make `kcl test .` pass. A kind without tests is not
   done, even if it generates and renders cleanly.
2. **Write the test first.** For each kind, in this order: spec (and status) schema, a
   failing test, the compose function, `kcl test .` green, and only then
   `kiln generate` and `kiln render`.
3. **Deferring work never defers tests.** If you are told to concentrate on the KCL, or to
   hold off on rendering or the YAML, that postpones `kiln generate` and `kiln render`
   only. Schemas, the compose function and its tests are all KCL, and all of them are in
   scope.
4. **Done means verified.** You are done when the three commands under "Verify your
   work" pass. If you could not run one, say so; do not call the work done.

## The workflow

| # | Phase | Command | Who |
|---|-------|---------|-----|
| 1 | Pull provider CRDs | `kiln pull-crds` | tool |
| 2 | Import the provider schemas you use | `kiln import <crd file>` | tool |
| 3 | Design the XR spec (and status) schema | edit `kcl-scripts/schemas_compositions.k` | you |
| 4 | Write the tests, then the compose function | edit `kcl-scripts/<kind>_test.k`, then `kcl-scripts/<kind>.k`; run `kcl test .` | you |
| 5 | Generate manifests and render | `kiln generate-all`, `kiln render-all` | tool |

You need `kcl`, the `crossplane` CLI, and Docker (only rendering uses Docker).
Phases 1 and 2 work with `kcl` 0.12 or 0.13.

Kiln is not published on PyPI; it is installed from GitHub. Every command in this
guide is written as plain `kiln …`. If `kiln` is not on your `PATH` and you run it
through `uvx`, put this prefix in front of each one (the package is in the
`tooling/` subdirectory of the repo):

```bash
uvx --from "git+https://github.com/leprechaun/kiln#subdirectory=tooling" kiln <command>
```

Or install it once with
`uv tool install "git+https://github.com/leprechaun/kiln#subdirectory=tooling"`.

## The intended workflow

Work on one kind at a time, from the cheapest check to the most expensive. Each
step has a check, and you do not move on until it passes.

```
 once per project       kiln pull-crds
 per provider resource  kiln import <crd>               -> schemas compile (kcl test .)
 per kind
   design               <Kind>Spec (+ <Kind>Status)     -> kcl test .
   inner loop           write a failing test            -> kcl test .   (fast, no Docker)
   (repeat)             write the minimal code          -> kcl test .
   outer loop           kiln generate <Kind>            -> kiln render <Kind>   (Docker)
   (repeat)             add observed fixtures           -> kiln render <Kind> --observed-resources ...
 before you finish      the full verification below
```

Where each kind of check fits, and what it can and cannot tell you:

| Check | Cost | Catches | Misses |
|-------|------|---------|--------|
| `kcl test .` | seconds, no Docker | logic errors, typos in schema fields, wrong or missing `forProvider` fields | anything about the generated Composition or XRD, a closed spec schema, how the real function runtime flattens your files |
| `kiln render <Kind>` | slower, needs Docker | the generated source failing to compile in the real runtime, a spec schema that rejects real XRs, wrong output shape | whether the cloud provider accepts the values; nothing talks to a cluster or AWS |
| `kiln render <Kind> --observed-resources ...` | same | the stages that depend on observed state: whether the next resource appears, and whether status is reported | observed shapes you got wrong in the fixture (a fixture encodes your assumptions) |

Neither check substitutes for the other. A green `kcl test .` has hidden real bugs
before; only a render found them. Check observed field names against the imported
`StatusAtProvider` schema, not against memory.

Write tests and render fixtures for the same stages your function has: cold start
(nothing observed yet), partly observed, and fully observed.

## Project layout

Every command finds its project by searching upward from the current directory
for `kiln.toml` (or take `--root <path>`). Start one with `kiln init <dir>`. The
layout is fixed:

| Path | Holds |
|------|-------|
| `kiln.toml` | the API group for your XRs: `group = "platform.example.com"` |
| `manifests/crossplane-providers/` | one Provider manifest per provider; `pull-crds` reads these |
| `manifests/functions.yaml` | the composition functions rendering needs (already set up) |
| `crds/` | downloaded CRDs (generated, git-ignored) |
| `kcl-scripts/` | your KCL: schemas, compose functions, tests |
| `manifests/crossplane-compositions/<kind>/` | generated `composition.yaml` and `xrd.yaml`; deploy these, put nothing else here |
| `render-fixtures/<kind>/` | sample XRs and mocked observed resources for rendering |

Arguments you pass to a command (like a CRD path) are relative to where you run
it, not to the project root. `kcl-scripts/` is **one compiled package**: `kcl test .`
compiles every file in it together.

## Phase 1: pull CRDs

```bash
kiln pull-crds
```

Downloads every CRD of the providers in `manifests/crossplane-providers/` into
`crds/<group>/<version>/<kind>.yaml`. No cluster or credentials needed. You only
repeat it to add a provider or bump a provider's version.

Each AWS group exists twice, for example `s3.aws.m.upbound.io` and
`s3.aws.upbound.io`. Use the `.m.` one: it is the namespaced variant, and its
resources use `apiVersion: s3.aws.m.upbound.io/v1beta1`. Check `ls crds/<group>/`
for the versions available.

## Phase 2: import the provider schemas you use

Import only the resources your function will create or read, not everything in `crds/`:

```bash
kiln import crds/s3.aws.m.upbound.io/v1beta1/bucket.yaml
```

This appends curated KCL schemas to `kcl-scripts/schemas_providers.k`: the
resource's `SpecForProvider` (what you set) and `StatusAtProvider` (what you can
read back), plus the nested types they use. Names are prefixed with the group and
version, for example `S3AwsmUpboundIoV1beta1BucketSpecForProvider` and
`S3AwsmUpboundIoV1beta1BucketStatusAtProvider`. Read the file (or `--print`) to see
the real field names and docs before you use them. Do not guess them.

- Importing is safe to repeat: a resource's schemas are replaced in place, and ones
  the provider no longer generates are dropped. Re-run `kiln pull-crds` and then
  `kiln import` for each resource after a provider version bump.
- Do not hand-edit imported schemas; the next import overwrites them.
- `type` is a reserved word in KCL, so a field called `type` is written `$type`.
  It serializes back to `type` in the YAML.
- The `StatusAtProvider` schemas are closed (unknown fields are an error).

## Phase 3: design the XR spec

In `kcl-scripts/schemas_compositions.k`, add a schema named `<Kind>Spec`, designed
from the consumer's side (what should someone configuring this actually choose?),
not by mirroring every cloud field:

```kcl
schema ObjectStoreSpec:
    bucketName: str
    region: str = "us-east-1"
    tags?: {str:str}
    [str]: any
```

**End every spec schema with `[str]: any`.** A real XR carries extra
control-plane fields (such as `spec.crossplane`) that your schema does not declare, and
a closed schema rejects them. `kcl test` fixtures never include those fields, so
only a real render shows the failure. Generation strips this from the XRD, so it
does not widen your public API.

To report status back to consumers, add an optional `<Kind>Status` schema
(`schema ObjectStoreStatus:` with optional fields such as `bucketArn?: str`).
Keep it closed: that is what makes a misspelt status field a compile error. When
it exists, Kiln puts it in the XRD under `status`. Without one the XRD declares no
status, and a real API server may drop status fields you set.

## Phase 4: write the tests, then the compose function

Create `kcl-scripts/<kind lowercased>.k` (for `ObjectStore`, `objectstore.k`)
holding one function named `compose<Kind>` with exactly this signature:

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

- The function returns the list of resources to compose. Kiln finds your kinds by
  looking for `compose<Kind> = lambda oxr, ocds` in `kcl-scripts/*.k` (files
  starting with `schemas_` or ending in `_test.k` are skipped).
- Every composed resource needs a unique `krm.kcl.dev/composition-resource-name`
  annotation. That name is how you find it again in `ocds`. Define each name once as a
  constant and use it for both the annotation and the lookup.
- `crossplane.io/external-name` sets the cloud object's own name.
- Type every `forProvider` value with its imported schema (as above), so a misspelt
  or missing field fails `kcl test`.
- The generated Composition flattens your files into one source string, so the
  function may only import `.schemas_compositions`, `.schemas_providers`, and the KCL
  standard library (for example `import json`). Do not import another file of your own.

### Resources that depend on observed state

Many resources can only be built once an earlier one reports something (an ARN, a
domain name). Read it from `ocds`, and emit the dependent resource only when the
value exists. Build schema-typed values *inside* the same `if` that gates the resource,
because a schema with required fields fails when constructed from a missing value:

```kcl
_observedAtProvider = ocds[_bucketName]?.Resource?.status?.atProvider
```

Read `atProvider` through its imported `StatusAtProvider` schema so a misspelt
field is a compile error and not a silent `None`. Build the typed value only once an
`atProvider` exists; before that (cold start) the whole chain is `None`, and every use
must stay guarded with `if` or `?.`:

```kcl
_bucketStatus = lambda atProvider -> schemas_providers.S3AwsmUpboundIoV1beta1BucketStatusAtProvider {
    _status: schemas_providers.S3AwsmUpboundIoV1beta1BucketStatusAtProvider = atProvider
    _status
}
_observedBucket = _bucketStatus(_observedAtProvider) if _observedAtProvider else None
_bucketArn = _observedBucket?.arn
```

If you compose another XR of your own as a child, its observed state is that XR's
status, not an `atProvider`. Read it with plain `?.` and do not cast it to a closed
status schema: Crossplane adds its own fields (such as `conditions`) to a real XR's
status, which a closed schema would reject.

### Reporting status

To set status on your own XR, add one more item to the returned list: the XR itself,
with `apiVersion`, `kind` and `metadata` copied from `oxr`. Emit it only when there is
something to report, and type the status:

```kcl
_xr = {
    apiVersion = oxr.apiVersion
    kind = oxr.kind
    metadata = oxr.metadata
    status = schemas_compositions.ObjectStoreStatus {bucketArn = _bucketArn}
} if _bucketArn else None

[_bucket] + ([_xr] if _xr else [])
```

### KCL gotchas

- A type annotation is only valid on a local variable. Not on a dotted path
  (`spec.forProvider: T = ...`) and not on a dict-literal key. Use the constructor form,
  `spec.forProvider = T { ... }`, instead.
- KCL has no leading-operator line continuation: a line starting with `+` does not
  continue the previous one. Keep the expression on one line or bind part of it to a local.
- `type X = A | B` aliases must be written on one line.
- Because `kcl-scripts/` is one package, top-level names in test files collide across
  files. Prefix test functions and shared `_`-locals with your kind's name
  (`_objectStoreBaseOxr`, not `_baseOxr`).

### Tests

Tests are a required part of every kind, written before the function they test. They
live in `kcl-scripts/<kind>_test.k` and run with:

```bash
cd kcl-scripts
kcl test .
```

```kcl
import .objectstore

test_builds_the_bucket_from_spec = lambda {
    oxr = {spec = {bucketName = "my-bucket", region = "eu-west-1"}}
    ocds = {}

    result = objectstore.composeObjectStore(oxr, ocds)

    assert len(result) == 1
    assert result[0].kind == "Bucket"
}
```

A kind is not tested until its `<kind>_test.k` has a `test_*` function for each of these:

1. **Every resource it can emit:** `apiVersion`, `kind`, the composition-resource-name
   annotation, and the `forProvider` fields that come from the spec (and the external
   name, if you set one).
2. **Optional spec fields:** passed through when set, and absent when not set.
3. **Defaults:** a spec default takes effect when the consumer leaves the field out.
4. **Every conditional resource** (anything built `if ... else None`): absent when its
   condition is false or its input is not observed yet, present when it is.
5. **Observed-state stages:** cold start (`ocds = {}`), a resource observed but with an
   empty `atProvider = {}`, partly observed, and fully observed. Assert exactly what is
   emitted at each stage.
6. **An extra field in the spec:** a test whose `spec` also carries an unexpected field
   (such as `crossplane = {}`) and still composes. This mirrors the `[str]: any` rule.
7. **Status:** the returned XR carries the right status once the value is observed, and is
   not emitted before.

Write one test, watch it fail, write the minimal code to pass it, repeat; do not write
the whole function first and the tests afterwards. `kcl test` is necessary but not
sufficient: a green suite has hidden real bugs before. The render step below catches what
it cannot.

## Phase 5: generate and render

```bash
kiln generate ObjectStore       # one kind
kiln generate-all               # every kind found in kcl-scripts/
```

This writes `composition.yaml` and `xrd.yaml` under
`manifests/crossplane-compositions/<kind lowercased>/`. It expects the spec schema
`<Kind>Spec` (and optionally `<Kind>Status`); the XRD's plural is the lowercased kind
plus `s`, its version is `v1alpha1`, and its API group comes from `kiln.toml`.

Then render the Composition for real. Write a sample XR in
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

For a function that reacts to observed state, mock a composed resource in
`render-fixtures/<kind>/` (its `crossplane.io/composition-resource-name` annotation
must equal the name you used in `ocds`) and render again:

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

```bash
kiln render ObjectStore --observed-resources render-fixtures/objectstore/observed-bucket.yaml
kiln render-all
```

Rendering exercises the generated source inside the real function runtime, so it
catches mistakes `kcl test` cannot: flattening problems, a closed spec schema,
and wrong observed shapes.

## Verify your work

You are done only when all three of these pass, run in this order from the project
(or `kcl-scripts/` for the first):

```bash
cd kcl-scripts && kcl test .     # every test passes
kiln generate-all                # prints a check mark for every kind
kiln render-all                  # prints a check mark for every kind, exits 0
```

- `kcl test .` can look green when there are no tests. A project with no tests is not
  done: check that every kind has a `<kind>_test.k` covering the list under "Tests", and
  that the `kcl test .` output lists tests for each kind.
- Run `kiln generate-all` every time, before rendering. Never trust whatever
  manifests are already on disk: `render` uses the generated files, so stale ones
  give you a render of old code. If the project is in git, `git diff manifests/`
  after `kiln generate-all` shows what regenerating changed.
- Every kind needs `render-fixtures/<kind>/xr.yaml`. `kiln render-all` fails for a kind
  without one.
- A failure prints a cross and the error. Fix the cause and run the sequence again from
  the top. Do not edit the generated files in `manifests/` by hand.
- Rendering needs Docker and the `crossplane` CLI. If either is missing, `kiln render`
  fails. That is not a pass. Say that the render step could not be run, and do not
  report the work as verified.

## Checklist for a new kind

1. `kiln pull-crds`, then `kiln import` each provider resource you use.
2. Add `<Kind>Spec` (ending in `[str]: any`) and, if you report status, `<Kind>Status`.
3. Write failing tests in `kcl-scripts/<kind>_test.k` (the list under "Tests"), then `compose<Kind>` in `kcl-scripts/<kind>.k`, until `kcl test .` passes.
4. `kiln generate <Kind>`, add `render-fixtures/<kind>/xr.yaml` (and observed fixtures), `kiln render <Kind>` succeeds.
5. Run the full verification above.
6. Commit the generated manifests; deploy `manifests/crossplane-compositions/<kind>/`.
