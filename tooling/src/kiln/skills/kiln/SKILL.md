---
name: kiln
description: >
  Build Crossplane compositions in a Kiln project (a repo with kiln.toml and kcl-scripts/).
  Use when adding or changing a composite kind, importing provider schemas, writing compose
  functions or their tests, running kiln generate/render, or when a render or the cluster
  reports an error.
---

# Kiln

Kiln builds Crossplane compositions from KCL. You write two things by hand: the API your
consumers see (an XR spec schema) and a function that turns it into cloud resources. Kiln
generates everything else: typed provider schemas, the `Composition`, and the
`CompositeResourceDefinition` (XRD).

Terms: an **XR** is the composite resource a consumer creates (it has `spec` and `status`). An
**MR** is one real cloud object a provider manages (its `spec.forProvider` is what you want, its
`status.atProvider` is what exists). `oxr` is the observed XR passed into your function; `ocds` is
a map of the composed resources observed so far. The `crossplane-intro` skill explains these.

## What Kiln is for

Kiln lets you spend your effort on the data structures and the cloud components you are
integrating, and on nothing else:

- **You work on the shapes and the mapping.** What should a consumer be able to ask for
  (the XR spec), and which provider resources does that become (the compose function)?
  Provider schemas are imported and typed, so you work against real field names, not guesses.
- **Your feedback loop is unit tests that run in seconds.** The compose function is a plain
  function from data to data, so `kcl test .` exercises it with no cluster, no Docker and no
  credentials. This is the point of the design, not an extra. Iterate with tests, and render
  only to confirm.
- **YAML is mechanised away.** Kiln generates the Composition and the XRD from your schemas and
  function. The only YAML you write is small sample data for rendering (an example XR and mocked
  observed resources). When a generated file looks wrong, fix the schema or the function upstream
  and regenerate.

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

## Reference

Each file below sits next to this one. Read it when its trigger applies; with only the CLI,
`kiln docs <name>` prints it.

| Read | When |
|------|------|
| [`provider-schemas.md`](provider-schemas.md) | pulling CRDs, choosing a provider group, importing schemas, a composition that is too big |
| [`composing.md`](composing.md) | designing the spec and status schemas, writing the compose function, resources that wait on observed state, reporting status, composing another of your kinds (child XRs) |
| [`testing.md`](testing.md) | writing `<kind>_test.k`: the tests every kind needs |
| [`rendering.md`](rendering.md) | generating and rendering, what render checks, observed-stage fixtures (including child XRs), invalid-XR fixtures |
| [`configuration.md`](configuration.md) | anything in `kiln.toml`: XR scope, provider config, output format |
| [`troubleshooting.md`](troubleshooting.md) | any error from `kcl test`, `kiln`, `kubectl` or the cluster |
| `kcl-primer` skill | KCL syntax, and every KCL compile error |
| `crossplane-intro` skill | XR, MR, `ocds` and the reconcile lifecycle; debugging a live cluster |

## The workflow

You need `kcl`, the `crossplane` CLI, and Docker (only rendering uses Docker). Work on one kind
at a time, from the cheapest check to the most expensive. Each step has a check, and you move on
only once it passes.

```
 once per project       kiln pull-crds                                    provider-schemas.md
 per provider resource  kiln import <crd>          -> kcl test . compiles provider-schemas.md
 per kind
   design               <Kind>Spec (+ <Kind>Status) -> kcl test .         composing.md
   inner loop           write a failing test        -> kcl test .  (fast) testing.md
   (repeat)             write the minimal code      -> kcl test .         composing.md
   outer loop           kiln generate <Kind>        -> kiln render <Kind> rendering.md
   (repeat)             add observed-<stage>.yaml   -> kiln render-all
 before you finish      "Verify your work" below
```

What each check can and cannot tell you:

| Check | Cost | Catches | Misses |
|-------|------|---------|--------|
| `kcl test .` | seconds, no Docker | logic errors, typos in schema fields, wrong or missing `forProvider` fields | anything about the generated Composition or XRD, a closed spec schema, how the real function runtime flattens your files |
| `kiln render <Kind>` | slower, needs Docker | the generated source failing to compile in the real runtime, and every composed resource the cluster would reject (checked against the CRDs in `crds/`) | whether the cloud provider accepts the values; nothing talks to a cluster or AWS |
| `kiln render-all` with `observed-<stage>.yaml` fixtures | same | the stages that depend on observed state: whether the next resource appears, its shape, and whether status is reported | observed shapes you got wrong in the fixture (a fixture encodes your assumptions) |
| `kiln render-all` with `invalid-<case>.yaml` fixtures | same | that an XR breaking a spec rule (a `check:` block) is rejected with the right error, which `kcl test` cannot assert | rules you never wrote |

