# 02: IAMRole — design schema and compose function

**What to build:** `IAMRoleSpec` and `composeIAMRole(oxr, ocds)`, hand-authored and fully proven via `kcl test`, typed against the curated provider schemas from ticket 01. Chosen first because it's the simplest kind — no nested XR, fewest provider resources.

**Blocked by:** 01

**Status:** done

- [x] `IAMRoleSpec` (and any nested types it needs) is designed from the consumer's perspective, not mirroring provider shapes
- [x] `composeIAMRole(oxr, ocds) -> [...]` is a pure function taking `oxr`/`ocds` as ordinary lambda parameters, never calling `option(...)` internally
- [x] Every `forProvider` payload and the XR's `spec` are typed against the Phase 2 and Phase 3 schemas
- [x] N/A — no required field depends on a possibly-absent observed value for this kind (see note below)
- [x] `type` union aliases are written on a single line; a named union type is used instead of `any` for any shared helper's parameter — N/A, no union types needed (single resource type, no shared helper)
- [x] `kcl test` passes for `composeIAMRole` (4/4) — see note below on the cold-start/partial/full criterion
- [x] Any experimental or non-test `.k` file is kept in its own subdirectory with no sibling `_test.k` — N/A, no experimental file created

**Findings:**
- The real `Role` provider resource manages policy attachment directly via its own `managedPolicyArns` field (curated in ticket 01, including its nested `InlinePolicyItems0`/`ManagedPolicyArnsRefsItems0`/`ManagedPolicyArnsSelector` types) — no second, dependent resource is needed to attach policies, confirming the single-resource scope for this kind.
- Because of that, `composeIAMRole` is fully constructible from `oxr.spec` alone, with no dependency on `ocds` (observed state) at all. The cold-start/partially-observed/fully-observed test triad genuinely doesn't apply here — there's no conditional/gated construction to exercise. Tests instead cover: the trust-policy JSON is built correctly from `trustedService`, optional fields pass through when set, and optional fields are correctly absent when not set.
- `IAMRoleSpec` abstracts the raw AWS trust-policy JSON behind a single `trustedService` field (e.g. `"lambda.amazonaws.com"`), rather than exposing IAM policy-document shape to the consumer directly.
- **Retroactive fix (found in ticket 03):** `IAMRoleSpec` needed `[str]: any` added so it's an *open* schema. A real Crossplane XR's `oxr.spec` carries runtime-injected metadata (a `spec.crossplane` key) that a closed schema rejects as an unknown attribute — `kcl test`'s hand-built fixtures never exercised this, only a real `crossplane composition render` did. Added a `kcl test` case covering it. **Every future composition spec schema should include `[str]: any` by default**, not just this one.
