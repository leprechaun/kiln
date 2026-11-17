# Kiln project

This is a Kiln project: Crossplane compositions authored in KCL, with the
provider schemas, Composition and XRD generated for you.

## What Kiln is for

You are here to work on data structures and cloud components, not on YAML. Describe what
consumers can ask for and which provider resources that becomes, write that as a KCL
function, and prove it with unit tests that run in seconds (`kcl test .`, with no cluster,
Docker or credentials). Kiln generates the Composition and the XRD for you: never write or
hand-edit them. The only YAML you write is small sample data for rendering. Tests are the
main feedback loop, which is why the rules below make them mandatory.

## Running kiln

Kiln is not published on PyPI. It is installed from GitHub with `uv`. If `kiln` is
not on your `PATH`, run it through `uvx` by putting this prefix in front of every
`kiln ...` command in this file and in `kiln docs`:

```bash
uvx --from "git+https://github.com/leprechaun/kiln#subdirectory=tooling" kiln <command>
```

Or install it once, so plain `kiln` works:

```bash
uv tool install "git+https://github.com/leprechaun/kiln#subdirectory=tooling"
```

## Start here

Before doing anything else, read the `kiln` skill in `.agents/skills/kiln/` (or run
`kiln docs`, which prints the same text). It explains the whole workflow and the project
layout, and its Reference table says which file next to it to read for each phase, and
for any error. The `kcl-primer` and `crossplane-intro` skills cover KCL syntax and
Crossplane concepts. Refresh the skills after upgrading Kiln with
`kiln install-skills --force`.

## Rules

1. **Tests are part of the deliverable, not an extra.** For every kind you create,
   write `kcl-scripts/<kind>_test.k` and make `kcl test .` pass. A kind without tests
   is not done, even if it generates and renders cleanly.
2. **Write the test first.** For each kind, in this order: spec (and status) schema,
   a failing test, the compose function, `kcl test .` green, and only then
   `kiln generate <Kind>` and `kiln render <Kind>`.
3. **Deferring work never defers tests.** If you are told to concentrate on the KCL,
   or to hold off on rendering or the YAML, that postpones `kiln generate` and
   `kiln render` only. Schemas, the compose function and its tests are all KCL, and
   all of them are in scope.
4. **Done means verified.** You are done when `kcl test .`, `kiln generate-all` and
   `kiln render-all` all pass (see "Verify your work" in `kiln docs`). If you could
   not run one of them, say so. Do not call the work done.
