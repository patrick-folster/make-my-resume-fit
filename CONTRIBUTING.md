# Contributing

Thanks for considering a contribution to `make-my-resume-fit`.

## Development Setup

Use Python 3.10 or newer. This project currently has no runtime dependencies.

```bash
python -m unittest
```

For an installed CLI smoke test, install the project into a virtual environment
and run:

```bash
make-my-resume-fit --help
```

## Project Layout

- `make_my_resume_fit.py` contains the CLI parser, validation, template
  rendering, Codex invocation, metadata validation, and artifact publication.
- `resume-fitter.md` is the prompt template consumed by the CLI.
- `schemas/metadata.schema.json` defines the structured metadata expected from
  Codex.
- `tests/test_make_my_resume_fit.py` contains the unit tests.

## Change Guidelines

- Keep behavior changes covered by focused unit tests.
- Keep parser behavior, README examples, and tests aligned.
- Accept multiple job offers only by repeating `--job-offer`.
- Keep Codex command construction isolated in `build_codex_command()`.
- Preserve privacy boundaries: the Codex workspace should receive the temp copy
  of the resume, not direct access to the original resume path or output folder.
- Do not commit generated resumes, PDFs, metadata outputs, cache files, virtual
  environments, or local `.env` files.

## Checks Before Opening A Pull Request

Run:

```bash
python -m unittest
git diff --check
```

If you change user-facing CLI behavior, update `README.md` in the same change.
If you change prompt placeholders, keep `resume-fitter.md` and `PLACEHOLDERS` in
`make_my_resume_fit.py` synchronized.
