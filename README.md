# make-my-resume-fit

`make_my_resume_fit.py` renders `resume-fitter.md` with an existing LaTeX resume,
one or more job offer URLs, and fixed temp-local filenames, then sends the
rendered prompt to the local Codex CLI.

## Usage

```bash
python make_my_resume_fit.py \
  --original-resume resume.tex \
  --job-offer https://example.com/a \
  --job-offer https://example.com/b \
  --output-folder out/resume-fit
```

Repeat `--job-offer` once for each URL. The script validates that the resume is
an existing `.tex` file, creates a unique timestamp-named run directory under
the system temp folder, copies the validated resume into that directory as
`orig.tex`, renders the template without unresolved `{{PLACEHOLDER}}` markers,
and invokes:

```bash
codex exec --sandbox workspace-write --skip-git-repo-check -C <temp-run-directory> -
```

The rendered prompt is passed to Codex on standard input. Codex is instructed to
read `orig.tex` and write the optimized LaTeX resume as `new.tex` in the temp
run directory. The wrapper does not grant Codex direct access to the repository
root, the original resume path, or the final output folder.

After Codex exits successfully, the script verifies that the temp run directory
contains a file named `new.tex`, creates `--output-folder` when needed, and
copies the generated file to:

```text
<output-folder>/new.tex
```

If that final file already exists, it is overwritten. Temp run directories are
preserved for debugging.

When installed as a package, the CLI entry point is:

```bash
make-my-resume-fit
```

## Tests

```bash
python -m unittest
```
