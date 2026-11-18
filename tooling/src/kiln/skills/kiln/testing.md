# Testing

Tests are a required part of every kind, written before the function they test. They live in
`kcl-scripts/<kind>_test.k` and run with:

```bash
cd kcl-scripts
kcl test .
```

```kcl
import .objectstore

test_builds_the_bucket_from_spec = lambda {
    oxr = {spec = {bucketName = "my-bucket", region = "eu-west-1"}}
    ocds = {}

    result = objectstore.composeObjectStore(oxr, ocds)

    assert len(result) == 1
    assert result[0].kind == "Bucket"
}
```

## The tests every kind needs

A kind is not tested until its `<kind>_test.k` has a `test_*` function for each of these:

1. **Every resource it can emit:** `apiVersion`, `kind`, the composition-resource-name
   annotation, and the `forProvider` fields that come from the spec (and the external
   name, if you set one).
2. **Optional spec fields:** passed through when set, and absent when not set.
3. **Defaults:** a spec default takes effect when the consumer leaves the field out.
4. **Every conditional resource** (anything built `if ... else None`): absent when its
   condition is false or its input is not observed yet, present when it is.
5. **Observed-state stages:** cold start (`ocds = {}`), a resource observed but with an
   empty `atProvider = {}`, partly observed, and fully observed. Assert exactly what is
   emitted at each stage.
6. **Status:** the returned XR carries the right status once the value is observed, and is
   not emitted before.
7. **Spec rules:** for each `check:` rule, a test where a valid spec composes. The rejected
   side cannot be asserted in `kcl test`; it is an `invalid-<case>.yaml` render fixture
   ([`rendering.md`](rendering.md)).

## The loop

Write one test, watch it fail, write the minimal code to pass it, repeat. The whole function
comes after its first test, never before it. `kcl test` is necessary but not sufficient: a green
suite has hidden real bugs before, and rendering ([`rendering.md`](rendering.md)) catches what it
cannot. Mirror each observed-state stage you test with an `observed-<stage>.yaml` render fixture.

Top-level names in test files share one package with every other file in `kcl-scripts/`: prefix
test functions and shared `_`-locals with your kind's name (`_objectStoreBaseOxr`).
