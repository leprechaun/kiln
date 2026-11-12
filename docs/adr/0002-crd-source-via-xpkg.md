# Source provider CRDs via `crossplane xpkg get-crds`

Phase 1 needs a repeatable, non-interactive way to get provider CRDs, with no live cluster or credentials in the loop. We verified `crossplane xpkg get-crds` pulls directly from a provider's OCI package and produces output identical to a live-cluster CRD pull, using only the `crossplane` CLI already in our toolchain. This beats pulling from a live, version-pinned cluster (requires cluster access and credentials that can expire mid-session) and `kcl import -m terraformschema` (untried, one hop further removed from the real source).
