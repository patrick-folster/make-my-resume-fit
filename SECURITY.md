# Security Policy

## Supported Versions

Security fixes are handled on the current `main` branch until formal release
branches exist.

## Reporting A Vulnerability

Please report security issues privately rather than opening a public issue.
If the repository has GitHub private vulnerability reporting enabled, use that
channel. Otherwise, contact the maintainer through the contact method listed on
the repository profile.

Include:

- affected version or commit;
- operating system and Python version;
- steps to reproduce;
- expected and actual behavior;
- any relevant logs with personal data removed.

## Sensitive Data

This tool processes resumes, job postings, generated resumes, and metadata. A
resume can contain personal information such as names, locations, employment
history, education, phone numbers, and email addresses.

Do not include real resumes, generated resume archives, job-application
metadata, `.env` files, tokens, or credentials in public issues, pull requests,
or test fixtures.

The CLI copies the source resume into an isolated temporary run directory and
preserves temp run directories for debugging. Users should delete those
directories when they no longer need them.

The Codex invocation is configured with live search and sandboxed network access
so job-offer URLs can be fetched. Review all generated resume claims before use.
