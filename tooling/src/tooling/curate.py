import argparse
import re
import sys

_SCHEMA_START = re.compile(r"^schema (\w+):", re.MULTILINE)
_DOCSTRING = re.compile(r'r""".*?"""', re.DOTALL)


def _without_docstring(block: str) -> str:
    return _DOCSTRING.sub("", block)


def curate_provider_schema(source: str) -> str:
    starts = [(m.start(), m.group(1)) for m in _SCHEMA_START.finditer(source)]
    blocks = {}
    for i, (start, name) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else len(source)
        blocks[name] = source[start:end]

    # Reference detection must look only at actual type annotations, not
    # docstring prose -- real-world descriptions routinely use a schema's
    # name as plain English (e.g. "...the Lambda Function...") which would
    # otherwise look like a genuine reference to that schema.
    bodies_for_matching = {name: _without_docstring(block) for name, block in blocks.items()}

    keep = {name for name in blocks if name.endswith("SpecForProvider")}
    frontier = set(keep)
    while frontier:
        name = frontier.pop()
        for other in blocks:
            if other not in keep and re.search(rf"\b{re.escape(other)}\b", bodies_for_matching[name]):
                keep.add(other)
                frontier.add(other)

    return "\n".join(block for name, block in blocks.items() if name in keep)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Curate a kcl-import-generated schema file down to just "
        "SpecForProvider and its transitively-referenced schemas."
    )
    parser.add_argument("input", help="Path to a kcl-import-generated .k file")
    parser.add_argument("-o", "--output", help="Where to write the curated .k file (defaults to stdout)")
    args = parser.parse_args()

    with open(args.input) as f:
        curated = curate_provider_schema(f.read())

    if args.output:
        with open(args.output, "w") as f:
            f.write(curated)
    else:
        sys.stdout.write(curated)
