# 05: DnsValidatedCertificate — full pipeline, schema through rendered manifest

**What to build:** `DnsValidatedCertificateSpec`, `composeDnsValidatedCertificate`, a generated manifest, and a passing render smoke test — a full vertical slice reusing the tooling proven in tickets 01 and 03. Independent of ticket 04.

**Blocked by:** 01, 03

**Status:** done

- [x] `DnsValidatedCertificateSpec` is designed from the consumer's perspective (domain name, region, an existing Route53 zone ID), and includes `[str]: any` so it stays open to the `spec.crossplane` metadata a real XR carries
- [x] `composeDnsValidatedCertificate(oxr, ocds) -> [...]` follows the same house rules as ticket 02
- [x] `kcl test` passes for `composeDnsValidatedCertificate` (4/4), with a genuinely three-stage observed-state progression — the richest case of the four kinds so far
- [x] The generator produces this kind's Composition YAML and XRD schema using the tooling built in ticket 03, with no new generator code needed
- [x] `crossplane composition render` succeeds against the generated DnsValidatedCertificate Composition (automated in `tests/integration/test_render_dnsvalidatedcertificate.py`), verified both cold-start and fully-observed via `--observed-resources`

**Findings:**

1. **The real three-resource DNS validation chain, modeled faithfully:** `Certificate` is always requested. Once its `status.atProvider.arn` is observed, `status.certificateArn` is surfaced onto the XR. Independently, once `status.atProvider.domainValidationOptions` is observed (a separate condition — `arn` and `domainValidationOptions` become available at different times), a Route53 `Record` is created with the exact validation record Values AWS asked for, and a `CertificateValidation` resource is created to wait for the record to resolve. This is the first kind where a required field (the Record's `name`/`type`/`records`) *genuinely* depends on a possibly-absent observed value — ticket 02 (IAMRole) didn't have this, ticket 04 (LambdaFunction) had a milder version of it.
2. **`type` is a reserved word in KCL schemas** — `kcl import` escapes the Route53 Record's `type` field as `$type`. Found by checking the real curated schema rather than assuming the field name; serializes back to plain `type` in rendered YAML, so no leakage into the actual manifest.
3. **Two repeated KCL syntax mistakes, both caught immediately by `kcl test`:** (a) a type annotation on a dotted attribute path (`spec.forProvider: Type = {...}`) isn't valid — the schema-constructor form (`spec.forProvider = Type { ... }`) is required instead; (b) KCL doesn't support Python-style leading-operator line continuation (`\n    + expr`) — the expression has to stay on one line or bind to a local first.
4. **Another real naming collision**, same root cause as ticket 04: `kcl test .` compiles every file in `kcl-scripts/` as one package, so leading-underscore "private" top-level names (`_baseOxr`, `_baseSpec`) collided across `lambdafunction_test.k` and `dnsvalidatedcertificate_test.k` too. Renamed to kind-prefixed (`_functionBaseOxr`, `_certBaseOxr`, `_certBaseSpec`). This will keep recurring for ticket 06 — worth just always prefixing shared test constants by kind from the start.
