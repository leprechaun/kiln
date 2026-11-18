import argparse
import sys
from pathlib import Path

from kiln.docs import render_docs, topic_names
from kiln.generate_all import generate_all
from kiln.generate_manifests import generate_manifests_for
from kiln.import_schema import import_schema
from kiln.init import DEFAULT_GROUP, init_project
from kiln.project import FORMATS, SCOPES, InvalidConfig, ProjectNotFound, find_project
from kiln.pull_crds import pull_crds
from kiln.render import render
from kiln.render_all import render_all
from kiln.skills import install_skills


_NO_VALIDATE_HELP = "Skip checking rendered resources' scope and shape against crds/ and the generated XRDs"


def _import(project, args) -> int:
    try:
        return import_schema(project, args.crd_file, print_only=args.print_only, schemas_file=args.schemas_file)
    except (ValueError, RuntimeError) as e:
        print(f"kiln: {e}", file=sys.stderr)
        return 1


def _generate(project, args) -> int:
    generate_manifests_for(
        kind=args.kind,
        spec_schema=args.spec_schema or f"{args.kind}Spec",
        group=project.group,
        plural=args.plural or f"{args.kind.lower()}s",
        kcl_dir=project.kcl_scripts_dir,
        output_dir=project.compositions_dir / args.kind.lower(),
        output_format=project.format,
        scope=args.scope or project.scope_for(args.kind),
        provider_config=project.provider_config_for(args.kind),
    )
    return 0


def _render(project, args) -> int:
    result = render(
        project, args.kind, observed_resources=args.observed_resources, validate=not args.no_validate, xr=args.xr
    )
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    return result.returncode


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="kiln", description="KCL-first authoring pipeline for Crossplane compositions.")
    parser.add_argument("--root", type=Path, help="Project root (default: search upward from the current directory for kiln.toml)")
    commands = parser.add_subparsers(dest="command", required=True)

    docs_cmd = commands.add_parser(
        "docs", help="Print the Kiln guide (written for LLM agents as well as people); add a topic for more"
    )
    docs_cmd.add_argument("topic", nargs="?", help="A topic from the list at the end of `kiln docs`, or `all`")

    init_cmd = commands.add_parser("init", help="Create a new, empty Kiln project")
    init_cmd.add_argument("directory", type=Path, help="Where to create the project")
    init_cmd.add_argument("--group", default=DEFAULT_GROUP, help=f"API group for the project's XRs (default: {DEFAULT_GROUP})")
    init_cmd.add_argument(
        "--scope",
        choices=SCOPES,
        default="Namespaced",
        help="Default XR scope: Namespaced (composes namespaced resources) or Cluster. Override per kind in kiln.toml. Default: Namespaced",
    )
    init_cmd.add_argument(
        "--format",
        choices=FORMATS,
        default="yaml",
        help="Composition output format: yaml (KCL embedded) or jsonnet (importstr, for ArgoCD). Default: yaml",
    )

    skills_cmd = commands.add_parser(
        "install-skills", help="Install (or refresh) the agent skills bundled with Kiln into .agents/skills/"
    )
    skills_cmd.add_argument("--force", action="store_true", help="Overwrite skills that are already installed")
    skills_cmd.set_defaults(handler=lambda project, args: install_skills(project.root, force=args.force))

    commands.add_parser(
        "pull-crds", help="Download CRDs for every provider in manifests/crossplane-providers/"
    ).set_defaults(handler=lambda project, args: pull_crds(project))

    import_cmd = commands.add_parser(
        "import", help="Import a provider CRD, curated down to SpecForProvider, into schemas_providers.k"
    )
    import_cmd.add_argument("crd_file", type=Path, help="Path to a raw CRD YAML file, e.g. from crds/")
    import_cmd.add_argument(
        "--print", dest="print_only", action="store_true", help="Print the curated schema instead of appending it"
    )
    import_cmd.add_argument(
        "--schemas-file", type=Path, help="File to append the curated schema to (default: kcl-scripts/schemas_providers.k)"
    )
    import_cmd.set_defaults(handler=_import)

    generate_cmd = commands.add_parser("generate", help="Generate one kind's Composition and XRD")
    generate_cmd.add_argument("kind", help="Composite kind, e.g. IAMRole")
    generate_cmd.add_argument("--spec-schema", help="Composition spec schema name (default: <Kind>Spec)")
    generate_cmd.add_argument("--plural", help="Plural resource name (default: lowercased kind + 's')")
    generate_cmd.add_argument(
        "--scope",
        choices=SCOPES,
        help="XR scope for this run (default: the kind's scope in kiln.toml, else the project's scope, else Namespaced)",
    )
    generate_cmd.set_defaults(handler=_generate)

    commands.add_parser(
        "generate-all", help="Regenerate every kind's Composition and XRD"
    ).set_defaults(handler=lambda project, args: generate_all(project))

    render_cmd = commands.add_parser("render", help="Render one kind's Composition against its sample XR")
    render_cmd.add_argument("kind", help="Composite kind, e.g. IAMRole")
    render_cmd.add_argument(
        "--observed-resources",
        type=Path,
        help="Mocked observed resources: a multi-document YAML file, or a directory whose .yaml/.yml files are all loaded",
    )
    render_cmd.add_argument(
        "--xr", type=Path, help="The XR to render (default render-fixtures/<kind>/xr.yaml), e.g. an invalid-*.yaml fixture"
    )
    render_cmd.add_argument("--no-validate", action="store_true", help=_NO_VALIDATE_HELP)
    render_cmd.set_defaults(handler=_render)

    render_all_cmd = commands.add_parser(
        "render-all",
        help="Render every kind against its sample XR, cold and with each observed-*.yaml; check each invalid-*.yaml fails",
    )
    render_all_cmd.add_argument("--no-validate", action="store_true", help=_NO_VALIDATE_HELP)
    render_all_cmd.set_defaults(handler=lambda project, args: render_all(project, validate=not args.no_validate))

    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)

    if args.command == "docs":
        try:
            sys.stdout.write(render_docs(args.topic))
        except KeyError:
            print(f"kiln: no docs topic {args.topic!r}; choose one of: {', '.join(topic_names())}", file=sys.stderr)
            return 2
        return 0

    if args.command == "init":
        return init_project(args.directory, group=args.group, output_format=args.format, scope=args.scope)

    try:
        project = find_project(Path.cwd(), root=args.root)
    except InvalidConfig as e:
        print(f"kiln: {e}", file=sys.stderr)
        return 2
    except ProjectNotFound as e:
        print(f"kiln: {e}", file=sys.stderr)
        return 2

    return args.handler(project, args)


def run() -> None:
    sys.exit(main())
