# KCL-first Crossplane platform

Status: ready-for-agent

## Problem Statement

Platform engineers currently have to hand-maintain AWS provider shapes, composition schemas, transformation logic, and Kubernetes manifests separately for every Crossplane composite kind, with no mechanical connection between them. A typo or type mismatch between these layers surfaces only at apply time, if at all — nothing but careful reading enforces that a transformation function's expectations match what a provider actually returns, or what a consumer's XR spec actually promises.

## Solution

A KCL-first authoring pipeline where everything except composition schema design and transformation logic is generated. Provider CRDs are pulled from provider packages, curated into typed KCL schemas, which type-check the hand-written XR schemas and the hand-written `compose*.k` transformation functions; a generator produces the final Composition YAML and XRD OpenAPI schema straight from those same typed artifacts. A platform engineer touches only two things by hand — the XR schema design, and the transformation logic — everything else is mechanically produced and therefore can't silently drift from the hand-written parts.

## User Stories

**Phase 1 — Source provider CRDs**

1. As a platform engineer, I want to run a single command that pulls a provider's CRDs straight from its package, so that I can get fresh schemas without needing live cluster access or credentials.
2. As a platform engineer, I want the pulled CRDs written to disk as plain files, so that I can inspect, diff, and commit them like any other input.
3. As a platform engineer, I want the CRD pull to target the exact package version declared in the provider manifests, so that the schemas I generate always correspond to the provider version we actually run.
4. As a platform engineer, I want to re-run the CRD pull by hand whenever a provider is upgraded, so that schemas can be refreshed deliberately rather than silently going stale.

**Phase 2 — Curate KCL provider schemas**

5. As a platform engineer, I want the curation step to keep only each resource's `spec.forProvider` fields (and any nested types they need), so that I don't have to hand-pick the handful of relevant fields out of dozens of irrelevant status/metadata schemas.
6. As a platform engineer, I want the curation step to discard `status.atProvider`, `metadata`, and generic Kubernetes boilerplate schemas, so that the resulting schema file stays small and reviewable.
7. As a platform engineer, I want the curated schema file structured as one schema per provider resource, forProvider-only, so that compose functions can import it the same way they'd import a hand-written schema file.
8. As a platform engineer, I want curation to preserve each field's required/optional status and docstring from the source CRD, so that I keep the typo-catching and documentation value of the original CRD without the noise.
9. As a platform engineer, I want curation to run as a standalone script I can invoke on a single CRD file, so that I can regenerate one provider's schema without re-running the whole pipeline.

**Phase 3 — Design composition schemas**

10. As a platform engineer, I want to hand-design each composite kind's XR spec schema (`StaticWebsiteSpec`, `IAMRoleSpec`, `LambdaFunctionSpec`, `DnsValidatedCertificateSpec`) from the consumer's perspective, so that the schema reflects what a consumer should be able to configure, not what the underlying providers happen to expose.
11. As a platform engineer, I want the nested types used by the XR specs (e.g. a bucket reference, a DNS zone, a lambda code location, a cert zone reference) hand-designed alongside the top-level specs, so that the schema stays internally consistent.
12. As a platform engineer, I want the composition schemas written as plain KCL schema definitions with no generated or templated content, so that they're easy to read, review, and evolve by hand.

**Phase 4 — Write & test transformation code**

13. As a platform engineer, I want each kind's transformation logic expressed as a pure `composeKind(oxr, ocds) -> [...]` function, so that it can be unit tested with `kcl test` without needing `option("params")` or a live runtime.
14. As a platform engineer, I want every `forProvider` payload and the XR's `spec` typed against the Phase 2/3 schemas inside each compose function, so that a typo or a structurally wrong payload fails fast, at test time, not at apply time.
15. As a platform engineer, I want any required field that depends on a possibly-absent observed value constructed inside the same conditional branch that gates whether the resource is emitted, so that cold-start or not-yet-observed states don't hard-fail against the schema's required-field check.
16. As a platform engineer, I want a `kcl test` suite per kind covering cold-start, partially-observed, and fully-observed scenarios, so that I have confidence the transformation behaves correctly across the resource's whole observation lifecycle.
17. As a platform engineer, I want every new `compose*.k` file to follow the house rules (no `option()` calls, union types over `any` for shared helpers, single-line type unions), so that known KCL footguns don't resurface.
18. As a platform engineer, I want any experimental or non-test `.k` file kept in its own subdirectory with no sibling `_test.k`, so that it can't accidentally break `kcl test ./...` for the whole directory.

**Phase 5 — Generate manifests**

19. As a platform engineer, I want an OpenAPI/JSON Schema normalizer that fixes `kcl doc generate --format openapi`'s known defects (`bool`→`boolean`, parsed and correctly-typed defaults, correct required/optional semantics for defaulted fields, fully inlined `$ref`s), so that the generated schema is actually valid for a Kubernetes XRD.
20. As a platform engineer, I want the Composition YAML/Jsonnet wrapper generated mechanically from each kind's compose function and schemas, so that I never hand-write or hand-sync the pipeline glue line, function references, or the auto-ready step.
21. As a platform engineer, I want the generator to enforce the `composeKind(oxr, ocds)` naming and signature convention at generation time, so that a violation is caught immediately rather than silently producing a broken Composition.
22. As a platform engineer, I want the generator's known gap around nested-XR composed resources (a resource emitted typed against another kind's own composition schema, not a flat provider schema) tracked as an explicit requirement, so that it isn't silently assumed away when the generator is built.
23. As a platform engineer, I want a render-only smoke test for each kind's generated Composition, running `crossplane render` and asserting it succeeds, so that I immediately know if a generated manifest is structurally broken, without yet having to write behavior assertions against the rendered output.

