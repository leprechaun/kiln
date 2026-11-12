# 03: Generate and render the Composition manifest, proven via IAMRole

**What to build:** The OpenAPI normalizer and the Composition/XRD generator, producing IAMRole's real manifest and passing a `crossplane render` smoke test. This is the first point the full five-phase pipeline runs end-to-end.

**Blocked by:** 02

**Status:** ready-for-agent

- [ ] The normalizer fixes `kcl doc generate --format openapi`'s four known defects: `bool` emitted as `"bool"` instead of `"boolean"`; defaults emitted as raw unparsed KCL source text instead of typed JSON values; a field with a default still listed as required; and an internally inconsistent, non-structural `$ref` scheme
- [ ] The generator enforces the `composeKind(oxr, ocds)` naming and signature convention at generation time, failing clearly if violated
- [ ] The generator produces the Composition YAML/Jsonnet wrapper (pipeline step, `importstr`, the `option(...)` glue line, auto-ready step) and the XRD's OpenAPI schema mechanically from IAMRole's schemas and compose function, with no hand-written glue
- [ ] Running `crossplane render` against the generated IAMRole Composition succeeds (a non-zero exit or error is a failure); no assertions are made against the rendered manifest's contents
- [ ] pytest unit tests cover the normalizer and generator as pure functions with fixture inputs and asserted outputs
