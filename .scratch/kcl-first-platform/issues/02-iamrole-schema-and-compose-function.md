# 02: IAMRole — design schema and compose function

**What to build:** `IAMRoleSpec` and `composeIAMRole(oxr, ocds)`, hand-authored and fully proven via `kcl test`, typed against the curated provider schemas from ticket 01. Chosen first because it's the simplest kind — no nested XR, fewest provider resources.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] `IAMRoleSpec` (and any nested types it needs) is designed from the consumer's perspective, not mirroring provider shapes
- [ ] `composeIAMRole(oxr, ocds) -> [...]` is a pure function taking `oxr`/`ocds` as ordinary lambda parameters, never calling `option(...)` internally
- [ ] Every `forProvider` payload and the XR's `spec` are typed against the Phase 2 and Phase 3 schemas
- [ ] Any required field depending on a possibly-absent observed value is constructed inside the same conditional branch that gates whether the resource is emitted
- [ ] `type` union aliases are written on a single line; a named union type is used instead of `any` for any shared helper's parameter
- [ ] `kcl test` passes for `composeIAMRole`, covering at minimum a cold-start scenario, a partially-observed scenario, and a fully-observed scenario
- [ ] Any experimental or non-test `.k` file is kept in its own subdirectory with no sibling `_test.k`
