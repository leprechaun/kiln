import re

_SCHEMA_START = re.compile(r"^schema (\w+):", re.MULTILINE)
_DOCSTRING = re.compile(r'r""".*?"""', re.DOTALL)


def without_docstring(block: str) -> str:
    return _DOCSTRING.sub("", block)


def split_blocks(source: str) -> tuple[str, dict[str, str]]:
    """Split into (text before the first schema, {schema name: its block, verbatim})."""
    starts = [(m.start(), m.group(1)) for m in _SCHEMA_START.finditer(source)]
    blocks = {}
    for i, (start, name) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else len(source)
        blocks[name] = source[start:end]
    return source[: starts[0][0]] if starts else source, blocks


def curate_provider_schema(source: str) -> str:
    _, blocks = split_blocks(source)

    # Reference detection must look only at actual type annotations, not
    # docstring prose -- real-world descriptions routinely use a schema's
    # name as plain English (e.g. "...the Lambda Function...") which would
    # otherwise look like a genuine reference to that schema.
    bodies_for_matching = {name: without_docstring(block) for name, block in blocks.items()}

    keep = {name for name in blocks if name.endswith(("SpecForProvider", "StatusAtProvider"))}
    frontier = set(keep)
    while frontier:
        name = frontier.pop()
        for other in blocks:
            if other not in keep and re.search(rf"\b{re.escape(other)}\b", bodies_for_matching[name]):
                keep.add(other)
                frontier.add(other)

    return "\n".join(block for name, block in blocks.items() if name in keep)


def merge_schemas(existing: str, curated: str, owned_prefixes: tuple[str, ...] | list[str] = ()) -> str:
    """Put each curated schema into `existing`: replace it in place if present, append it if not.

    An existing schema that is `<prefix>SpecForProvider*`, `<prefix>StatusAtProvider*` or
    `<prefix>AtProvider*` for one of `owned_prefixes` but is not in `curated` is stale (the provider
    no longer generates it) and is dropped.
    """
    preamble, existing_blocks = split_blocks(existing)
    _, curated_blocks = split_blocks(curated)
    owned = tuple(f"{prefix}{root}" for prefix in owned_prefixes for root in ("SpecForProvider", "StatusAtProvider", "AtProvider"))

    merged = []
    for name, block in existing_blocks.items():
        if name.startswith(owned) and name not in curated_blocks:
            continue
        if name in curated_blocks:
            trailing = block[len(block.rstrip("\n")) :]
            block = curated_blocks[name].rstrip("\n") + trailing
        merged.append(block)

    added = [block for name, block in curated_blocks.items() if name not in existing_blocks]
    result = preamble + "".join(merged)
    if added:
        result = result.rstrip("\n") + "\n\n" + "\n".join(added)
    return result
