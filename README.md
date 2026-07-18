# make-my-resume-fit

`make_my_resume_fit.py` renders `resume-fitter.md` with an existing LaTeX resume,
one or more job offer URLs, and an output folder, then sends the rendered prompt
to the local Codex CLI.

## Usage

```bash
python make_my_resume_fit.py \
  --original-resume resume.tex \
  --job-offer https://example.com/a \
  --job-offer https://example.com/b \
  --output-folder out/resume-fit
```

Repeat `--job-offer` once for each URL. The script validates that the resume is
an existing `.tex` file, creates the output folder when needed, renders the
template without unresolved `{{PLACEHOLDER}}` markers, and invokes:

```bash
codex exec --sandbox workspace-write -C <working-root> -
```

The rendered prompt is passed to Codex on standard input. If the output folder
is outside the working root, the script also passes `--add-dir <output-folder>`.

When installed as a package, the CLI entry point is:

```bash
make-my-resume-fit
```

## Tests

```bash
python -m unittest
```
