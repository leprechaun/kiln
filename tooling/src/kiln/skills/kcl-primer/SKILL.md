---
name: kcl-primer
description: >
  KCL syntax for Kiln compose functions: dicts, schemas, lambdas, optional chaining, tests, and
  common compile errors. Use when writing KCL, or when kcl test / kiln render reports a syntax
  or type error.
---

# KCL primer

KCL is a configuration language (closer to HCL than Python). Full reference:
https://www.kcl-lang.io/docs/user_docs/guides/. For Kiln workflow and rules see the `kiln` skill.

## Syntax that trips people up

**Dicts and schema instances: newlines, no commas.**

```kcl
_bucket = {
    apiVersion = "s3.aws.m.upbound.io/v1beta1"
    metadata.annotations = {"krm.kcl.dev/composition-resource-name" = "bucket"}
}
```

- Both `key = value` and `key: value` are valid in a dict. They differ: `=` overrides on
  merge, `:` unions. Kiln code uses `=`. Dotted keys (`spec.forProvider = ...`) build nested dicts.
- A JSON one-liner with commas is valid, but a stray comma between multi-line entries is not.
- Locals starting with `_` are private and mutable; use them for intermediate values.
- **`type` is a keyword.** It cannot be a bare name (a local or a lambda parameter). As a key
  it is fine: read a dict's with `c["type"]`, and in a schema write the field as `$type` (the way
  `kcl import` does) and read it as `fp.$type`. It serialises back to `type`:

  ```kcl
  _conditionType = _condition["type"]

  schema PolicyRule:
      $type: str
  _rule = PolicyRule {$type = "Allow"}
  _ruleType = _rule.$type
  ```
- Type annotations are valid only on locals (`x: T = ...`), not on dotted paths or dict keys. Use the
  constructor form instead: `spec.forProvider = T { ... }`.
- **A line starting with `+` or `|` begins a new statement**, and fails to compile. To continue an
  expression, end the previous line with the operator and a `\`:

  ```kcl
  _all = _resources + \
      _more
  _withKind = _base | \
      {kind = "ConfigMap"}
  ```

  The operator alone at the end of a line is not enough, and wrapping the expression in
  parentheses does not help; both fail too.
- `type X = A | B` must be on one line.
- Interpolation: `"arn:aws:s3:::${bucketName}/*"`. Concatenation with `+` also works.
- **Inner `spec` shadows yours.** Inside a dict that defines its own `spec.<x>` key, `spec.<y>`
  means that dict's `spec`, not the `spec` local holding the XR spec:

  ```kcl
  _bucket = {
      spec.forProvider.region = spec.region   # wrong: reads _bucket's own spec
  }
  _region = spec.region                       # right: bind XR values to locals first
  _bucket = {
      spec.forProvider.region = _region
  }
  ```

  The symptom is a value that goes missing, or `expected str, got {str:str}`.
- **`in` on a schema instance tests declaration, not presence.** `"field" in obj` is True for every
  attribute the schema declares, even when unset. Test the value: `if obj.field` / `not obj.field`.

## The compose function

```kcl
import .schemas_compositions
import .schemas_providers

composeThing = lambda oxr, ocds -> [any] {
    spec: schemas_compositions.ThingSpec = oxr.spec
    _thing = {...}
    [_thing]            # last expression is the return value
}
```

The name must be exactly `compose<Kind>` with `lambda oxr, ocds`. Import only `.schemas_compositions`,
`.schemas_providers` and the standard library; Kiln flattens files into one source string.

The standard library and string methods work inside compose functions:

```kcl
import json

_policy = json.encode({Version = "2012-10-17", Statement = []})   # a JSON string, as policy fields take
_resourceName = "www.example.com".replace(".", "-")              # "www-example-com"
```

## Schemas

```kcl
schema ThingSpec:
    name: str                 # required
    count: int = 5            # default
    tags?: {str:str}          # optional
```

Schemas can carry validation: a `check:` block (`count > 0, "count must be positive"`).
Indentation is any consistent width; imported schemas use 4 spaces.

## Optional values and observed state

```kcl
_arn = ocds["bucket"]?.Resource?.status?.atProvider?.arn   # None before it is observed
_policy = [_policyResource] if _arn else []                # gate dependent resources
region = spec.region or "us-east-1"
```

Build typed values (schemas with required fields) inside the same `if` that gates them.

## Tests

KCL has `assert` and a built-in runner. Put `test_*` lambdas in `kcl-scripts/<kind>_test.k`
and run `kcl test .` from `kcl-scripts/`:

```kcl
import .thing

test_builds_one_resource = lambda {
    result = thing.composeThing({spec = {name = "x"}}, {})
    assert len(result) == 1, "expected exactly one resource"
}
```

Top-level names in test files share one package: prefix helpers with the kind (`_thingBaseOxr`).
The required test list is in [`../kiln/testing.md`](../kiln/testing.md).

## Common errors

| Error | Usual cause |
|-------|-------------|
| `expected one of ["}"] got ,` | Comma between multi-line dict entries |
| `unexpected token 'indent'` | Inconsistent indentation, or a continuation line starting with an operator |
| `unexpected token '+'` (or `'\|'`) | A line starting with an operator; end the previous line with the operator and `\` |
| `expected one of ["identifier", "literal", "(", "[", "{"] got newline` | An operator at the end of a line without a `\` after it |
| `expected one of ["identifier", "literal", "(", "[", "{"] got =` on `type = ...` | `type` used as a bare name; rename the local, or write the key as `"type"` / `$type` |
| `name 'X' is not defined` | Typo, or the name is defined in a file you cannot import (one-package rule) |
| Type mismatch on `forProvider` | Field name or type differs from the imported schema; read `schemas_providers.k` |
| Unknown attribute on `StatusAtProvider` | Those schemas are closed; check the real field names |
| `expected str, got {str:str}` inside a resource dict | `spec.<y>` resolves to the dict's own `spec`; bind the XR value to a local first |

## Examples

Before inventing a pattern, read the existing `kcl-scripts/<kind>.k` and `<kind>_test.k` files in
this project. They show the conventions already in use (observed-state staging, status, child XRs).