**Cross-cutting**

24. As a platform engineer, I want each phase's tooling (CRD pull, curation, normalizer, generator) to run independently, so that I can regenerate one stage without re-running the whole pipeline.
25. As a platform engineer, I want the five phases scoped as five separate stories, so that each can be built, reviewed, and merged independently.
26. As a platform engineer, I want the pipeline proven against the same four composite kinds already scoped (`StaticWebsite`, `IAMRole`, `LambdaFunction`, `DnsValidatedCertificate`), so that the first implementation exercises the hardest known case — a nested XR, multiple provider resources per kind — rather than a toy example.

## Implementation Decisions

- Five separate stories, one per phase, built from scratch in this repo — no code ported from prior exploratory work (see ADR 0001).
- **Phase 1**: a thin wrapper invoking `crossplane xpkg get-crds` against the platform's provider manifests (see ADR 0002), triggered manually/offline, writing CRDs to disk organized by `<group>/<version>/<kind>.yaml`.
- **Phase 2**: a Python script (managed with `uv`). Input: a raw CRD file. Output: a `schemas_providers.k`-shaped file containing only the `SpecForProvider` schema and its transitively-required nested types, preserving required/optional markers and field docstrings, discarding `status`/`metadata`/generic k8s schemas.
- **Phase 3**: hand-authored KCL schema files — one XR spec schema per composite kind, plus small nested types. No generation involved.
- **Phase 4**: hand-authored `compose*.k` files, one `composeKind(oxr, ocds) -> [...]` function per kind, typed against the Phase 2 and Phase 3 schemas. House rules apply: never call `option(...)` inside a `compose*.k` file; construct any schema-typed payload with a required-but-possibly-absent field inside the same branch that gates emission; write `type` union aliases on one line; prefer a named union type over `any` for a shared helper's parameter; keep experimental/non-test `.k` files in their own subdirectory with no sibling `_test.k`.
- The `composeKind(oxr, ocds)` naming and signature convention is a **documented hard rule** as of this spec. A linter or generator-level check enforcing it is a nice-to-have, not required.
- The Phase 5 generator's handling of nested-XR composed resources is an explicit, recorded requirement for that story — its concrete design is deferred to implementation time, not decided in this spec.
- **Phase 5**: a Python script (managed with `uv`) that normalizes `kcl doc generate --format openapi` output (fixing the `bool` type keyword, raw-text defaults, required-field semantics for defaulted fields, and the `$ref` scheme), plus a generator that produces the Composition YAML/Jsonnet wrapper and XRD OpenAPI schema from the Phase 3/4 artifacts.

## Testing Decisions

- A good test here asserts externally observable behaviour — resource lists emitted, files written, exit codes, generated manifest structure — never a script's or a compose function's internal locals.
- **Phase 1** wrapper: tested by invoking it against a real provider manifest and asserting the expected CRD files land on disk with non-empty `forProvider` fields.
- **Phase 2** curation script and **Phase 5** normalizer/generator: pure Python functions, tested with pytest using fixture inputs and asserted fixture outputs. No mocking needed — I/O stays at the thin CLI entrypoint, which isn't unit tested beyond the integration-level check above.
- **Phase 3/4**: `kcl test` per kind, covering at minimum a cold-start scenario, a partially-observed scenario, and a fully-observed scenario for any resource with conditional emission logic. This is the domain's established seam for compose-function correctness.
- **Phase 5** generator output: one `crossplane render` smoke test per kind, asserting only that render succeeds — no assertions against the rendered manifest's contents yet.
- No equivalence/comparison testing across authoring methods — this pipeline is the only method being built; that question is already settled.

## Out of Scope

- Porting or reviewing any code, tests, or tooling from prior exploratory work — this is a from-scratch build (ADR 0001).
- Behavior assertions against `crossplane render` output (specific fields/values in the rendered manifest) — only successful rendering is checked for now.
- A linter or generator-level check enforcing the `composeKind(oxr, ocds)` naming convention — documented as a hard rule only.
- Concrete design of how the Phase 5 generator handles nested-XR composed resources — recorded as a known requirement, not designed here.
- Any new composite kinds beyond the four already scoped.
- CI automation of the Phase 1 CRD pull — it's a manually-triggered, offline step for now.
- Setting up a live Crossplane control plane / cluster for end-to-end deployment testing.

## Further Notes

- This spec covers all five phases as one epic; expect it to be broken into five separate tickets, one per phase.
- `GLOSSARY.md` (`XR`, `XRD`, `MR`, `oxr`, `ocds`) and two ADRs (build-from-scratch, CRD source via `xpkg`) already exist in this repo and should be treated as binding context for anyone implementing this spec.
- The specific defects fixed by Phase 5's normalizer, and the specific curation rules in Phase 2, were validated through prior exploratory work before this spec was written — correctness of the approach itself isn't an open question, only its implementation in this fresh codebase.
