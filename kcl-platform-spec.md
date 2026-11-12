# KCL-first platform: handover spec

**Status:** exploratory spike, not a committed plan. Written to hand off to a fresh
session for story breakdown. Everything described as "proven" below was run
against the real `kcl` binary (v0.12.3) in this repo, and in one case against a
real live CRD pulled from the `cia-test` EKS cluster — not reasoned about in the
abstract. Everything described as "unresolved" is a genuine open question, not
false modesty.

## 0. The premise

This repo (`cia-infra-test`) exists to compare six ways of writing Crossplane
Composition logic for the same three composite kinds (`StaticWebsite`,
`IAMRole`, `LambdaFunction`, plus a nested `DnsValidatedCertificate`). See
`MEMORY.md` / prior session notes: the verdict already leaned toward
`externalized-kcl` (pure `composeX(oxr, ocds)` KCL functions, `kcl test`-able
with no Docker, spliced into the real Composition via Jsonnet).

This document is about going one step further: **not just "use KCL for the
transformation logic," but restructure the whole authoring pipeline around
KCL**, so that AWS provider shapes, composition input/output schemas, the
transformation logic, and the final Kubernetes manifests are as mechanically
connected as possible — minimizing the surface area a platform engineer has to
hand-maintain to roughly: the composition schema design, and the transformation
logic. Everything else becomes generated.

## 1. The five phases

Originally proposed as four; split into five per this session's decision to
decouple *where a provider schema comes from* from *turning it into KCL*,
since those are genuinely different problems with different risk profiles.

| # | Phase | Input | Output | Who owns it |
|---|-------|-------|--------|-------------|
| 1 | **Source provider schemas** | A real AWS provider (Upbound) resource — e.g. `Bucket` | A raw CRD/OpenAPI document for that resource | Mechanical, but **the source is an open question** (see §4.1) |
| 2 | **Generate + curate KCL provider schemas** | Phase 1's raw CRD/OpenAPI doc | A small, curated `schemas_providers.k`-style file (just `forProvider`, not `status`) | Mechanical tool (`kcl import -m crd`) + a **curation step we have not built** |
| 3 | **Design composition schemas** | Nothing (human judgment) | `schemas_compositions.k`-style files — the XR's `spec`, designed from the consumer's perspective | **100% hand-authored.** This is the actual design work. |
| 4 | **Write & test transformation code** | Phase 2 + Phase 3 schemas | `compose*.k` functions (`composeStaticWebsite(oxr, ocds) -> [...]`), proven via `kcl test` | **Hand-authored business logic.** Irreducible. |
| 5 | **Generate manifests** | Phase 3/4 schemas + the `compose*.k` function | The Composition YAML/Jsonnet wrapper, and the XRD's OpenAPI schema | Mechanical tool (`kcl doc generate --format openapi`) + a **normalizer we have not built** |

Phases 1–2 and 5 each have a real tool behind them (confirmed working, see §3),
but each also has a confirmed gap that needs code we have not written yet.
Phases 3–4 are permanently manual, and that's fine — that's where the actual
platform-design value lives.

## 2. What already exists in this repo, uncommitted

All of the following is **working but uncommitted** (`git status` shows it as
modified/untracked). A fresh session should decide whether to keep, commit, or
discard it before starting story work — it was built as a working prototype
for phase 3/4, not reviewed as final.

- `kcl-scripts/schemas_compositions.k` (49 lines, new) — hand-written XR spec
  schemas: `StaticWebsiteSpec`, `IAMRoleSpec`, `LambdaFunctionSpec`,
  `DnsValidatedCertificateSpec`, plus small nested types (`BucketRef`, `Zone`,
  `LambdaCode`, `CertZoneRef`).
- `kcl-scripts/schemas_providers.k` (124 lines, new) — hand-written
  `forProvider` schemas for all 12 provider resources the four kinds build
  (`BucketForProvider`, `DistributionForProvider`, `RoleForProvider`,
  `FunctionForProvider`, etc.), plus a `type StaticWebsiteForProvider = A | B
  | ...` union used to type-check `staticwebsite.k`'s shared resource-builder
  helper.
