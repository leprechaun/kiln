import tomllib
from dataclasses import dataclass, field
from pathlib import Path

MARKER = "kiln.toml"


FORMATS = ("yaml", "jsonnet")
SCOPES = ("Namespaced", "Cluster")


class ProjectNotFound(Exception):
    pass


class InvalidConfig(Exception):
    pass


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
