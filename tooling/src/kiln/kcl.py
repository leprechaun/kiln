import subprocess
from pathlib import Path


class KclError(RuntimeError):
    """A `kcl` invocation failed; the message is fit to show the user as-is."""


def run_kcl(args: list[str], work_dir: Path) -> None:
    """Run `kcl <args>` in `work_dir`, raising KclError with what kcl reported if it fails."""
    try:
        result = subprocess.run(["kcl", *args], cwd=work_dir, capture_output=True, text=True)
    except FileNotFoundError:
        raise KclError("`kcl` binary not found: install kcl and put it on PATH") from None
    if result.returncode != 0:
        # Name the subcommand (`doc generate`, `import`), not a leading flag such as `-m`.
        words = [args[0]]
        if len(args) > 1 and not args[1].startswith("-"):
            words.append(args[1])
        detail = result.stderr.strip() or result.stdout.strip() or f"exit status {result.returncode}"
        raise KclError(f"kcl {' '.join(words)} failed: {detail}")
