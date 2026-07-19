import datetime as dt
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import make_my_resume_fit


def valid_changes_payload(target_file="new.tex"):
    return {
        "schema_version": "1.0",
        "slug": "example-python-engineer",
        "summary": "Tailored the resume toward the supplied job offer.",
        "target_files": [target_file],
        "warnings": [],
        "changes": [
            {
                "id": "change-001",
                "section": "Experience",
                "location_hint": "First role bullet list",
                "change_type": "rewrite",
                "before": "Built internal tools.",
                "after": "Built Python automation tools for operations teams.",
                "reason": "Aligns the resume with the posting's Python automation requirement.",
                "evidence": "Source resume mentions internal tools; job posting mentions Python.",
                "truthfulness_risk": "Low; does not add unsupported employers or credentials.",
            }
        ],
    }


class ParserTests(unittest.TestCase):
    def test_repeated_job_offer_arguments_are_collected(self):
        parser = make_my_resume_fit.build_parser()

        args = parser.parse_args(
            [
                "--original-resume",
                "resume.tex",
                "--job-offer",
                "https://example.com/a",
                "--job-offer",
                "https://example.com/b",
                "--output-folder",
                "out",
                "--output-name",
                "tailored-resume",
            ]
        )

        self.assertEqual(
            args.job_offers,
            ["https://example.com/a", "https://example.com/b"],
        )
        self.assertEqual(args.output_name, "tailored-resume")


