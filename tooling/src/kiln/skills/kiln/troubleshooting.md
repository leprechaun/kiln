# Troubleshooting

Find the message or symptom you got. KCL syntax and compile errors are in the `kcl-primer` skill; live-cluster
checks are in the `crossplane-intro` skill.

| Message or symptom | Where it shows | Cause | Fix |
|--------------------|----------------|-------|-----|
| `cannot apply cluster scoped composed resource ... for a namespaced composite resource` | cluster; `kiln render` | A namespaced XR composes a legacy (non-`.m.`) provider group | Use the `.m.` group and import its CRD ([`provider-schemas.md`](provider-schemas.md)) |
| `... is cluster-scoped, but this project's XRs are namespaced` | `kiln import` | You imported a legacy CRD | Import the `.m.` file the warning names |
| `field not declared in schema` | cluster; `kiln render` | A shape copied from the legacy API or from memory, often in a resource built as a plain dict | Build `forProvider` through its imported schema ([`composing.md`](composing.md)) |
| `expected object, got array` / `expected string, got object` | `kiln render` | A one-item list where the `.m.` API takes an object; a policy given as an object | Use an object; `json.encode(...)` the policy |
| `required field is missing` / `required parameter is missing` | `kiln render` | A required provider parameter such as `region` is not set | Set it in `forProvider` (or `initProvider`) |
| `no CRD or XRD for <apiVersion> <Kind>` | `kiln render` | A wrong `apiVersion`, a provider not pulled, or a child kind not generated | Fix the `apiVersion`, `kiln pull-crds`, or `kiln generate` the child |
| `metadata.annotations: Too long: may not be more than 262144 bytes` | `kubectl apply` | The Composition is too big for client-side apply | "Composition size" in [`provider-schemas.md`](provider-schemas.md) |
| A managed resource with no status and no events at all | cluster | Its provider config does not exist (default `ClusterProviderConfig/default`) | Set `providerConfig` ([`configuration.md`](configuration.md)) |
| `an empty namespace may not be set when a resource name is provided` | cluster | The cluster's XRD still has the old scope | `kubectl get xrd <name> -o jsonpath='{.spec.scope}'`; see "XR scope" in [`configuration.md`](configuration.md) |
| `expected str, got {str:str}` inside a resource dict | `kcl test` | `spec.<y>` inside a dict with its own `spec.<x>` reads that dict's `spec` | Bind XR values to locals first (`kcl-primer`) |
| A dependent resource appears ~10 minutes late | cluster | It waits on a `status.atProvider` value that lags until the next poll | Gate on a Ready condition (`crossplane-intro`) |
| Passes `kcl test`, render fails to compile | `kiln render` | A cross-file import, or stale generated files | [`composing.md`](composing.md); run `kiln generate-all` |
| `the installed Kiln skills are out of date` | `kiln generate`, `kiln render` | Kiln was upgraded but the project's skills were not; their guidance may contradict what kiln does | `kiln install-skills --force`, then reread the skill |
| `... ends in [str]: any, which is no longer needed` | `kiln generate` | An index signature left on a spec schema from older Kiln docs | Remove it; spec schemas are closed |