- `kcl-scripts/staticwebsite.k`, `iamrole.k`, `lambdafunction.k`,
  `dnsvalidatedcertificate.k` (all modified) — each now imports both schema
  files, types its `spec` local from `schemas_compositions`, and types every
  `forProvider` payload it constructs from `schemas_providers`.
- `kcl-scripts/inline-demo/iamrole.k` (67 lines, new, isolated in its own
  subdirectory on purpose) — a **deliberately rejected alternative**: the same
  `IAMRole` logic rewritten without the lambda, calling `option("params")`
  directly, module-scope. Kept as a worked example of why we didn't go this
  route (see §3.4). Has no `_test.k` file, so it's inert to `kcl test ./...`.
- All 36 existing tests in `kcl-scripts/*_test.k` still pass unmodified —
  nothing in `tests/*_test.k` was touched, per explicit instruction this
  session.

## 3. Experiments run, with results and caveats

### 3.1 Schema-typing the existing `compose*.k` functions (phases 3+4 proof)

**What we did:** added `schemas_compositions.k` / `schemas_providers.k`, typed
`spec` and every `forProvider` local across all four `compose*.k` files, ran
`kcl test ./...` after every change.

**Result:** works, and caught two real things:

1. **Typo-catching, confirmed live.** Deliberately misspelling
   `spec.bucket.name` → `spec.buckett.name` produces
   `attribute 'buckett' not found in 'StaticWebsiteSpec', did you mean
   '["bucket"]'?` — through the real `kcl test` command, not a toy example.
2. **A real latent bug, surfaced by adding types.** `staticwebsite.k`'s
   `distributionForProvider` and `domainAliasRecordForProvider`, and
   `lambdafunction.k`'s `FunctionForProvider`, were all originally built
   *unconditionally*, with the actual `[resource] if hasX else []` gate only
   wrapping the emission, not the construction. With loose `{str:any}` dicts
   this was harmless (a stray `None` just sits there unused). Once those
   fields became **required** on a schema, constructing them while the
   gating field was still `None` (cold start, or a zone set but not yet
   resolved) hard-failed with `attribute '...' is required and can't be None
   or Undefined`. **Fix:** move the schema-typed construction *inside* the
   same branch that gates emission. This is now a load-bearing convention,
   not a one-off fix — see §5.

**Caveats found along the way (real KCL mechanics, not opinions):**

- A value typed as a schema instance is **not** assignable to a parameter
  typed `{str:any}`. Loosening to `any` fixes it, and loses nothing, since
  the real type-check already happened at construction. A union type
  (`A | B | C`) also works as a parameter type and is strictly better than
  `any`: I proved it rejects an unrelated raw dict at the call boundary
  (`Cannot add member 'totallyWrong' to 'schemas [...]'`), which `any`
  does not.
- **`type X = A | B | C` union aliases must be on one line.** The natural
  multi-line, leading-`|`-per-line style either silently truncates to just
  the first member or throws `InvalidSyntax`, depending on context. Hit this
  for real in `schemas_providers.k`'s `StaticWebsiteForProvider` alias.
- Ternary branches (`[x] if cond else []`) are lazily skipped for any
  expression that depends on a runtime value (a function call with a
  variable argument, a schema instantiation referencing a possibly-`None`
  field) — confirmed via direct probes. But a **fully constant, zero-argument
  expression** (e.g. a no-arg lambda call with no free variables) gets
  evaluated regardless of which branch is "selected," because KCL appears to
  constant-fold it at compile time. This asymmetry is subtle and is exactly
  what caused bug #2 above.

### 3.2 Generating OpenAPI/JSON Schema from KCL schemas (phase 5 proof, partial)

**What we did:** `kcl doc generate --format openapi` against
`schemas_compositions.k` / `schemas_providers.k` (needs a `kcl.mod` — neither
file currently has one; had to init one in a scratch copy).