class ValidationTests(unittest.TestCase):
    def test_validate_resume_path_requires_existing_tex_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            resume = root / "resume.tex"
            resume.write_text("% resume", encoding="utf-8")

            self.assertEqual(make_my_resume_fit.validate_resume_path(resume), resume.resolve())

            with self.assertRaisesRegex(ValueError, "must be a .tex file"):
                other = root / "resume.pdf"
                other.write_text("pdf", encoding="utf-8")
                make_my_resume_fit.validate_resume_path(other)

            with self.assertRaisesRegex(ValueError, "does not exist"):
                make_my_resume_fit.validate_resume_path(root / "missing.tex")

    def test_validate_resume_path_rejects_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "not a file"):
                make_my_resume_fit.validate_resume_path(Path(tmp))

    def test_ensure_output_folder_creates_directory_and_rejects_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "nested" / "out"

            self.assertEqual(make_my_resume_fit.ensure_output_folder(output), output.resolve())
            self.assertTrue(output.is_dir())

            file_path = root / "not-a-directory"
            file_path.write_text("content", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "not a directory"):
                make_my_resume_fit.ensure_output_folder(file_path)

    def test_build_output_resume_filename_requires_stem_only(self):
        self.assertEqual(
            make_my_resume_fit.build_output_resume_filename("tailored-resume"),
            "tailored-resume.tex",
        )
        self.assertEqual(
            make_my_resume_fit.build_output_resume_filename("  My Resume  "),
            "My Resume.tex",
        )

        invalid_names = [
            ("", "must not be empty"),
            ("resume.tex", "must not include a file extension"),
            ("nested/resume", "must not contain path separators"),
            (r"nested\\resume", "must not contain path separators"),
            ("..", "directory reference"),
        ]
        for output_name, message in invalid_names:
            with self.subTest(output_name=output_name):
                with self.assertRaisesRegex(ValueError, message):
                    make_my_resume_fit.build_output_resume_filename(output_name)

    def test_create_run_workspace_copies_resume_to_timestamped_temp_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            resume = root / "resume.tex"
            resume.write_text("% source resume", encoding="utf-8")

            run_dir = make_my_resume_fit.create_run_workspace(
                resume,
                temp_root=root / "temp",
                timestamp=dt.datetime(2026, 7, 18, 12, 34, 56, 123456),
            )

            self.assertEqual(
                run_dir.name,
                "make-my-resume-fit-20260718T123456123456",
            )
            self.assertEqual(run_dir.parent, (root / "temp").resolve())
            self.assertEqual(
                (run_dir / make_my_resume_fit.ORIGINAL_RESUME_FILENAME).read_text(
                    encoding="utf-8"
                ),
                "% source resume",
            )

    def test_create_run_workspace_adds_suffix_for_name_collision(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            resume = root / "resume.tex"
            resume.write_text("% source resume", encoding="utf-8")
            timestamp = dt.datetime(2026, 7, 18, 12, 34, 56, 123456)

            first = make_my_resume_fit.create_run_workspace(
                resume,
                temp_root=root,
                timestamp=timestamp,
            )
            second = make_my_resume_fit.create_run_workspace(
                resume,
                temp_root=root,
                timestamp=timestamp,
            )

            self.assertEqual(first.name, "make-my-resume-fit-20260718T123456123456")
            self.assertEqual(second.name, "make-my-resume-fit-20260718T123456123456-01")


class RenderingTests(unittest.TestCase):
    def test_render_template_replaces_all_placeholders(self):
        template = (
            "Resume: {{INPUT_RESUME}}\n"
            "Jobs:\n{{JOB_OFFER_URLS}}\n"
            "Output: {{OUTPUT_RESUME}}\n"
        )

        rendered = make_my_resume_fit.render_template(
            template,
            input_resume="orig.tex",
            job_offers=["https://example.com/a", "https://example.com/b"],
            output_resume="new.tex",
        )

        self.assertIn("Resume: orig.tex", rendered)
        self.assertIn("- https://example.com/a\n- https://example.com/b", rendered)
        self.assertIn("Output: new.tex", rendered)
        self.assertNotIn("/tmp/resume.tex", rendered)
        self.assertNotIn("/tmp/out", rendered)
        self.assertNotRegex(rendered, make_my_resume_fit.UNRESOLVED_PLACEHOLDER_RE)

    def test_render_template_rejects_unresolved_placeholders(self):
        with self.assertRaisesRegex(ValueError, "unresolved placeholders"):
            make_my_resume_fit.render_template(
                "{{INPUT_RESUME}} {{UNKNOWN}}",
                input_resume="orig.tex",
                job_offers=["https://example.com/a"],
                output_resume="new.tex",
            )

    def test_rendered_prompt_tells_codex_to_search_latex_markers_literally(self):
        rendered = make_my_resume_fit.render_template(
            make_my_resume_fit.load_template(),
            input_resume="orig.tex",
            job_offers=["https://example.com/a"],
            output_resume="new.tex",
        )

        self.assertIn("rg -n -F", rendered)
        self.assertIn("-e '\\begin{document}'", rendered)
        self.assertIn("-e '\\section*'", rendered)

    def test_rendered_prompt_tells_codex_to_fetch_job_offer_urls(self):
        rendered = make_my_resume_fit.render_template(
            make_my_resume_fit.load_template(),
            input_resume="orig.tex",
            job_offers=["https://example.com/a"],
            output_resume="new.tex",
        )

        self.assertIn("Fetch and read every supplied job-offer URL", rendered)
        self.assertIn("fetched job descriptions", rendered)
        self.assertIn("use any available live-search or browser tools", rendered)
        self.assertNotIn("Do not fetch or validate", rendered)

    def test_rendered_prompt_separates_resume_file_from_final_json_response(self):
        rendered = make_my_resume_fit.render_template(
            make_my_resume_fit.load_template(),
            input_resume="orig.tex",
            job_offers=["https://example.com/a"],
            output_resume="new.tex",
        )

        self.assertIn("Write the complete tailored LaTeX resume to:\n\n`new.tex`", rendered)
        self.assertIn("return only valid JSON in the final assistant response", rendered)
        self.assertIn("lowercase, hyphenated `slug`", rendered)
        self.assertIn("`changes` as the final top-level JSON property", rendered)
        self.assertIn("truthfulness, ambiguity, or evidence risk", rendered)
        self.assertIn("punctuation-only", rendered)


class CodexInvocationTests(unittest.TestCase):
    def test_build_codex_command_sandboxes_temp_run_dir_only(self):
        schema = str(make_my_resume_fit.METADATA_SCHEMA_PATH.resolve())
        self.assertEqual(
            make_my_resume_fit.build_codex_command(Path("/tmp/run")),
            [
                "codex",
                "--search",
                "-c",
                "sandbox_workspace_write.network_access=true",
                "exec",
                "--sandbox",
                "workspace-write",
                "--skip-git-repo-check",
                "-C",
                "/tmp/run",
                "--output-schema",
                schema,
                "-o",
                "/tmp/run/metadata.json",
                "-",
            ],
        )

    def test_build_codex_command_omits_original_resume_repo_and_output_paths(self):
        command = make_my_resume_fit.build_codex_command(Path("/tmp/run"))

        self.assertNotIn("/tmp/source/resume.tex", command)
        self.assertNotIn("/tmp/project", command)
        self.assertNotIn("/tmp/out", command)
        self.assertNotIn("--add-dir", command)

    def test_invoke_codex_passes_prompt_on_stdin(self):
        schema = str(make_my_resume_fit.METADATA_SCHEMA_PATH.resolve())
        with mock.patch("make_my_resume_fit.subprocess.run") as run:
            run.return_value = subprocess.CompletedProcess(
                args=make_my_resume_fit.build_codex_command(Path("/tmp/run")),
                returncode=0,
            )

            make_my_resume_fit.invoke_codex("rendered prompt", run_dir=Path("/tmp/run"))

        run.assert_called_once_with(
            [
                "codex",
                "--search",
                "-c",
                "sandbox_workspace_write.network_access=true",
                "exec",
                "--sandbox",
                "workspace-write",
                "--skip-git-repo-check",
                "-C",
                "/tmp/run",
                "--output-schema",
                schema,
                "-o",
                "/tmp/run/metadata.json",
                "-",
            ],
            input="rendered prompt",
            text=True,
            check=False,
        )

    def test_invoke_codex_reports_missing_executable(self):
        with mock.patch("make_my_resume_fit.subprocess.run", side_effect=FileNotFoundError):
            with self.assertRaisesRegex(make_my_resume_fit.CodexInvocationError, "not found"):
                make_my_resume_fit.invoke_codex("prompt", run_dir=Path("/tmp/run"))

    def test_invoke_codex_reports_nonzero_exit(self):
        with mock.patch("make_my_resume_fit.subprocess.run") as run:
            run.return_value = subprocess.CompletedProcess(
                args=make_my_resume_fit.build_codex_command(Path("/tmp/run")),
                returncode=7,
            )

            with self.assertRaisesRegex(make_my_resume_fit.CodexInvocationError, "exit code 7"):
                make_my_resume_fit.invoke_codex("prompt", run_dir=Path("/tmp/run"))

    def test_validate_generated_resume_requires_new_tex_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)

            with self.assertRaisesRegex(
                make_my_resume_fit.CodexInvocationError,
                "without producing new.tex",
            ):
                make_my_resume_fit.validate_generated_resume(run_dir)

            generated = run_dir / make_my_resume_fit.TAILORED_RESUME_FILENAME
            generated.write_text("% tailored", encoding="utf-8")
            self.assertEqual(make_my_resume_fit.validate_generated_resume(run_dir), generated)

    def test_validate_generated_resume_uses_requested_output_filename(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)

            with self.assertRaisesRegex(
                make_my_resume_fit.CodexInvocationError,
                "without producing tailored-resume.tex",
            ):
                make_my_resume_fit.validate_generated_resume(run_dir, "tailored-resume.tex")

            generated = run_dir / "tailored-resume.tex"
            generated.write_text("% tailored", encoding="utf-8")
            self.assertEqual(
                make_my_resume_fit.validate_generated_resume(run_dir, "tailored-resume.tex"),
                generated,
            )

    def test_validate_metadata_json_accepts_schema_matching_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            metadata_path = Path(tmp) / "metadata.json"
            metadata_path.write_text(
                json.dumps(valid_changes_payload()),
                encoding="utf-8",
            )

            self.assertEqual(
                make_my_resume_fit.validate_metadata_json(metadata_path),
                valid_changes_payload(),
            )

    def test_validate_metadata_json_requires_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(
                make_my_resume_fit.CodexInvocationError,
                "structured output metadata.json",
            ):
                make_my_resume_fit.validate_metadata_json(Path(tmp) / "metadata.json")

    def test_validate_metadata_json_rejects_empty_or_malformed_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            metadata_path = Path(tmp) / "metadata.json"

            metadata_path.write_text("   \n", encoding="utf-8")
            with self.assertRaisesRegex(make_my_resume_fit.CodexInvocationError, "empty"):
                make_my_resume_fit.validate_metadata_json(metadata_path)

            metadata_path.write_text("{not json", encoding="utf-8")
            with self.assertRaisesRegex(make_my_resume_fit.CodexInvocationError, "malformed JSON"):
                make_my_resume_fit.validate_metadata_json(metadata_path)

    def test_validate_metadata_json_rejects_schema_violations(self):
        with tempfile.TemporaryDirectory() as tmp:
            metadata_path = Path(tmp) / "metadata.json"
            payload = valid_changes_payload()
            del payload["changes"][0]["truthfulness_risk"]
            metadata_path.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaisesRegex(
                make_my_resume_fit.CodexInvocationError,
                "does not match schema",
            ):
                make_my_resume_fit.validate_metadata_json(metadata_path)

            payload = valid_changes_payload()
            payload["warnings"] = "none"
            metadata_path.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaisesRegex(
                make_my_resume_fit.CodexInvocationError,
                r"\$\.warnings must be an array",
            ):
                make_my_resume_fit.validate_metadata_json(metadata_path)

    def test_validate_metadata_json_requires_slug(self):
        with tempfile.TemporaryDirectory() as tmp:
            metadata_path = Path(tmp) / "metadata.json"
            payload = valid_changes_payload()
            del payload["slug"]
            metadata_path.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaisesRegex(
                make_my_resume_fit.CodexInvocationError,
                r"\$\.slug is required",
            ):
                make_my_resume_fit.validate_metadata_json(metadata_path)

    def test_validate_metadata_json_rejects_non_slug_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            metadata_path = Path(tmp) / "metadata.json"
            payload = valid_changes_payload()
            payload["slug"] = "Example Python Engineer"
            metadata_path.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaisesRegex(
                make_my_resume_fit.CodexInvocationError,
                r"\$\.slug must match pattern",
            ):
                make_my_resume_fit.validate_metadata_json(metadata_path)


