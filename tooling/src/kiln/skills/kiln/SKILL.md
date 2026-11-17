---
name: kiln
description: >
  Build Crossplane compositions in a Kiln project (a repo with kiln.toml and kcl-scripts/).
  Use when adding or changing a composite kind, importing provider schemas, writing compose
  functions or their tests, or running kiln generate/render.
---

# Kiln

Kiln turns KCL into Crossplane compositions. You write the XR spec schema and a `compose<Kind>`
function; Kiln generates provider schemas, the Composition and the XRD.

**Run `kiln docs` first.** It is the single source of truth for commands, layout, KCL gotchas and
the required tests. This skill only sets the order of work; it does not restate that guide, so it
cannot drift from it.

## Order of work, per kind

1. `kiln pull-crds`, then `kiln import <crd>` for each provider resource you use.
2. Add `<Kind>Spec` to `kcl-scripts/schemas_compositions.k`. End it with `[str]: any`.
3. Test first. Write one failing test in `kcl-scripts/<kind>_test.k`, watch it fail, write the
   minimal `compose<Kind>` to pass it, run `kcl test .`, repeat. Do not write the whole function
   and add tests afterwards.
4. Only then `kiln generate <Kind>` and `kiln render <Kind>` (needs Docker and `crossplane`).
5. Finish with the three commands under "Verify your work" in `kiln docs`.

## Rules that are easy to forget

- **Tests are the deliverable, not an extra.** A kind with no `<kind>_test.k` is not done, even if
  it generates and renders cleanly. `kcl test .` is the fast loop (seconds, no Docker); render only
  confirms. Cover every emitted resource, optional fields, defaults, conditional resources, each
  observed-state stage (cold start, partly, fully observed), an extra spec field, and status; the
  full list is under "Tests" in `kiln docs`.
- Deferring rendering, or "just do the KCL", never defers tests.
- Never hand-edit `manifests/crossplane-compositions/` or imported provider schemas. Fix the
  schema or function and regenerate.
- Always `kiln generate-all` before `kiln render-all`; render uses what is on disk.
- If Docker or `crossplane` is missing, say render could not run. Do not call the work verified.
- `format = "jsonnet"` in `kiln.toml` writes `composition.jsonnet` + `composition.k` instead of
  `composition.yaml`; `kiln render` then needs the `jsonnet` binary on `PATH`.

## Debugging

| Symptom | Look at |
|---------|---------|
| `kcl test .` syntax error | `kcl-primer` skill |
| Passes `kcl test`, fails `kiln render` | Closed spec schema (missing `[str]: any`), a cross-file import, wrong observed-resource shape |
| Resource never appears | Its `ocds` lookup name differs from its `composition-resource-name` annotation |
| Status not reported | Missing `<Kind>Status` schema, so the XRD declares no status |
| Concepts (XR, MR, ocds) | `crossplane-intro` skill |