**Result:** real, structurally mostly-correct output — correct `required`
list (respects KCL's `?` marker), correct `$ref`-based nesting, correct
`int` → `{"type": "integer", "format": "int64"}` mapping.

**Four confirmed defects, each with reproduced output:**

1. `bool` → emitted as `"type": "bool"`. Not a valid OpenAPI/JSON Schema
   type keyword (must be `"boolean"`); Kubernetes's CRD validator would
   reject it.
2. **Defaults are raw, unparsed KCL source text wrapped in a JSON string.**
   `priceClass: str = "PriceClass_100"` → `"default": "\"PriceClass_100\""`
   (literal embedded quotes). `flag: bool = True` → `"default": "True"` (the
   string `"True"`, not the JSON boolean `true`). Both would fail
   type-of-default validation as-is.
3. **A field with a default is still listed as `required`.** Only the `?`
   marker affects the `required` list; declaring a default does not make a
   field optional in the generated schema, which is backwards from normal
   CRD defaulting semantics.
4. **The `$ref` scheme is internally inconsistent, and the overall shape is
   wrong for a CRD regardless.** The document declares `"openapi": "3.0"`
   (which uses `#/components/schemas/X`) but every generated `$ref` points
   at `#/definitions/X` (Swagger 2.0's path) with no `definitions` object
   anywhere — every nested ref is dangling as generated. Separately and more
   fundamentally: Kubernetes CRDs/XRDs require fully self-contained
   ("structural") schemas with **no `$ref` at all** — even a correctly
   pathed `$ref` would need to be recursively inlined before Kubernetes
   would accept it.

**Verdict:** real capability, not usable as-is. Needs a normalizer: fix
`bool`→`boolean`, re-parse+retype defaults, decide the semantics of
defaulted-but-"required" fields, and recursively inline every `$ref` into one
self-contained schema per top-level type. Scoped at maybe a couple hundred
lines, not a rewrite — but it's infrastructure to build and own, not a
zero-cost command.

### 3.3 Generating KCL schemas from a real provider CRD (phase 1+2 proof)

**What we did:** `kubectl get crd buckets.s3.aws.m.upbound.io -o yaml` against
the live `cia-test` EKS cluster (the exact CRD `staticwebsite.k`'s `Bucket`
resource targets), then `kcl import -m crd` on the real output. (An earlier
attempt with a hand-built synthetic CRD YAML hit an unexplained
`cannot unmarshal array into ... JSONSchemaProps` error during incremental
isolation testing — never root-caused, and turned out not to matter, because
the **real** CRD imported cleanly on the first try. Don't waste time chasing
that synthetic repro; the real tool works against real input.)

**Result:** clean generation, and the part we actually care about is good:

```kcl
schema S3AwsmUpboundIoV1beta1BucketSpecForProvider:
    r"""
    ...
    bucketNamespace : str, optional
        Namespace for the bucket. Determines bucket naming scope...
    region : str, required
        Region where this resource will be managed...
    tags : {str:str}, optional
        Key-value map of resource tags.
    """
    bucketNamespace?: str
    forceDestroy?: bool
    objectLockEnabled?: bool
    region: str
    tags?: {str:str}
```

Correct required/optional split, correct types (including the `tags:
{str:str}` map), and real field-level docstrings pulled straight from the
CRD's `description` fields — better than our hand-written version (which
only modeled `region`, since that's all we use).

**The caveat, confirmed by counting:** the *full* import produced **34
schemas across 902 lines** for this one CRD. 27 of those 34 schemas model
`status.atProvider` — CORS rules, lifecycle rules, replication
configuration, server-side encryption, versioning, website config, grants —
plus generic `metadata`/`ObjectMeta`/`OwnerReference` boilerplate. We already
decided (earlier in this project) not to type the observed/`status` side at
all — it's externally owned, arbitrarily deep, and already handled safely via
`?.`. So the signal-to-noise ratio of a raw `kcl import -m crd` run is poor:
the 5-field `SpecForProvider` schema we want is buried in 29 schemas we don't.

**Verdict:** real capability, same shape of gap as phase 5 — needs a curation
step that keeps `spec.forProvider` (and any input types it transitively
needs) and discards `status`, `metadata`, and the generic k8s boilerplate,
per resource.

**Unresolved and genuinely open — where do the CRDs in phase 1 come from, in
an automated pipeline?** This spike pulled from a live cluster by hand, which
is not something CI can depend on. Options not yet evaluated:
- Extract CRDs directly from the provider's `xpkg` package (the Crossplane
  `Provider` package itself bundles its CRDs — this avoids needing a live
  cluster at all, and is probably the right answer, but hasn't been tried).
- `kcl import -m terraformschema` — Upbound's providers are themselves
  generated from Terraform provider schemas, so this might be a cleaner,
  one-step-removed source. Not tested.
- Continue pulling from a live cluster, pinned to a specific provider
  version. Simple but environment-dependent and was literally blocked by an
  expired SSO token mid-session today.

### 3.4 Why the lambda-based `compose*(oxr, ocds)` signature stays, not `option()` directly

Explored and explicitly rejected earlier this session, kept here because it's
load-bearing for phase 4's design and a fresh session might reasonably ask
"why not simplify further":

- `option("params")` is how Crossplane's `function-kcl` runtime injects
  `oxr`/`ocds` into a KCL program — but it's **only resolvable inside that
  runtime** (or via `kcl run -D params=...` / a `-Y` settings file by hand).
  A `.k` file calling it directly can't be unit tested with `kcl test` the
  way the current `compose*.k` files are.
- Confirmed directly: `kcl test` **does** have its own `-D`/`-Y` flags, so an
  `option()`-based file is technically runnable under `kcl test` — but `-D`
  binds **one value for the entire test invocation**. Every `test_*` function
  in that run shares the same injected `oxr`/`ocds`. Proved this breaks
  real coverage: added a third test wanting a "role not yet observed"
  scenario alongside two tests assuming "role observed," in the same `kcl
  test` run with one `-D` — the third test failed, not from a logic bug, but
  because there's structurally no way to give different test functions
  different injected values in one invocation.
- Consequence: dropping the lambda would mean replacing `kcl test`'s native
  per-test scenario/assert/report loop with a **hand-rolled harness** — a
  script that shells out to `kcl run -D ...` once per scenario and parses the
  output itself, essentially reimplementing `kcl test` badly, in a second
  language, alongside `tests/harness.py` (which already does the equivalent
  for the other five methods via `crossplane composition render`). Not worth
  it. **Keep `compose*(oxr, ocds)` as the permanent shape of every
  transformation function.**
- Related, confirmed hazard: `kcl test` compiles **an entire directory** as
  one package, evaluating every top-level statement in every `.k` file in it
  — even ones nothing imports. Dropping an `option()`-calling file directly
  into `kcl-scripts/` (instead of its own subdirectory) made `option("params")`
  resolve to `None` and failed **all 36 existing tests**, not just something
  related to the new file. This is why `inline-demo/iamrole.k` lives in its
  own subdirectory with no `_test.k` beside it.

## 4. Open risks and decisions a fresh session needs to make

1. **§3.3's unresolved question: where do source CRDs/schemas come from in
   an automated pipeline?** Needs a decision before phase 1 can be a real,
   repeatable story rather than a manual spike.
2. **The phase 2 and phase 5 "curation"/"normalizer" steps don't exist yet.**
   Both are scoped (see §3.2, §3.3) but unwritten. Each is probably its own
   story.
3. **The phase 5 generator depends on a rigid naming convention holding
   across every kind** — every transformation must be named `composeX`,
   take exactly `(oxr, ocds)`, and live in a file the generator can find.
   `kcl test` cannot catch a violation of this convention (it only validates
   the `.k` file in isolation, never the glued-together Jsonnet + `option()`
   call) — only the full render-based `tests/equivalence/` suite would. This
   needs to be written down as a hard rule for anyone authoring a new
   `compose*.k`, possibly enforced by a linter/generator check rather than
   trusted to memory.
4. **Nested-XR composition isn't a flat case for the generator.**
   `staticwebsite.k` builds a `DnsValidatedCertificate` instance typed
   against *that kind's own* composition schema, not a provider schema. Any
   phase-5 generator needs to understand "this transformation emits an
   instance of another kind's schema" as a real case, not assume every
   emitted resource is either the current kind's own spec or a flat AWS
   provider object.
5. **Today's prototype (§2) is uncommitted.** Decide whether it's the
   starting point for phase 3/4 stories, or whether it gets reviewed/redone
   from scratch.

## 5. House rules for anyone writing a `compose*.k` going forward

These aren't style preferences — each one is here because violating it
produces a real, confirmed failure mode above:

- Never call `option(...)` inside a `compose*.k` file. Take `oxr`/`ocds` as
  ordinary lambda parameters. (§3.4)
- When a `forProvider` (or any schema-typed) payload has a required field
  that depends on a possibly-absent status value, **construct it inside the
  same `if`/`else` branch that gates whether the resource is emitted at
  all** — never hoist it above the gate "for readability." (§3.1, bug #2)
- Keep any experimental/non-test `.k` file that might error without external
  input (e.g. anything calling `option()`) in its own subdirectory with no
  sibling `_test.k` — never loose in a directory `kcl test` already covers.
  (§3.4)
- Write `type` union aliases on a single line.
- Prefer a named union type over `any` for a shared helper's "accepts one of
  several schemas" parameter — it's strictly more protective and costs
  nothing. (§3.1)

## 6. Suggested story breakdown

Roughly one story per phase, plus the two known "build the missing tool"
gaps as their own stories since they're the riskiest/least-scoped pieces:

1. **Phase 1 — Decide and implement a source for provider CRDs/schemas.**
   Resolve §4.1. Output: a repeatable, non-interactive way to get a provider
   resource's raw schema (CRD YAML or Terraform schema) into the repo or CI.
2. **Phase 2 — Build the CRD→KCL curation step.** Wrap `kcl import -m crd`
   with an extractor that keeps only `spec.forProvider` (+ transitively
   needed nested types) per resource, discards `status`/`metadata`/k8s
   boilerplate, and writes it into a `schemas_providers.k`-shaped file.
3. **Phase 3 — Design composition schemas for the remaining kinds (or
   redo the four already prototyped).** Pure design work; decide whether to
   keep this session's `schemas_compositions.k` as a starting draft.
4. **Phase 4 — Migrate/finish `compose*.k` transformations to the typed
   convention**, applying §5's house rules. Largely done for the four
   existing kinds in this session's uncommitted work — mostly a review/commit
   decision, not new work, unless kinds are added.
5. **Phase 5 — Build the KCL→OpenAPI normalizer and the Composition-YAML
   generator.** Two sub-pieces: (a) fix `kcl doc generate --format openapi`'s
   four defects (§3.2); (b) generate the Jsonnet/YAML wrapper (`functionRef:
   function-kcl`, `importstr`, the `option(...)` glue line, the `auto-ready`
   step) from convention, per §4.3's naming-convention risk.

## 7. Glossary (for a fresh session or a human unfamiliar with this repo)

- **XR** — Composite Resource: the Kubernetes object a platform consumer
  creates (e.g. a `StaticWebsite`). Has `spec` (consumer input) and `status`
  (what the composition has observed/persisted).
- **XRD** — CompositeResourceDefinition: the schema (OpenAPI) + CRD generator
  for an XR kind.
- **MR** — Managed Resource: one real cloud object (e.g. a `Bucket`),
  reconciled forever by a provider controller. Has `spec.forProvider`
  (desired) and `status.atProvider` (observed).
- **`oxr`** — the *observed* XR passed into a composition function: its
  current `spec` + `status`.
- **`ocds`** — observed composed resources: a map, keyed by each resource's
  `krm.kcl.dev/composition-resource-name` annotation, of its current
  observed state (`ocds["bucket"].Resource.status.atProvider...`).
- **`function-kcl`** — the Crossplane Composition Function that runs KCL
  source as a pipeline step, and is the thing that actually binds
  `option("params")` to `{oxr, ocds}` at runtime.
- **Composition pipeline step glue line** — the one line (`items =
  composeX(option("params").oxr, option("params").ocds)`) that the Jsonnet
  wrapper appends after `importstr`-ing a pure `.k` file in, bridging the
  testable pure function to the live runtime's calling convention.