class PublicationTests(unittest.TestCase):
    def test_copy_final_artifacts_writes_dated_versioned_archive_from_metadata_slug(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            generated = root / "new.tex"
            original = root / "orig.tex"
            output = root / "out"
            generated.write_text("% tailored", encoding="utf-8")
            original.write_text("% original", encoding="utf-8")
            metadata = valid_changes_payload()

            archive = make_my_resume_fit.copy_final_artifacts(
                generated,
                original,
                metadata,
                output,
                current_date=dt.date(2026, 7, 18),
            )

            self.assertEqual(
                archive,
                (output / "2026-07-18-v1-example-python-engineer").resolve(),
            )
            self.assertEqual((archive / "new.tex").read_text(encoding="utf-8"), "% tailored")
            self.assertEqual((archive / "orig.tex").read_text(encoding="utf-8"), "% original")
            metadata_text = (archive / "metadata.json").read_text(encoding="utf-8")
            self.assertEqual(json.loads(metadata_text), metadata)
            self.assertEqual(list(json.loads(metadata_text).keys())[-1], "changes")
            self.assertFalse((output / "new.tex").exists())
            self.assertFalse((output / "orig.tex").exists())
            self.assertFalse((output / "metadata.json").exists())

    def test_create_archive_directory_uses_next_version_without_modifying_existing(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "out"
            existing = output / "2026-07-18-v1-example-python-engineer"
            existing.mkdir(parents=True)
            sentinel = existing / "sentinel.txt"
            sentinel.write_text("keep", encoding="utf-8")

            archive = make_my_resume_fit.create_archive_directory(
                output,
                "example-python-engineer",
                current_date=dt.date(2026, 7, 18),
            )

            self.assertEqual(
                archive,
                (output / "2026-07-18-v2-example-python-engineer").resolve(),
            )
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")

    def test_copy_final_artifacts_rejects_unusable_slug_before_creating_output_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            generated = root / "new.tex"
            original = root / "orig.tex"
            output = root / "out"
            generated.write_text("% tailored", encoding="utf-8")
            original.write_text("% original", encoding="utf-8")
            metadata = valid_changes_payload()
            metadata["slug"] = ""

            with self.assertRaisesRegex(make_my_resume_fit.CodexInvocationError, "usable slug"):
                make_my_resume_fit.copy_final_artifacts(
                    generated,
                    original,
                    metadata,
                    output,
                    current_date=dt.date(2026, 7, 18),
                )

            self.assertFalse(output.exists())

    def test_create_archive_directory_rejects_existing_output_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "out"
            output.write_text("not a directory", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "not a directory"):
                make_my_resume_fit.create_archive_directory(
                    output,
                    "example-python-engineer",
                    current_date=dt.date(2026, 7, 18),
                )


class RunTests(unittest.TestCase):
    def test_run_validates_renders_invokes_and_copies_new_tex(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            resume = root / "resume.tex"
            output = root / "out"
            resume.write_text("% resume", encoding="utf-8")

            def write_generated_resume(prompt, *, run_dir):
                (run_dir / "tailored-resume.tex").write_text(
                    "% tailored",
                    encoding="utf-8",
                )
                (run_dir / make_my_resume_fit.METADATA_FILENAME).write_text(
                    json.dumps(valid_changes_payload("tailored-resume.tex")),
                    encoding="utf-8",
                )

            create_run_workspace = make_my_resume_fit.create_run_workspace

            def create_test_workspace(original_resume):
                return create_run_workspace(
                    original_resume,
                    temp_root=root / "runs",
                    timestamp=dt.datetime(2026, 7, 18, 12, 34, 56, 123456),
                )

            class FixedDate(dt.date):
                @classmethod
                def today(cls):
                    return cls(2026, 7, 18)

            with mock.patch(
                "make_my_resume_fit.create_run_workspace",
                side_effect=create_test_workspace,
            ), mock.patch(
                "make_my_resume_fit.invoke_codex",
                side_effect=write_generated_resume,
            ) as invoke, mock.patch(
                "make_my_resume_fit.dt.date",
                FixedDate,
            ):
                exit_code = make_my_resume_fit.run(
                    [
                        "--original-resume",
                        str(resume),
                        "--job-offer",
                        "https://example.com/a",
                        "--output-folder",
                        str(output),
                        "--output-name",
                        "tailored-resume",
                    ]
                )

                self.assertEqual(exit_code, 0)
                self.assertTrue(output.is_dir())
                archive = output / "2026-07-18-v1-example-python-engineer"
                self.assertTrue(archive.is_dir())
                self.assertEqual(
                    (archive / "tailored-resume.tex").read_text(encoding="utf-8"),
                    "% tailored",
                )
                self.assertEqual((archive / "orig.tex").read_text(encoding="utf-8"), "% resume")
                metadata_text = (archive / "metadata.json").read_text(encoding="utf-8")
                self.assertEqual(
                    json.loads(metadata_text),
                    valid_changes_payload("tailored-resume.tex"),
                )
                self.assertEqual(list(json.loads(metadata_text).keys())[-1], "changes")
                self.assertFalse((output / "tailored-resume.tex").exists())
                self.assertFalse((output / "orig.tex").exists())
                self.assertFalse((output / "metadata.json").exists())
                run_dir = invoke.call_args.kwargs["run_dir"]
                self.assertEqual((run_dir / "orig.tex").read_text(encoding="utf-8"), "% resume")
                prompt = invoke.call_args.args[0]
                self.assertIn("orig.tex", prompt)
                self.assertIn("tailored-resume.tex", prompt)
                self.assertIn("- https://example.com/a", prompt)
                self.assertNotIn(str(resume.resolve()), prompt)
                self.assertNotIn(str(output.resolve()), prompt)
                invoke.assert_called_once()
                self.assertEqual(invoke.call_args.kwargs["run_dir"], run_dir)

    def test_run_reports_missing_metadata_json_after_successful_codex(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            resume = root / "resume.tex"
            output = root / "out"
            resume.write_text("% resume", encoding="utf-8")

            def write_generated_resume(prompt, *, run_dir):
                (run_dir / "tailored-resume.tex").write_text(
                    "% tailored",
                    encoding="utf-8",
                )

            create_run_workspace = make_my_resume_fit.create_run_workspace

            def create_test_workspace(original_resume):
                return create_run_workspace(
                    original_resume,
                    temp_root=root / "runs",
                    timestamp=dt.datetime(2026, 7, 18, 12, 34, 56, 123456),
                )

            with mock.patch(
                "make_my_resume_fit.create_run_workspace",
                side_effect=create_test_workspace,
            ), mock.patch(
                "make_my_resume_fit.invoke_codex",
                side_effect=write_generated_resume,
            ):
                exit_code = make_my_resume_fit.run(
                    [
                        "--original-resume",
                        str(resume),
                        "--job-offer",
                        "https://example.com/a",
                        "--output-folder",
                        str(output),
                        "--output-name",
                        "tailored-resume",
                    ]
                )

                self.assertEqual(exit_code, 1)
                self.assertFalse(output.exists())

    def test_run_reports_malformed_metadata_json_without_creating_output_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            resume = root / "resume.tex"
            output = root / "out"
            resume.write_text("% resume", encoding="utf-8")

            def write_malformed_outputs(prompt, *, run_dir):
                (run_dir / "tailored-resume.tex").write_text(
                    "% tailored",
                    encoding="utf-8",
                )
                (run_dir / make_my_resume_fit.METADATA_FILENAME).write_text(
                    "{not json",
                    encoding="utf-8",
                )

            create_run_workspace = make_my_resume_fit.create_run_workspace

            def create_test_workspace(original_resume):
                return create_run_workspace(
                    original_resume,
                    temp_root=root / "runs",
                    timestamp=dt.datetime(2026, 7, 18, 12, 34, 56, 123456),
                )

            with mock.patch(
                "make_my_resume_fit.create_run_workspace",
                side_effect=create_test_workspace,
            ), mock.patch(
                "make_my_resume_fit.invoke_codex",
                side_effect=write_malformed_outputs,
            ):
                exit_code = make_my_resume_fit.run(
                    [
                        "--original-resume",
                        str(resume),
                        "--job-offer",
                        "https://example.com/a",
                        "--output-folder",
                        str(output),
                        "--output-name",
                        "tailored-resume",
                    ]
                )

                self.assertEqual(exit_code, 1)
                self.assertFalse(output.exists())

    def test_run_reports_invalid_metadata_json_after_successful_codex(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            resume = root / "resume.tex"
            output = root / "out"
            resume.write_text("% resume", encoding="utf-8")

            def write_invalid_outputs(prompt, *, run_dir):
                (run_dir / "tailored-resume.tex").write_text(
                    "% tailored",
                    encoding="utf-8",
                )
                (run_dir / make_my_resume_fit.METADATA_FILENAME).write_text(
                    '{"schema_version": "1.0"}',
                    encoding="utf-8",
                )

            create_run_workspace = make_my_resume_fit.create_run_workspace

            def create_test_workspace(original_resume):
                return create_run_workspace(
                    original_resume,
                    temp_root=root / "runs",
                    timestamp=dt.datetime(2026, 7, 18, 12, 34, 56, 123456),
                )

            with mock.patch(
                "make_my_resume_fit.create_run_workspace",
                side_effect=create_test_workspace,
            ), mock.patch(
                "make_my_resume_fit.invoke_codex",
                side_effect=write_invalid_outputs,
            ):
                exit_code = make_my_resume_fit.run(
                    [
                        "--original-resume",
                        str(resume),
                        "--job-offer",
                        "https://example.com/a",
                        "--output-folder",
                        str(output),
                        "--output-name",
                        "tailored-resume",
                    ]
                )

                self.assertEqual(exit_code, 1)
                self.assertFalse(output.exists())

    def test_run_reports_missing_new_tex_after_successful_codex(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            resume = root / "resume.tex"
            output = root / "out"
            resume.write_text("% resume", encoding="utf-8")

            create_run_workspace = make_my_resume_fit.create_run_workspace

            def create_test_workspace(original_resume):
                return create_run_workspace(
                    original_resume,
                    temp_root=root / "runs",
                    timestamp=dt.datetime(2026, 7, 18, 12, 34, 56, 123456),
                )

            with mock.patch(
                "make_my_resume_fit.create_run_workspace",
                side_effect=create_test_workspace,
            ), mock.patch("make_my_resume_fit.invoke_codex"):
                exit_code = make_my_resume_fit.run(
                    [
                        "--original-resume",
                        str(resume),
                        "--job-offer",
                        "https://example.com/a",
                        "--output-folder",
                        str(output),
                        "--output-name",
                        "tailored-resume",
                    ]
                )

                self.assertEqual(exit_code, 1)
                self.assertFalse(output.exists())
                self.assertTrue((root / "runs").exists())

    def test_run_rejects_existing_output_file_before_final_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            resume = root / "resume.tex"
            output = root / "out"
            resume.write_text("% resume", encoding="utf-8")
            output.write_text("not a directory", encoding="utf-8")

            def write_generated_resume(prompt, *, run_dir):
                (run_dir / "tailored-resume.tex").write_text(
                    "% tailored",
                    encoding="utf-8",
                )
                (run_dir / make_my_resume_fit.METADATA_FILENAME).write_text(
                    json.dumps(valid_changes_payload("tailored-resume.tex")),
                    encoding="utf-8",
                )

            create_run_workspace = make_my_resume_fit.create_run_workspace

            def create_test_workspace(original_resume):
                return create_run_workspace(
                    original_resume,
                    temp_root=root / "runs",
                    timestamp=dt.datetime(2026, 7, 18, 12, 34, 56, 123456),
                )

            with mock.patch(
                "make_my_resume_fit.create_run_workspace",
                side_effect=create_test_workspace,
            ), mock.patch(
                "make_my_resume_fit.invoke_codex",
                side_effect=write_generated_resume,
            ):
                with self.assertRaises(SystemExit):
                    make_my_resume_fit.run(
                        [
                            "--original-resume",
                            str(resume),
                            "--job-offer",
                            "https://example.com/a",
                            "--output-folder",
                            str(output),
                            "--output-name",
                            "tailored-resume",
                        ]
                    )


if __name__ == "__main__":
    unittest.main()
