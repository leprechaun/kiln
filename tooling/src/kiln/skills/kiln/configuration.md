# Configuration

Every setting in `kiln.toml`.

## kiln.toml reference

| Key | Values | Default | What it does |
|-----|--------|---------|--------------|
| `group` | an API group | required | The API group of every XR (and XRD) the project defines |
| `format` | `"yaml"`, `"jsonnet"` | `"yaml"` | How the Composition is written; see "Output format" below |
| `scope` | `"Namespaced"`, `"Cluster"` | `"Namespaced"` | Each XRD's scope; see "XR scope" below |
| `providerConfig` | `{ kind = "...", name = "..." }` | none | The `providerConfigRef` given to composed managed resources that set none; see "Provider config" below |
| `[kinds.<Kind>]` | `scope`, `providerConfig` | the project values | Per-kind overrides of the two keys above |

```toml
group = "platform.example.com"
format = "yaml"
scope = "Namespaced"
providerConfig = { kind = "ClusterProviderConfig", name = "pod-identity" }

[kinds.ObjectStore]
scope = "Cluster"
providerConfig = { kind = "ProviderConfig", name = "team-a" }
```

A kind's setting beats the project's. Kind names match case-insensitively. `kiln init --scope` and
`kiln init --format` write the project values.

## XR scope

An XRD is `Namespaced` (the default) or `Cluster`. The choice follows what the function composes:

- A **Namespaced** XR can only compose resources in its own namespace. Use it with the namespaced
  provider groups (`s3.aws.m.upbound.io`, the `.m.` ones this guide recommends).
- A **Cluster** XR can compose cluster-scoped resources (the legacy non-`.m.` provider groups) as
  well as namespaced ones. When it composes a namespaced resource, set `metadata.namespace` on that
  resource explicitly.

An XRD's scope is **immutable** on the cluster. Changing it later means deleting the XRD (and every
XR of that kind) and applying the new one; `kiln generate` warns when the scope of an existing
`xrd.yaml` changes. `kiln generate <Kind> --scope Cluster` overrides `kiln.toml` for one run.

## Provider config

A managed resource without `spec.providerConfigRef` uses `ClusterProviderConfig/default`, and
fails silently if that does not exist (see the `crossplane-intro` skill). Set `providerConfig` to
the one your cluster has.

Generation then gives that `providerConfigRef` to every composed managed resource (anything with
`spec.forProvider` outside your own API group) that does not set one itself. The XR and child XRs
are left alone, and a ref your function sets wins. It is applied in the generated Composition, not
in your function, so `kcl test` does not see it; `kiln render` does. Without the setting, nothing is
added.

## Output format

By default the Composition is plain YAML with the KCL embedded in one `source:` string.
`format = "jsonnet"` is for a tool that evaluates jsonnet itself (ArgoCD does). Generation then
writes `composition.jsonnet` and `composition.k` instead of `composition.yaml`. The jsonnet file
holds the Composition with `"source": importstr 'composition.k'`; the `.k` file is the generated,
flattened KCL. `xrd.yaml` is unchanged. Deploy all three files from the directory. Both generated
files are output: do not edit them.

`kiln render` and `kiln render-all` work in both modes. In jsonnet mode they evaluate
`composition.jsonnet` with the `jsonnet` binary (go-jsonnet or C++ jsonnet, on your `PATH`) into a
temporary file and render that, so you render what you would deploy. Without `jsonnet` installed,
render fails; that is not a pass.
