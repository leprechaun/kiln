# 05: DnsValidatedCertificate — full pipeline, schema through rendered manifest

**What to build:** `DnsValidatedCertificateSpec`, `composeDnsValidatedCertificate`, a generated manifest, and a passing render smoke test — a full vertical slice reusing the tooling proven in tickets 01 and 03. Independent of ticket 04.

**Blocked by:** 01, 03

**Status:** ready-for-agent

- [ ] `DnsValidatedCertificateSpec` (and nested types such as a cert zone reference) is designed from the consumer's perspective
- [ ] `composeDnsValidatedCertificate(oxr, ocds) -> [...]` follows the same house rules as ticket 02
- [ ] `kcl test` passes for `composeDnsValidatedCertificate`, covering cold-start, partially-observed, and fully-observed scenarios
- [ ] The generator produces this kind's Composition YAML/Jsonnet wrapper and XRD schema using the tooling built in ticket 03, with no new generator code needed
- [ ] `crossplane render` succeeds against the generated DnsValidatedCertificate Composition
