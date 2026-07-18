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
