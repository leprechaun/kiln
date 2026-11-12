# 01: Pull and curate provider schemas

**What to build:** A human-triggered, offline tool that pulls a provider's CRDs straight from its package and curates them into a `forProvider`-only KCL schema file — no live cluster or credentials needed, results saved to disk as plain files.

**Blocked by:** None (can start immediately)

**Status:** done

- [x] Running the CRD-pull wrapper against a provider manifest (e.g. `provider-aws-s3`) writes CRD files organized by `<group>/<version>/<kind>.yaml`, with no live cluster or credentials required
- [x] Running the curation script against a pulled CRD produces a `schemas_providers.k`-shaped file containing only the `SpecForProvider` schema and its transitively-required nested types
- [x] The curated schema preserves required/optional markers and field docstrings from the source CRD
- [x] `status.atProvider`, `metadata`, and generic Kubernetes boilerplate schemas are discarded from the curated output
- [x] The curation script can be invoked standalone on a single CRD file without re-running the rest of the pipeline
- [x] pytest unit tests cover the curation script's pure function(s) with fixture CRD inputs and asserted curated outputs
- [x] Proven against the real `Bucket` resource (`s3.aws.m.upbound.io`), matching the fields already validated manually

**Implementation notes:** `make pull-crds` wraps `crossplane xpkg get-crds` against `manifests/crossplane-providers/` (all six providers this platform needs: s3, iam, lambda, acm, cloudfront, route53), writing to `crds/`. All six are also pre-cached in `~/.crossplane/cache` (confirmed: a full re-pull took 0.6s, so later tickets don't need network access). The curation logic lives in `tooling/src/tooling/curate.py` (`curate_provider_schema`, exposed as the `curate-provider-schema` CLI script), covered by `tooling/tests/test_curate.py`.
