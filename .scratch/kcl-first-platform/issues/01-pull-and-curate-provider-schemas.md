# 01: Pull and curate provider schemas

**What to build:** A human-triggered, offline tool that pulls a provider's CRDs straight from its package and curates them into a `forProvider`-only KCL schema file — no live cluster or credentials needed, results saved to disk as plain files.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] Running the CRD-pull wrapper against a provider manifest (e.g. `provider-aws-s3`) writes CRD files organized by `<group>/<version>/<kind>.yaml`, with no live cluster or credentials required
- [ ] Running the curation script against a pulled CRD produces a `schemas_providers.k`-shaped file containing only the `SpecForProvider` schema and its transitively-required nested types
- [ ] The curated schema preserves required/optional markers and field docstrings from the source CRD
- [ ] `status.atProvider`, `metadata`, and generic Kubernetes boilerplate schemas are discarded from the curated output
- [ ] The curation script can be invoked standalone on a single CRD file without re-running the rest of the pipeline
- [ ] pytest unit tests cover the curation script's pure function(s) with fixture CRD inputs and asserted curated outputs
- [ ] Proven against the real `Bucket` resource (`s3.aws.m.upbound.io`), matching the fields already validated manually
