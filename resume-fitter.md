# Resume Fitter Prompt

Use the supplied original resume, job offer URLs, and output folder exactly as provided.

You are already running inside the Codex process launched by this repository's
CLI wrapper. Do not run `make_my_resume_fit.py`, `make-my-resume-fit`, `codex`,
or any command that launches another Codex process. Read the original resume
directly and write the tailored LaTeX output directly under the supplied output
folder.

Original resume path:
{{ORIGINAL_RESUME}}

Job offer URLs:
{{JOB_OFFER_URLS}}

Output folder:
{{OUTPUT_FOLDER}}

Optimize the LaTeX resume for the supplied job offers. Keep the output in LaTeX format, preserve truthful experience and qualifications, and write all generated or modified files under the supplied output folder. Do not fetch or validate the URLs in this wrapper; use them as the job-offer references for the Codex run.
