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
and invokes Codex with structured-output capture:

```bash
codex --search -c sandbox_workspace_write.network_access=true exec --sandbox workspace-write --skip-git-repo-check -C <temp-run-directory> --output-schema <schema-file> -o <temp-run-directory>/metadata.json -
```

The rendered prompt is passed to Codex on standard input. Codex is instructed to
read `orig.tex`, fetch and process every supplied job offer URL, and write the
optimized LaTeX resume as `new.tex` in the temp run directory. Codex must return
only schema-matching JSON as its final response; the wrapper captures that final
response as temp-local `metadata.json` and validates it against
`schemas/metadata.schema.json`. The metadata includes a lowercase hyphenated
`slug` in the form `<shortened company name>-<shortened position>`, with
`changes` as the final top-level JSON property. The wrapper does not grant Codex
direct access to the repository root, the original resume path, or the final
output folder. The `--search` flag gives the Codex run live search access, and
`sandbox_workspace_write.network_access=true` allows sandboxed shell commands
such as `curl` to fetch job postings directly.

After Codex exits successfully, the script verifies that the temp run directory
contains a file named `new.tex`, verifies that the captured structured response
is valid JSON matching the repository schema, reads the validated metadata
`slug`, creates `--output-folder` when needed, and writes both final artifacts to
a dated run archive:

```text
<output-folder>/
`-- 2026-07-18-v1-example-python-engineer/
    |-- new.tex
    `-- metadata.json
```

Archive folder names use the system local date in `yyyy-mm-dd` format, a version
index, and the validated metadata slug:
`<yyyy>-<mm>-<dd>-v<index>-<metadata-slug>`. The version index starts at `v1`
for each date and slug combination. If a matching `v1` archive already exists,
the wrapper creates the next available folder such as `v2` or `v3` without
modifying the existing archive. Temp run directories are preserved for debugging.
The wrapper fails without creating the final output folder or archive when Codex
exits successfully but omits `new.tex`, omits `metadata.json`, returns malformed
JSON, returns JSON that does not match the schema, or returns metadata without a
usable slug.

When installed as a package, the CLI entry point is:

```bash
make-my-resume-fit
```

## Tests

```bash
python -m unittest
```
