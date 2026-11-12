# 06: StaticWebsite — full pipeline, including nested-XR generator support

**What to build:** `StaticWebsiteSpec` (referencing `DnsValidatedCertificateSpec` for its nested cert instance), `composeStaticWebsite` (which emits a nested `DnsValidatedCertificate` instance among its resources), and the generator extended to handle a compose function emitting another kind's own schema instance. This is where the previously-deferred nested-XR requirement actually gets resolved.

**Blocked by:** 01, 03, 05 (needs `DnsValidatedCertificateSpec` to exist to type-check the nested instance it constructs)

**Status:** ready-for-agent

- [ ] `StaticWebsiteSpec` (and nested types such as a bucket reference and a DNS zone) is designed from the consumer's perspective, referencing `DnsValidatedCertificateSpec` for its nested certificate instance
- [ ] `composeStaticWebsite(oxr, ocds) -> [...]` follows the same house rules as ticket 02, and constructs a `DnsValidatedCertificate` instance typed against that kind's own composition schema as one of its emitted resources
- [ ] `kcl test` passes for `composeStaticWebsite`, covering cold-start, partially-observed, and fully-observed scenarios
- [ ] The generator correctly recognizes and handles the case where a compose function emits an instance of another kind's own composition schema, rather than assuming every emitted resource is either the current kind's own spec or a flat provider object
- [ ] `crossplane render` succeeds against the generated StaticWebsite Composition
