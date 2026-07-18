"""Command-line helper for rendering a resume-fitting Codex prompt."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Sequence


TEMPLATE_PATH = Path(__file__).with_name("resume-fitter.md")
ORIGINAL_RESUME_FILENAME = "orig.tex"
TAILORED_RESUME_FILENAME = "new.tex"
RUN_DIR_PREFIX = "make-my-resume-fit-"
PLACEHOLDERS = {
    "input_resume": "{{INPUT_RESUME}}",
    "job_offer_urls": "{{JOB_OFFER_URLS}}",
    "output_resume": "{{OUTPUT_RESUME}}",
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
        help="Folder where the wrapper should copy the tailored resume output.",
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


def create_run_workspace(
    original_resume: Path,
    *,
    temp_root: Path | None = None,
    timestamp: dt.datetime | None = None,
) -> Path:
    """Create an isolated temp run directory and copy the resume to orig.tex."""
    root = Path(temp_root) if temp_root is not None else Path(tempfile.gettempdir())
    stamp = (timestamp or dt.datetime.now()).strftime("%Y%m%dT%H%M%S%f")

    # The timestamp is enough for normal runs; the suffix handles deterministic
    # tests, clock collisions, and concurrent invocations in the same microsecond.
    for suffix in ["", *[f"-{index:02d}" for index in range(1, 100)]]:
        run_dir = root / f"{RUN_DIR_PREFIX}{stamp}{suffix}"
        try:
            run_dir.mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            continue
        shutil.copyfile(original_resume, run_dir / ORIGINAL_RESUME_FILENAME)
        return run_dir.resolve()

    raise ValueError(f"could not create a unique temp run directory under {root}")


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
    input_resume: str = ORIGINAL_RESUME_FILENAME,
    job_offers: Sequence[str],
    output_resume: str = TAILORED_RESUME_FILENAME,
) -> str:
    """Replace all known placeholders and reject unresolved template markers."""
    rendered = (
        template.replace(PLACEHOLDERS["input_resume"], input_resume)
        .replace(PLACEHOLDERS["job_offer_urls"], format_job_offers(job_offers))
        .replace(PLACEHOLDERS["output_resume"], output_resume)
    )
    unresolved = UNRESOLVED_PLACEHOLDER_RE.findall(rendered)
    if unresolved:
        names = ", ".join(sorted(set(unresolved)))
        raise ValueError(f"template contains unresolved placeholders: {names}")
    return rendered


def build_codex_command(run_dir: Path) -> list[str]:
    """Return the sandboxed Codex command used to consume the prompt on stdin."""
    return ["codex", "exec", "--sandbox", "workspace-write", "-C", str(run_dir.resolve()), "-"]


def invoke_codex(prompt: str, *, run_dir: Path) -> None:
    """Invoke Codex with the rendered prompt via stdin."""
    command = build_codex_command(run_dir)
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


def validate_generated_resume(run_dir: Path) -> Path:
    """Return the temp new.tex path after confirming Codex produced a file."""
    generated_resume = run_dir / TAILORED_RESUME_FILENAME
    if not generated_resume.is_file():
        raise CodexInvocationError(
            f"Codex completed without producing {TAILORED_RESUME_FILENAME} in {run_dir}."
        )
    return generated_resume


def copy_generated_resume(generated_resume: Path, output_folder: Path) -> Path:
    """Copy temp new.tex to the deterministic final output path."""
    output = ensure_output_folder(output_folder)
    final_resume = output / TAILORED_RESUME_FILENAME
    shutil.copyfile(generated_resume, final_resume)
    return final_resume


def run(argv: Sequence[str] | None = None) -> int:
    """Parse arguments, render the prompt, and invoke Codex."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        original_resume = validate_resume_path(args.original_resume)
        run_dir = create_run_workspace(original_resume)
        template = load_template()
        prompt = render_template(
            template,
            input_resume=ORIGINAL_RESUME_FILENAME,
            job_offers=args.job_offers,
            output_resume=TAILORED_RESUME_FILENAME,
        )
        invoke_codex(prompt, run_dir=run_dir)
        generated_resume = validate_generated_resume(run_dir)
        copy_generated_resume(generated_resume, args.output_folder)
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
