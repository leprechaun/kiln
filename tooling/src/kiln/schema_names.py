import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import yaml

from kiln.curate import split_blocks, without_docstring

_SCHEMA_NAME = re.compile(r"^schema (\w+):", re.MULTILINE)


@dataclass(frozen=True)
class CrdIdentity:
    group: str
    kind: str
    versions: tuple[str, ...]


def read_crd_identity(crd_file: Path) -> CrdIdentity:
    spec = yaml.safe_load(crd_file.read_text())["spec"]
    if not spec.get("versions"):
        raise ValueError(f"{crd_file}: the CRD has no spec.versions")
    return CrdIdentity(
        group=spec["group"],
        kind=spec["names"]["kind"],
        versions=tuple(v["name"] for v in spec["versions"]),
    )


def _group_prefix(group: str) -> str:
    # e.g. lambda.aws.m.upbound.io -> LambdaAwsmUpboundIo: a one-letter segment joins the one before it
    parts: list[str] = []
    for segment in group.split("."):
        if len(segment) == 1 and parts:
            parts[-1] += segment
        else:
            parts.append(segment.capitalize())
    return "".join(parts)


def schema_prefixes(crd: CrdIdentity) -> list[str]:
    """The prefix every curated schema of this CRD carries, one per version."""
    return [f"{_group_prefix(crd.group)}{v.capitalize()}{crd.kind}" for v in crd.versions]


def _scoped(remainder: str) -> str:
    # Only the spec side is mapped back to the 0.12 names, because compose functions refer to those.
    # Status-side nested types keep kcl's own names: mapping `AtProvider...` to `StatusAtProvider...`
    # would collide with 0.13's separate `StatusAtProvider...` types for nested lists.
    if remainder == "" or remainder.startswith(("Spec", "Status", "AtProvider")):
        return remainder
    if remainder.startswith(("ForProvider", "InitProvider")):
        return "Spec" + remainder
    return "SpecForProvider" + remainder


def to_group_prefixed_names(source: str, crd: CrdIdentity) -> str:
    """Rename kcl 0.13's `<Kind><Version>...` schemas to the group-prefixed names kcl 0.12 produced.

    0.13 drops the API group from schema names, so two groups' `Function` kinds would collide
    in schemas_providers.k. Names already in the group-prefixed form are left alone.
    """
    names = _SCHEMA_NAME.findall(source)
    renames = {}
    for version, prefix in zip(crd.versions, schema_prefixes(crd)):
        flat = f"{crd.kind}{version.capitalize()}"
        for name in names:
            if name.startswith(flat):
                renames[name] = prefix + _scoped(name[len(flat) :])

    if not renames:
        return source

    pattern = r"\b(" + "|".join(map(re.escape, sorted(renames, key=len, reverse=True))) + r")\b"

    def rename(text: str) -> str:
        return re.sub(pattern, lambda m: renames[m.group(1)], text)

    # kcl may emit two schemas under names that only differ where we drop or move a segment. Identical
    # definitions (docstrings aside) are the same schema, so they merge; different ones can't share a name.
    _, blocks = split_blocks(source)
    by_new_name = defaultdict(list)
    for name, new_name in renames.items():
        by_new_name[new_name].append(name)
    for new_name, group in by_new_name.items():
        if len({"".join(without_docstring(rename(blocks[n])).split()) for n in group}) > 1:
            raise ValueError(
                f"kcl schemas {' and '.join(sorted(group))} collide: all would be named {new_name} but their definitions differ"
            )

    return rename(source)
