# Repository Instructions

## Source Map

- `make_my_resume_fit.py` contains the CLI parser, validation, template rendering, Codex invocation, and console entry point.
- `resume-fitter.md` is the prompt template consumed by the CLI; keep placeholder names in sync with `PLACEHOLDERS`.
- `tests/test_make_my_resume_fit.py` covers parser behavior, path validation, rendering, Codex invocation, and the top-level `run()` flow.
- `README.md` documents user-facing CLI usage and should match parser semantics.

## Working Rules

- Work inside this repository only; do not write files into parent or adjacent projects.
- Keep changes scoped to the requested task and preserve unrelated work in the working tree.
- Do not create, switch, or rename git branches unless the user explicitly asks for branch operations.
- Use repository-relative paths in docs and instructions.
- Write well-commented code that explains non-obvious logic so future human and AI maintainers can understand it.
- Add or update tests for behavioral changes, including edge cases and failure paths that are practical to exercise.
- Keep `.cyclestone/DECISIONS.md` as chronological project history; do not merge it wholesale into `AGENTS.md`.

## CLI Invariants

- The CLI invokes Codex through `build_codex_command()` and passes the rendered prompt on standard input.
- Keep command construction isolated in `build_codex_command()` so invocation changes do not affect parsing, validation, or rendering.
- Accept multiple job offers only by repeating `--job-offer`; keep parser behavior, README examples, and tests aligned with that contract.
- Validate that `--original-resume` points to an existing `.tex` file before rendering.
- Create `--output-folder` when needed, but reject an existing non-directory path.
- Reject rendered templates that still contain unresolved `{{PLACEHOLDER}}` markers.

## Checks

- Run `python -m unittest` after code changes.
- Run `git diff --check` before handing off edits.
