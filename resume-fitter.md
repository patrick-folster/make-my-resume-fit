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
complete optimized resume to the required output file. Do not fetch or validate
the URLs in this wrapper; use them as the job-offer references for the Codex
run.
