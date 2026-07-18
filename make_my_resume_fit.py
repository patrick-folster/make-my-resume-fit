"""Command-line helper for rendering a resume-fitting Codex prompt."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Sequence


TEMPLATE_PATH = Path(__file__).with_name("resume-fitter.md")
PLACEHOLDERS = {
    "original_resume": "{{ORIGINAL_RESUME}}",
    "job_offer_urls": "{{JOB_OFFER_URLS}}",
    "output_folder": "{{OUTPUT_FOLDER}}",
}
UNRESOLVED_PLACEHOLDER_RE = re.compile(r"{{[^{}]+}}")


class CodexInvocationError(RuntimeError):
    """Raised when the local Codex executable cannot complete the prompt run."""


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser without performing any filesystem side effects."""
    parser = argparse.ArgumentParser(
        description="Render a resume-fitting prompt and run it with Codex.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Example:\n"
            "  python make_my_resume_fit.py --original-resume resume.tex \\\n"
            "    --job-offer https://example.com/a \\\n"
            "    --job-offer https://example.com/b \\\n"
            "    --output-folder out/resume-fit\n\n"
            "Pass multiple job offers by repeating --job-offer once per URL."
        ),
    )
    parser.add_argument(
        "--original-resume",
        required=True,
        type=Path,
        help="Path to the existing source resume LaTeX file (.tex).",
    )
    parser.add_argument(
        "--job-offer",
        action="append",
        required=True,
        dest="job_offers",
        metavar="URL",
        help="Job offer URL. Repeat this option to provide multiple URLs.",
    )
    parser.add_argument(
        "--output-folder",
        required=True,
        type=Path,
        help="Folder where Codex should write the tailored resume output.",
    )
    return parser


def validate_resume_path(path: Path) -> Path:
    """Return a resolved resume path after confirming it is an existing .tex file."""
    if not path.exists():
        raise ValueError(f"original resume does not exist: {path}")
    if not path.is_file():
        raise ValueError(f"original resume is not a file: {path}")
    if path.suffix.lower() != ".tex":
        raise ValueError(f"original resume must be a .tex file: {path}")
    return path.resolve()


def ensure_output_folder(path: Path) -> Path:
    """Create the output folder if needed and return its resolved path."""
    if path.exists() and not path.is_dir():
        raise ValueError(f"output folder is not a directory: {path}")
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ValueError(f"could not create output folder {path}: {exc}") from exc
    return path.resolve()


def load_template(path: Path = TEMPLATE_PATH) -> str:
    """Load the prompt template from disk."""
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"template file not found: {path}") from exc


def format_job_offers(job_offers: Sequence[str]) -> str:
    """Format repeated job-offer arguments as a deterministic Markdown list."""
    return "\n".join(f"- {url}" for url in job_offers)


def render_template(
    template: str,
    *,
    original_resume: Path,
    job_offers: Sequence[str],
    output_folder: Path,
) -> str:
    """Replace all known placeholders and reject unresolved template markers."""
    rendered = (
        template.replace(PLACEHOLDERS["original_resume"], str(original_resume))
        .replace(PLACEHOLDERS["job_offer_urls"], format_job_offers(job_offers))
        .replace(PLACEHOLDERS["output_folder"], str(output_folder))
    )
    unresolved = UNRESOLVED_PLACEHOLDER_RE.findall(rendered)
    if unresolved:
        names = ", ".join(sorted(set(unresolved)))
        raise ValueError(f"template contains unresolved placeholders: {names}")
    return rendered


def build_codex_command() -> list[str]:
    """Return the local Codex command used to consume the rendered prompt on stdin."""
    return ["codex", "exec", "-"]


def invoke_codex(prompt: str) -> None:
    """Invoke Codex with the rendered prompt via stdin."""
    command = build_codex_command()
    try:
        completed = subprocess.run(
            command,
            input=prompt,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise CodexInvocationError(
            "Codex executable not found. Ensure `codex` is installed and on PATH."
        ) from exc
    except OSError as exc:
        raise CodexInvocationError(f"failed to invoke Codex: {exc}") from exc

    if completed.returncode != 0:
        raise CodexInvocationError(
            f"Codex command failed with exit code {completed.returncode}."
        )


def run(argv: Sequence[str] | None = None) -> int:
    """Parse arguments, render the prompt, and invoke Codex."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        original_resume = validate_resume_path(args.original_resume)
        output_folder = ensure_output_folder(args.output_folder)
        template = load_template()
        prompt = render_template(
            template,
            original_resume=original_resume,
            job_offers=args.job_offers,
            output_folder=output_folder,
        )
        invoke_codex(prompt)
    except ValueError as exc:
        parser.error(str(exc))
    except CodexInvocationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    return 0


def main() -> None:
    """Console-script entry point."""
    raise SystemExit(run())


if __name__ == "__main__":
    main()
