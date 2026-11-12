# Known gaps and guardrails

Written after tickets 01–06 all shipped with passing `kcl test` suites that still
hid real bugs — every ticket from 03 onward had at least one bug that `kcl test`
missed entirely and only `crossplane composition render` caught. This document
exists so that pattern doesn't get rediscovered from scratch on the next ticket.

## Gaps `kcl test` structurally cannot see

1. **Multi-file → single-string flattening correctness.** `kcl test` runs
   `kcl-scripts/` as a real multi-file package with working `import .x`
   statements. `function-kcl`'s runtime only ever accepts one flattened source
   string — a form `kcl test` never exercises. The dangling
   `schemas_compositions.` prefix bug (ticket 03) was invisible to every
   passing `kcl test` run.

2. **Real control-plane-injected fields.** A hand-written fixture only
   contains what its author remembered to put in it. Every real XR carries
   extra runtime metadata (Crossplane v2's `spec.crossplane`) that no fixture
   had until we added it on purpose. A closed schema passed every `kcl test`
   and still broke render immediately (tickets 02/03).

3. **Anything about the generated XRD/OpenAPI schema.** `kcl test` never
   calls `kcl doc generate`. The entire defect class the normalizer exists
   for — `bool`→`boolean`, raw-KCL-literal defaults, required-with-a-default,
   dangling `$ref`s, plus two more found only by inspection (stray defaults
   below the top level, the `additionalProperties` leak from `[str]: any`) —
   is completely outside what `kcl test` touches.

4. **Real `function-kcl`/`function-auto-ready`/reconciler mechanics.** The
   actual shape of `ocds["name"].Resource.status...`, how `auto-ready` labels
   resources, how `resourceRefs` populate, whether a nested XR is treated as
   "just another composed resource" — none of this exists in pure KCL
   evaluation. It's Go code we don't control and can't unit test in KCL.

## Risks still open even after today's render checks

5. **Never touched a real cluster or AWS account.** Render proves the
   pipeline *logic* is correct; it proves nothing about whether the provider
   accepts these exact field combinations, or whether a real Kubernetes API
   server accepts our XRD. We fixed the wrong `additionalProperties: {type:
   object}` artifact, but never confirmed whether a genuinely open schema
   needs Kubernetes' own `x-kubernetes-preserve-unknown-fields: true` instead
   — those aren't the same thing, and we don't know which one Crossplane
   actually needs.

6. **Never chained a nested XR's output into its own Composition's render.**
   We rendered `StaticWebsite` and `DnsValidatedCertificate` independently,
   each with a hand-written `xr.yaml`. We never verified that what
   `StaticWebsite` actually emits as a nested cert instance is valid input
   when Crossplane reconciles *that* instance for real.

7. **The SAN bug — `domainValidationOptions[0]` only, a real latent bug.**
   `DnsValidatedCertificateSpec` has an optional `subjectAlternativeNames?:
   [str]` field (additional domain names a cert should cover beyond
   `domainName`). When ACM validates a certificate via DNS, it must prove
   ownership of *every* domain on the cert, and each domain gets its own
   distinct validation record (its own `resourceRecordName` /
   `resourceRecordType` / `resourceRecordValue`). So
   `status.atProvider.domainValidationOptions` is an array with **one entry
   per domain on the cert**, not one entry total.

   In `kcl-scripts/dnsvalidatedcertificate.k`:

   ```kcl
   _validationOptions = ocds["certificate"]?.Resource?.status?.atProvider?.domainValidationOptions
   _validationOption = _validationOptions[0] if _validationOptions else None
   ```

   This only ever looks at index `0`. The `Record` built a few lines down and
   the `validationRecordFqdns` passed to `CertificateValidation` are both
   built from that single entry.

   **Concrete failure:** request a cert for `domainName = "example.com"` with
   `subjectAlternativeNames = ["www.example.com"]`. ACM returns two
   validation options, one per domain. The code creates a DNS record for
   whichever is at index 0 and silently ignores the other. That domain's
   validation record never gets created, so ACM can never finish validating
   it — the certificate sits permanently stuck in `PENDING_VALIDATION` for
   that SAN. `CertificateValidation.validationRecordFqdns` only lists one of
   the two FQDNs AWS requires, so validation never completes at all.

   Never caught because every test (`kcl test` fixtures and the real render)
   only ever used a bare `domainName`, never `subjectAlternativeNames` — so
   `domainValidationOptions` was always a single-entry array, and `[0]` was
   always "the only one."

   **Fix shape:** loop over every entry in `_validationOptions`, emit one
   `Record` per domain (each needs its own `composition-resource-name`,
   e.g. `validation-record-0`, `validation-record-1`, ...), and collect every
   entry's `resourceRecordName` into `validationRecordFqdns` rather than a
   single-element list. Not yet fixed — this file is the record of it until
   it is.

8. **Untested intermediate shapes in the `?.` safe-navigation chains.** We
   tried "key absent," "status present but empty," and "fully populated" —
   not every shape in between (e.g. `ocds` key present but `.Resource`
   missing entirely; `.Resource` present but no `.status` key at all).

9. **`enableFunctionUrl: false` explicit vs. absent** — only tested absent.

10. **No idempotency / ordering assumptions verified.** We assumed AWS
    populates `arn` before `domainValidationOptions`, encoded that as two
    separate gates — but never checked against reality that this is the
    actual order, or that re-rendering with evolving observed state converges
    correctly.

## Guardrails to adopt going forward

- **Treat `kcl test` as necessary, not sufficient.** Every ticket from 03 on
  had a 100%-green `kcl test` suite hiding a real bug. The render smoke test
  is load-bearing, not a formality — don't skip it to save time.
- **Don't trust a fixture just because you wrote it.** Every field-name
  mistake avoided (`$type`, `s3OriginConfig` shape, `domainValidationOptions`
  structure) came from checking the real curated schema first, not from
  assuming. A fixture encodes the author's mental model, which can be wrong
  in a way that's internally consistent and still passes.
- **`kcl-scripts/` is one shared compiled package.** A name collision
  anywhere (test function names, leading-underscore locals) breaks
  everything, confusingly. This bit us twice already (tickets 04, 05).
  Kind-prefix every top-level test name and local — nothing enforces this
  automatically.
- **The curation tool's docstring-prose heuristic is fixed for the failure
  mode found (ticket 04's `Function` false-positive), not provably airtight.**
  It still works by "does this name appear as a whole word in the kept
  schema's body" — a future provider resource could still trip it in a new
  way (e.g. a field name coincidentally matching another schema's name).
- **There's no automated fallback if Docker/registry access is ever
  unavailable.** The render tests are the only thing proving the generated
  source is even valid; there's no cheaper `kcl vet`-only check in the suite
  as a fallback sanity check.
