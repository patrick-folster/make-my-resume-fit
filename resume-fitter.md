# Resume Fitter Instructions

Use the supplied temporary resume filenames and job-offer URLs exactly as provided.

You are already running inside the Codex process launched by this repository’s CLI wrapper. Do not run `make_my_resume_fit.py`, `make-my-resume-fit`, `codex`, or any other command that launches another Codex process.

You are operating in an isolated temporary workspace.

## Required Inputs and Output

Input resume file:

`{{INPUT_RESUME}}`

Job-offer URLs:

`{{JOB_OFFER_URLS}}`

Output resume file:

`{{OUTPUT_RESUME}}`

Read only the supplied input resume and the fetched job descriptions. Write the complete tailored LaTeX resume only to:

`{{OUTPUT_RESUME}}`

Do not create alternative resume files, intermediate copies, summaries, cover letters, or other deliverables unless they are required internally to complete the task.

## Primary Objective

Tailor the resume to the supplied job offers while preserving factual accuracy.

The finished resume must work well for both:

1. recruiters and hiring managers reading the rendered PDF; and
2. applicant tracking systems parsing the PDF text.

Optimize relevance, clarity, keyword alignment, evidence, readability, and text-extraction quality without inventing or exaggerating qualifications.

## Job-Offer Retrieval

Fetch and read every supplied job-offer URL before modifying the resume.

Extract and evaluate, when available:

* company name;
* position title;
* required qualifications;
* preferred qualifications;
* responsibilities;
* technologies and tools;
* domain terminology;
* seniority expectations;
* leadership or collaboration expectations;
* location, remote-work, authorization, or availability requirements;
* repeated or prominently emphasized keywords.

Use the actual job descriptions as the basis for tailoring.

If a URL cannot be accessed with shell tools such as `curl`, use any available live-search or browser tools. If the posting still cannot be retrieved:

* do not infer requirements from the URL, company name, or position title alone;
* do not invent role-specific keywords;
* continue using only successfully retrieved postings;
* add a warning to the final JSON identifying the inaccessible URL.

When several job offers are supplied, optimize for their strongest shared requirements while retaining important role-specific terms where they can be supported truthfully.

## Source-of-Truth Rules

The input resume is the source of truth for the candidate’s:

* employment history;
* projects;
* responsibilities;
* technologies;
* education;
* certifications;
* achievements;
* dates;
* locations;
* job titles;
* years of experience;
* business results.

You may improve wording, ordering, emphasis, and structure, but you must not add unsupported facts.

Do not:

* invent employers, projects, technologies, responsibilities, metrics, certifications, degrees, clients, industries, or achievements;
* increase years of experience beyond what the source supports;
* turn exposure into expertise;
* turn collaboration into ownership or leadership;
* turn maintenance into greenfield development;
* claim production use when only experimentation is supported;
* claim exact business impact without evidence;
* change official job titles in a misleading way;
* remove important qualifications merely because they are not mentioned in the posting.

When evidence is incomplete, use accurate and appropriately qualified wording. Record the risk in the final JSON when a proposed statement may require human verification.

## Tailoring Strategy

Prioritize changes that improve both recruiter relevance and ATS matching.

### Professional Summary

Rewrite the summary so it:

* clearly identifies the candidate’s professional level and primary role;
* reflects the most relevant technical and business strengths;
* includes important job-description terminology only when supported;
* communicates value in a natural, human-readable way;
* avoids generic claims, keyword stuffing, clichés, and unsupported superlatives.

Keep the summary concise and specific.

### Skills

Preserve the existing skill categories exactly as they appear in the source resume.

Do not:

* rename skill categories;
* add new skill categories;
* remove skill categories;
* merge categories;
* split categories;
* move a skill into a different category unless the source resume clearly places it incorrectly.

Within each existing category, reorder the skills according to their relevance and order of appearance in the job description. Skills emphasized earliest or most strongly in the job offer should generally appear first.

Ensure that all important job-offer skills are represented in the appropriate existing skill category when the source resume or professional-experience evidence truthfully supports them.

A skill may be added to the Skills section only when:

* it is explicitly supported by the source resume;
* it is clearly demonstrated in an experience or project entry; or
* it is a standard alternative name or abbreviation for an already documented skill.

Do not add unsupported skills merely because they appear in the job offer.

Mark every skill newly added to the Skills section by enclosing it in parentheses.

Example:

`Languages & Frameworks: C#, .NET, TypeScript, Angular, (NestJS)`

The parentheses indicate that the skill was added during tailoring. Do not place parentheses around skills that were already present in the source Skills section, even when they are reordered or renamed slightly.

When a newly added skill requires both a common name and an abbreviation, keep the entire added entry inside one pair of parentheses.

Examples:

* `(Amazon Web Services (AWS))`
* `(Continuous Integration and Continuous Delivery (CI/CD))`
* `(Electronic Data Interchange (EDI))`

Avoid nested parentheses when they would reduce readability. In such cases, use a clear alternative format such as:

* `(AWS — Amazon Web Services)`
* `(CI/CD — Continuous Integration and Continuous Delivery)`

Use conventional, ATS-searchable terminology. Where useful, include both the common abbreviation and expanded term without unnatural duplication.

The final skill ordering should follow this priority:

1. required skills from the job offer, in the order presented or emphasized;
2. preferred skills from the job offer, in the order presented or emphasized;
3. other relevant skills already present in the source resume;
4. remaining truthful skills in their original relative order.

When multiple job offers are supplied, order skills according to:

1. skills required by multiple offers;
2. skills most strongly emphasized across the offers;
3. skills required by the primary or most relevant offer;
4. preferred or secondary skills;
5. remaining source-resume skills.

Do not delete truthful existing skills solely because they are absent from the job offer. Less relevant skills may be moved later within their existing category.

Record every newly added parenthesized skill as a substantive change in the final JSON audit trail. The corresponding change must identify:

* the skill category;
* the added skill;
* the source-resume evidence supporting it;
* the job-description requirement or terminology it aligns with;
* any ambiguity or truthfulness risk.

If an important job-offer skill cannot be supported by the source resume, do not add it. Instead, include it in `warnings` as a potentially missing qualification requiring human review.

### Professional Experience

Prioritize bullets that best demonstrate the requirements of the target role.

For each relevant bullet:

* begin with a clear action or responsibility;
* identify what was built, improved, integrated, maintained, or delivered;
* mention relevant technologies naturally;
* explain the technical or business purpose;
* include measurable results only when supported;
* preserve enough context for a recruiter to understand the scope.

Prefer evidence-based wording over self-evaluation.

Good:

* Developed and maintained .NET and Angular applications supporting business-critical EDI workflows.

Avoid:

* Highly skilled expert who successfully developed world-class applications.

Use present tense for current responsibilities and past tense for previous roles, unless the source resume consistently follows another intentional convention.

Do not force every job-description keyword into the resume. Include a keyword only where it accurately describes the candidate’s experience.

### Projects

Emphasize projects that provide direct evidence for the target role, especially when they demonstrate:

* relevant technologies;
* architecture or system-design decisions;
* ownership;
* open-source work;
* automation;
* testing;
* reliability;
* integrations;
* developer tooling;
* business-critical systems.

Do not present unfinished or experimental work as a completed production system.

### Education and Certifications

Preserve all truthful entries.

Do not infer equivalencies, accreditation, honors, or certification status that are not present in the source resume.

## Recruiter Readability

The rendered resume should be easy to scan quickly.

Use:

* a clear professional headline;
* concise section headings;
* consistent date and location formatting;
* strong information hierarchy;
* concise bullets;
* relevant details near the beginning of each section;
* natural language that a recruiter can understand without decoding excessive jargon.

Avoid:

* dense paragraphs;
* repetitive bullets;
* vague adjectives;
* first-person pronouns;
* excessive buzzwords;
* oversized skill inventories;
* decorative content that competes with professional information;
* repeating the same claim in the summary, skills, and multiple experience bullets.

The first page should contain the strongest evidence for the target role.

Do not reduce readability merely to force the resume into a specific page count. Preserve the existing approximate length unless a small adjustment clearly improves relevance and readability.

## ATS and PDF Text-Extraction Requirements

Preserve or improve ATS compatibility.

The final LaTeX should produce a PDF with a clean, logical text stream.

Use or preserve:

* standard section names such as `Summary`, `Skills`, `Professional Experience`, `Projects`, `Education`, and `Certifications`;
* selectable text rather than text rendered as images;
* Unicode mappings such as `glyphtounicode` and `\pdfgentounicode=1` when already supported by the template;
* conventional left-to-right reading order;
* visible text for important links and contact information;
* simple bullet structures;
* consistent headings and date formatting.

Avoid introducing:

* text boxes;
* multi-column layouts that produce an incorrect reading order;
* important content in headers or footers only;
* icons without accompanying readable text;
* tables that interleave unrelated content in the extracted text;
* hidden keywords;
* white text;
* zero-size text;
* repeated keyword blocks;
* graphics containing essential resume content;
* manual spacing that causes words to merge during copy and paste.

Preserve the template’s visual design unless a change is necessary for readability, ATS parsing, or correct PDF text extraction.

Verify that adjacent entries and sections remain separated in the PDF text stream. In particular, prevent the final text of one list or job entry from merging with the first text of the next entry.

## LaTeX Preservation and Validation

Preserve the complete compilable LaTeX document.

Do not:

* replace the document with fragments;
* remove required packages or custom commands without accounting for their usage;
* alter contact details, URLs, dates, employer names, or project names unless correcting an evident formatting issue;
* introduce unsupported packages unnecessarily;
* insert Markdown into the LaTeX file.

Before completing the task, inspect the resulting file for:

* balanced environments and braces;
* valid LaTeX control sequences;
* unresolved placeholders;
* accidental Markdown syntax;
* duplicated sections;
* missing resume content;
* incorrect file paths;
* obvious compilation errors;
* text-stream collisions between sections or entries.

Compile the resume when a suitable LaTeX compiler is available. If compilation succeeds, inspect the extracted PDF text when practical to confirm:

* correct reading order;
* no merged words between entries;
* no missing contact information;
* no repeated or scrambled sections;
* no essential content lost during extraction.

If compilation or PDF-text validation cannot be performed, report that limitation in `warnings`.

When inspecting LaTeX control sequences with `rg`, search for literal strings rather than regular-expression patterns.

Example:

```bash
rg -n -F \
  -e '\begin{document}' \
  -e '\end{document}' \
  -e '\section*' \
  -e '\newpage' \
  new.tex
```

## Required File Output

Write the complete tailored LaTeX resume to:

`{{OUTPUT_RESUME}}`

The output file must contain the full document, from `\documentclass` through `\end{document}`.

Do not place the LaTeX source in the final assistant response.

## Final Response Format

The file output and final assistant response are separate deliverables.

After writing the resume file, return only valid JSON in the final assistant response.

Do not:

* wrap the JSON in Markdown fences;
* add introductory or closing prose;
* include comments;
* include trailing commas;
* include the LaTeX resume in the JSON.

The JSON must conform to the provided output schema.

Use:

* `"schema_version": "1.0"`;
* a lowercase, hyphenated `slug` in the form `<shortened-company-name>-<shortened-position>`;
* `{{OUTPUT_RESUME}}` in `target_files`;
* `changes` as the final top-level JSON property.

## Change Audit Requirements

Report only meaningful, substantive resume edits.

Do not report:

* punctuation-only changes;
* whitespace-only changes;
* line wrapping;
* indentation;
* purely visual spacing changes;
* changes made only to preserve compilation.

Each item in `changes` must include:

* a stable identifier;
* the resume section;
* a practical location hint;
* the change type;
* a useful before snippet;
* a useful after snippet;
* the job-alignment reason;
* evidence from the source resume or fetched job descriptions;
* any truthfulness, ambiguity, or evidence risk.

Use concise snippets that are specific enough for a human reviewer to identify the edit.

Stable change identifiers should be deterministic and descriptive, for example:

* `summary-role-positioning`
* `skills-cloud-reordering`
* `experience-acme-api-alignment`
* `project-cyclestone-automation-emphasis`

Do not generate random identifiers.

Use `warnings` for:

* job-offer URLs that could not be fetched;
* missing or ambiguous evidence;
* unsupported keywords found in a posting;
* statements that should not be strengthened without human review;
* unavailable compilation or PDF-text validation;
* conflicts among multiple job descriptions;
* job requirements the candidate does not appear to meet.

Warnings should be factual and actionable. Do not hide evidence gaps by omitting them from both the resume and the audit trail.

## Completion Criteria

The task is complete only when:

1. every accessible job-offer URL has been fetched and evaluated;
2. the source resume has been read;
3. the complete tailored LaTeX document has been written to `{{OUTPUT_RESUME}}`;
4. the resume remains truthful and compilable to the extent validation is available;
5. the content is readable for recruiters;
6. the structure and text stream are suitable for ATS parsing;
7. the final response contains only schema-conforming JSON;
8. `changes` is the final top-level JSON property.