Neither check substitutes for the other: a green `kcl test .` has hidden real bugs before, and
only a render found them. Write tests and render fixtures for the same stages your function has:
cold start (nothing observed yet), partly observed, and fully observed.

## Running kiln

Kiln is not published on PyPI; it is installed from GitHub. Every command here is written as
plain `kiln …`. If `kiln` is not on your `PATH`, run it through `uvx` with this prefix (the
package is in the `tooling/` subdirectory of the repo):

```bash
uvx --from "git+https://github.com/leprechaun/kiln#subdirectory=tooling" kiln <command>
```

Or install it once with
`uv tool install "git+https://github.com/leprechaun/kiln#subdirectory=tooling"`.

## Project layout

Every command finds its project by searching upward from the current directory for `kiln.toml`
(or takes `--root <path>`). Start one with `kiln init <dir>`. The layout is fixed:

| Path | Holds |
|------|-------|
| `kiln.toml` | the API group for your XRs, and optional settings ([`configuration.md`](configuration.md)) |
| `manifests/crossplane-providers/` | one Provider manifest per provider; `pull-crds` reads these |
| `manifests/functions.yaml` | the composition functions rendering needs (already set up) |
| `crds/` | downloaded CRDs (generated, git-ignored) |
| `kcl-scripts/` | your KCL: schemas, compose functions, tests |
| `manifests/crossplane-compositions/<kind>/` | generated Composition and `xrd.yaml`; deploy these, put nothing else here |
| `render-fixtures/<kind>/` | `xr.yaml`, the sample XR; `observed-<stage>.yaml`, mocked observed resources for each stage; `invalid-<case>.yaml`, XRs that must be rejected |

Arguments you pass to a command (like a CRD path) are relative to where you run it, not to the
project root. `kcl-scripts/` is **one compiled package**: `kcl test .` compiles every file in it
together.

## Verify your work

You are done only when all three of these pass, run in this order from the project
(or `kcl-scripts/` for the first):

```bash
cd kcl-scripts && kcl test .     # every test passes
kiln generate-all                # prints a check mark for every kind
kiln render-all                  # prints a check mark for every kind and stage, exits 0
```

- `kcl test .` can look green when there are no tests. A project with no tests is not
  done: check that every kind has a `<kind>_test.k` covering the list in
  [`testing.md`](testing.md), and that the `kcl test .` output lists tests for each kind.
- Run `kiln generate-all` every time, before rendering. `render` uses the generated files on
  disk, so stale ones give you a render of old code. If the project is in git,
  `git diff manifests/` after `kiln generate-all` shows what regenerating changed.
- Every kind needs `render-fixtures/<kind>/xr.yaml`; `kiln render-all` fails for a kind
  without one. A kind whose function reacts to observed state also needs
  `observed-<stage>.yaml` fixtures, and a kind with spec rules needs an `invalid-<case>.yaml`
  per rule ([`rendering.md`](rendering.md)).
- A failure prints a cross and the error; look it up in [`troubleshooting.md`](troubleshooting.md).
  Fix the cause upstream and run the sequence again from the top.
- Rendering needs Docker and the `crossplane` CLI. If either is missing, `kiln render`
  fails. That is not a pass. Say that the render step could not be run, and do not
  report the work as verified.

## Checklist for a new kind

1. `kiln pull-crds`, then `kiln import` each provider resource you use, from the `.m.` groups.
2. Add `<Kind>Spec` and, if you report status, `<Kind>Status`.
3. Write failing tests in `kcl-scripts/<kind>_test.k`, then `compose<Kind>` in
   `kcl-scripts/<kind>.k`, until `kcl test .` passes.
4. `kiln generate <Kind>`, add `render-fixtures/<kind>/xr.yaml`, an `observed-<stage>.yaml`
   per observed stage and an `invalid-<case>.yaml` per spec rule, and `kiln render <Kind>` succeeds.
5. Set `providerConfig` in `kiln.toml` if the cluster has no `ClusterProviderConfig/default`.
6. Run "Verify your work" above.
7. Commit the generated manifests; deploy `manifests/crossplane-compositions/<kind>/`.
