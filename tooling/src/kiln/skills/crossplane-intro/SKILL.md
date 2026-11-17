---
name: crossplane-intro
description: >
  Crossplane concepts as Kiln uses them: XR, XRD, Composition, managed resources, ocds, and the
  reconcile lifecycle. Use when reasoning about how resources get created, or why a composed
  resource is stuck or missing.
---

# Crossplane, as Kiln uses it

| Term | Meaning | Where it lives |
|------|---------|----------------|
| **XR** | The composite resource a consumer creates; their API | `render-fixtures/<kind>/xr.yaml` (sample) |
| **XRD** | Schema for the XR; `scope` is `Namespaced` (can only compose resources in its own namespace) or `Cluster` (can also compose cluster-scoped resources) | generated: `manifests/crossplane-compositions/<kind>/xrd.yaml` |
| **Composition** | Maps an XR to managed resources via `function-kcl` | generated: `composition.yaml` (or `.jsonnet`) |
| **MR** | One real cloud object a provider manages | what `compose<Kind>` returns |
| **Provider** | Controller that reconciles MRs | `manifests/crossplane-providers/` |

Never edit the XRD or Composition by hand; they come from your KCL.

## The function

`compose<Kind> = lambda oxr, ocds -> [any]`

- `oxr`: the observed XR. `oxr.spec` is the consumer's input.
- `ocds`: composed resources observed so far, keyed by each resource's
  `krm.kcl.dev/composition-resource-name` annotation. Read provider output with
  `ocds["bucket"]?.Resource?.status?.atProvider?.arn`.
- It returns the desired resources. Returning the XR itself (same `apiVersion`/`kind`/`metadata`)
  with a `status` sets XR status.

## Lifecycle: why staging matters

Crossplane re-runs the function on every reconcile. On the first run `ocds` is empty, so anything
that needs another resource's output (an ARN, a domain name) cannot be built yet. Emit it on a
later run once the value is observed. That gives three stages worth testing: cold start, partly
observed, fully observed.

- A new MR is created, the provider reconciles, `status.atProvider` fills in, the next run sees it.
- `status.atProvider` can lag reality until the provider's next poll (around 10 minutes). Where a
  dependent resource exists to signal readiness, gate on its `Ready` condition instead: for
  example ACM `CertificateValidation` Ready, not `Certificate` `atProvider.status == "ISSUED"`:

  ```kcl
  _conditions = ocds[_validationName]?.Resource?.status?.conditions or []
  _validationReady = any_true([c.type == "Ready" and c.status == "True" for c in _conditions])
  ```
- Spec changes re-run the function and the desired resources are updated.
- Deleting the XR deletes its MRs (the default deletion policy).

## MR essentials

- `spec.forProvider` is what you want; `status.atProvider` is what exists.
- `crossplane.io/external-name` sets the cloud object's own name.
- Use the namespaced `.m.` API groups (for example `s3.aws.m.upbound.io`); take any field shape
  from the imported schema, not memory.
- Without `spec.providerConfigRef`, an MR uses `ClusterProviderConfig/default`. If that does not
  exist, the MR shows **no status and no events**: nothing points at the cause. Kiln can add the
  right ref for you ([`../kiln/configuration.md`](../kiln/configuration.md)).
- `function-auto-ready` marks the XR ready when all composed resources are.

## Debugging a live cluster

| Symptom | Check |
|---------|-------|
| Resource not created | Composition and XRD installed (`kubectl get composition,xrd`); provider healthy (`kubectl get providers`) |
| MR stuck | `kubectl describe <mr>`: read `status.conditions` for the provider's message |
| MR has no status and no events at all | `kubectl get clusterproviderconfig,providerconfig -A`: does the one it references exist? |
| An error message you do not recognise | [`../kiln/troubleshooting.md`](../kiln/troubleshooting.md) maps messages to causes |
| Status not updating | Is the XRD's `status` declared? Without `<Kind>Status` the API server may drop it |
| Resource appears late | Expected: it depends on an observed value; see Lifecycle |

Docs: https://docs.crossplane.io/ and https://marketplace.upbound.io/.
