# KCL-First Platform

Domain vocabulary for the Crossplane/KCL composition platform being redesigned in `cia-infra-test` — spans the Kubernetes-native resource model (XR/XRD/MR) and the KCL composition-function calling convention (`oxr`/`ocds`).

## Language

**XR**:
A Composite Resource: the Kubernetes object a platform consumer creates (e.g. a `StaticWebsite`). Carries `spec` (consumer input) and `status` (what the composition has observed or persisted).

**XRD**:
A CompositeResourceDefinition: the OpenAPI schema and CRD generator that defines an XR kind.

**MR**:
A Managed Resource: one real cloud object (e.g. a `Bucket`), reconciled continuously by a provider controller. Carries `spec.forProvider` (desired state) and `status.atProvider` (observed state).
_Avoid_: resource, cloud resource

**oxr**:
The observed XR passed into a composition function — its current `spec` plus `status`.

**ocds**:
Observed composed resources: a map, keyed by each resource's `composition-resource-name` annotation, of its current observed state.
