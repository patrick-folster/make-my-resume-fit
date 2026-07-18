# Decisions

## 0001 Resume Fitter CLI

- The CLI invokes Codex with `codex exec -` and passes the rendered prompt on
  standard input. Command construction is isolated in `build_codex_command()` so
  the invocation can be changed later without affecting parsing, validation, or
  template rendering.
- Multiple job offer URLs are accepted only by repeating `--job-offer`, which
  keeps parsing unambiguous and aligns the help text, README example, and tests.
