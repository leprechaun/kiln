import tomllib
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path

import yaml

from kiln.discover import discover_compose_files

MARKER = "kiln.toml"


FORMATS = ("yaml", "jsonnet")
SCOPES = ("Namespaced", "Cluster")


class ProjectNotFound(Exception):
    pass


class InvalidConfig(Exception):
    pass


@dataclass(frozen=True)
class Kind:
    """One composite kind and everything the project's conventions derive from its name."""

    name: str
    spec_schema: str
    plural: str
    output_dir: Path
    fixtures_dir: Path
    scope: str
    provider_config: dict[str, str] | None
    source_file: Path

    @property
    def xr_file(self) -> Path:
        return self.fixtures_dir / "xr.yaml"

    @property
    def xrd_file(self) -> Path:
        return self.output_dir / "xrd.yaml"

    @property
    def composition_file(self) -> Path:
        return self.output_dir / "composition.yaml"

    @property
    def composition_jsonnet_file(self) -> Path:
        return self.output_dir / "composition.jsonnet"

    def deployed_scope(self) -> str:
        """The scope the kind's generated XRD says it is deployed with, else the one kiln.toml sets."""
        if self.xrd_file.is_file():
            scope = ((yaml.safe_load(self.xrd_file.read_text()) or {}).get("spec") or {}).get("scope")
            if scope:
                return scope
        return self.scope


@dataclass(frozen=True)
class Project:
    root: Path
    group: str
    format: str = "yaml"
    scope: str = "Namespaced"
    kind_scopes: dict[str, str] = field(default_factory=dict)
    provider_config: dict[str, str] | None = None
    kind_provider_configs: dict[str, dict[str, str]] = field(default_factory=dict)

    def _kind_setting(self, settings: dict, kind: str, default):
        # Kinds come from kiln.toml (CamelCase) and from the command line, often lowercased.
        matches = [value for name, value in settings.items() if name.lower() == kind.lower()]
        return matches[0] if matches else default

    def scope_for(self, kind: str) -> str:
        return self._kind_setting(self.kind_scopes, kind, self.scope)

    def provider_config_for(self, kind: str) -> dict[str, str] | None:
        """The providerConfigRef to give composed managed resources that do not set one, if configured."""
        return self._kind_setting(self.kind_provider_configs, kind, self.provider_config)

    @cached_property
    def _compose_files(self) -> dict[str, Path]:
        """A snapshot of kcl-scripts taken on first use, so later changes on disk are not seen."""
        return discover_compose_files(self.kcl_scripts_dir)

    def kind(
        self, name: str, spec_schema: str | None = None, plural: str | None = None, scope: str | None = None
    ) -> Kind:
        """The kind called `name` (any case: the command line often lowercases it), with the project's conventions applied."""
        name = next((k for k in self._compose_files if k.lower() == name.lower()), name)
        return Kind(
            name=name,
            source_file=self._compose_files.get(name) or self.kcl_scripts_dir / f"{name.lower()}.k",
            spec_schema=spec_schema or f"{name}Spec",
            plural=plural or f"{name.lower()}s",
            output_dir=self.compositions_dir / name.lower(),
            fixtures_dir=self.render_fixtures_dir / name.lower(),
            scope=scope or self.scope_for(name),
            provider_config=self.provider_config_for(name),
        )

    @property
    def kcl_scripts_dir(self) -> Path:
        return self.root / "kcl-scripts"

    @property
    def compositions_dir(self) -> Path:
        return self.root / "manifests" / "crossplane-compositions"

    @property
    def providers_dir(self) -> Path:
        return self.root / "manifests" / "crossplane-providers"

    @property
    def functions_file(self) -> Path:
        return self.root / "manifests" / "functions.yaml"

    @property
    def render_fixtures_dir(self) -> Path:
        return self.root / "render-fixtures"

    @property
    def crds_dir(self) -> Path:
        return self.root / "crds"


def _provider_config(value, where: str) -> dict[str, str]:
    if (
        not isinstance(value, dict)
        or set(value) != {"kind", "name"}
        or not all(isinstance(v, str) and v for v in value.values())
    ):
        raise InvalidConfig(
            f'{MARKER}: {where} must be a table with exactly a kind and a name, '
            f'e.g. {{ kind = "ClusterProviderConfig", name = "default" }}, got {value!r}'
        )
    return dict(value)


def find_project(start: Path, root: Path | None = None) -> Project:
    candidates = [root] if root else [start, *start.parents]
    for candidate in candidates:
        marker = candidate / MARKER
        if marker.is_file():
            config = tomllib.loads(marker.read_text())
            output_format = config.get("format", "yaml")
            if output_format not in FORMATS:
                raise InvalidConfig(f"{MARKER}: format must be one of {', '.join(FORMATS)}, got {output_format!r}")
            kinds = config.get("kinds", {})
            scope = config.get("scope", "Namespaced")
            kind_scopes = {kind: table.get("scope", scope) for kind, table in kinds.items()}
            for where, value in [("scope", scope), *[(f"kinds.{k}.scope", v) for k, v in kind_scopes.items()]]:
                if value not in SCOPES:
                    raise InvalidConfig(f"{MARKER}: {where} must be one of {', '.join(SCOPES)}, got {value!r}")
            provider_config = (
                _provider_config(config["providerConfig"], "providerConfig") if "providerConfig" in config else None
            )
            kind_provider_configs = {
                kind: _provider_config(table["providerConfig"], f"kinds.{kind}.providerConfig")
                for kind, table in kinds.items()
                if "providerConfig" in table
            }
            return Project(
                root=candidate,
                group=config["group"],
                format=output_format,
                scope=scope,
                kind_scopes=kind_scopes,
                provider_config=provider_config,
                kind_provider_configs=kind_provider_configs,
            )
    raise ProjectNotFound(f"no {MARKER} found in {root or start}" + ("" if root else " or any parent directory"))
