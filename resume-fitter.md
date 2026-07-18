# Resume Fitter Prompt

Use the supplied temp-local resume filenames and job offer URLs exactly as provided.

You are already running inside the Codex process launched by this repository's
CLI wrapper. Do not run `make_my_resume_fit.py`, `make-my-resume-fit`, `codex`,
or any command that launches another Codex process. You are running in an
isolated temp workspace. Read only the input resume file named below and write
the tailored LaTeX output only to the output resume file named below in the
current workspace.

Input resume file:
{{INPUT_RESUME}}

Job offer URLs:
{{JOB_OFFER_URLS}}

Output resume file:
{{OUTPUT_RESUME}}

Optimize the LaTeX resume for the supplied job offers. Keep the output in
LaTeX format, preserve truthful experience and qualifications, and write the
complete optimized resume to the required output file.

Fetch and read every supplied job offer URL before tailoring the resume. Base
the optimization on the fetched job descriptions, requirements, responsibilities,
and terminology. If shell commands such as `curl` cannot resolve or access a
URL, use the available live search or browser tools to fetch the posting. If a
URL still cannot be fetched after those options, clearly report that failure and
do not invent role-specific details from the URL alone.

When inspecting LaTeX control sequences with `rg`, search for them as literal
strings instead of regex patterns. For example:

```bash
rg -n -F \
  -e '\begin{document}' \
  -e '\end{document}' \
  -e '\section*' \
  -e '\newpage' \
  new.tex
```
