# Privacy Notice

This tool processes resume content, job-offer URLs, generated resumes, and
generated metadata. Resumes often contain personal information, so review the
data you provide before running the tool.

The wrapper creates an isolated temporary run directory, copies the source
resume into that directory as `orig.tex`, and preserves temporary run
directories for debugging. After a successful run, it copies the original
resume, tailored resume, and metadata into the requested output archive.

The wrapper invokes the local Codex CLI and passes the rendered prompt on
standard input. Depending on your Codex and OpenAI configuration, resume
content, job-offer content, prompts, tool output, generated resumes, and
metadata may be processed by external services. Review the terms and privacy
settings for the tools and accounts you configure.

Do not use this project to process resumes, job postings, or personal data that
you do not have permission to use. You are responsible for handling generated
files, temporary files, logs, and shared outputs according to your own privacy,
security, and compliance obligations.
