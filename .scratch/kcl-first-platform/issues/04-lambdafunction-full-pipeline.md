# 04: LambdaFunction — full pipeline, schema through rendered manifest

**What to build:** `LambdaFunctionSpec`, `composeLambdaFunction`, a generated manifest, and a passing render smoke test — a full vertical slice reusing the tooling proven in tickets 01 and 03. Independent of ticket 05; can run in parallel with it.

**Blocked by:** 01, 03

**Status:** ready-for-agent

- [ ] `LambdaFunctionSpec` (and nested types such as the lambda code location) is designed from the consumer's perspective
- [ ] `composeLambdaFunction(oxr, ocds) -> [...]` follows the same house rules as ticket 02 (no `option()` calls, gated construction of required-but-possibly-absent fields, single-line type unions, named unions over `any`)
- [ ] `kcl test` passes for `composeLambdaFunction`, covering cold-start, partially-observed, and fully-observed scenarios
- [ ] The generator produces LambdaFunction's Composition YAML/Jsonnet wrapper and XRD schema using the tooling built in ticket 03, with no new generator code needed
- [ ] `crossplane render` succeeds against the generated LambdaFunction Composition
