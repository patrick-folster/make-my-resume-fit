# Decisions

## 0001 Resume Fitter CLI

- The CLI invokes Codex with `codex exec -` and passes the rendered prompt on
  standard input. Command construction is isolated in `build_codex_command()` so
  the invocation can be changed later without affecting parsing, validation, or
  template rendering.
- Multiple job offer URLs are accepted only by repeating `--job-offer`, which
  keeps parsing unambiguous and aligns the help text, README example, and tests.

## 0003 Isolated Codex Workspace

- Each CLI run creates a unique `make-my-resume-fit-YYYYMMDDTHHMMSSffffff`
  directory under the system temp folder, copies the validated source resume to
  `orig.tex`, and preserves the temp directory for debugging.
- Codex is invoked with the temp run directory as its `-C` working root and no
  extra writable directories, so the prompt and command do not expose the
  original resume path, repository root, or final output folder.
- The deterministic optimized resume filename is `new.tex`. Codex writes it in
  the temp run directory, and the wrapper copies it to `--output-folder/new.tex`,
  overwriting that final file when it already exists.

## 0004 Structured Change Tracking

- Codex is invoked with `--output-schema schemas/changes.schema.json` and
  `-o <temp-run-directory>/changes.json` so the tailored resume and audit trail
  are both produced inside the isolated temp workspace before publication.
- The wrapper validates the captured final response with standard-library JSON
  parsing plus a focused validator for the repository-owned schema subset,
  avoiding a runtime dependency for this narrow contract.
- Final artifacts are published only after both `new.tex` and structured
  `changes.json` validate, preventing partial successful output in the requested
  output folder.

## 0005 Archive Run Artifacts

- Final artifacts are published under
  `<output-folder>/<yyyy>-<mm>-<dd>-v<index>-<metadata-slug>/`, using the system
  local date and the validated `slug` from Codex's `metadata.json`.
- Archive version selection probes from `v1` upward and creates the selected
  directory with `exist_ok=False`, so existing archives are not overwritten or
  modified.
- The wrapper keeps output-folder creation until after `new.tex` and
  `metadata.json` have both validated, and it performs a defensive filesystem
  slug check before creating an archive directory.
