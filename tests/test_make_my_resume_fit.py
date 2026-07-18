import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import make_my_resume_fit


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
            ]
        )

        self.assertEqual(
            args.job_offers,
            ["https://example.com/a", "https://example.com/b"],
        )


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


class RenderingTests(unittest.TestCase):
    def test_render_template_replaces_all_placeholders(self):
        template = (
            "Resume: {{ORIGINAL_RESUME}}\n"
            "Jobs:\n{{JOB_OFFER_URLS}}\n"
            "Output: {{OUTPUT_FOLDER}}\n"
        )

        rendered = make_my_resume_fit.render_template(
            template,
            original_resume=Path("/tmp/resume.tex"),
            job_offers=["https://example.com/a", "https://example.com/b"],
            output_folder=Path("/tmp/out"),
        )

        self.assertIn("Resume: /tmp/resume.tex", rendered)
        self.assertIn("- https://example.com/a\n- https://example.com/b", rendered)
        self.assertIn("Output: /tmp/out", rendered)
        self.assertNotRegex(rendered, make_my_resume_fit.UNRESOLVED_PLACEHOLDER_RE)

    def test_render_template_rejects_unresolved_placeholders(self):
        with self.assertRaisesRegex(ValueError, "unresolved placeholders"):
            make_my_resume_fit.render_template(
                "{{ORIGINAL_RESUME}} {{UNKNOWN}}",
                original_resume=Path("resume.tex"),
                job_offers=["https://example.com/a"],
                output_folder=Path("out"),
            )


class CodexInvocationTests(unittest.TestCase):
    def test_build_codex_command_is_stable(self):
        self.assertEqual(
            make_my_resume_fit.build_codex_command(Path("/tmp/out")),
            [
                "codex",
                "exec",
                "--sandbox",
                "workspace-write",
                "--add-dir",
                "/tmp/out",
                "-",
            ],
        )

    def test_invoke_codex_passes_prompt_on_stdin(self):
        with mock.patch("make_my_resume_fit.subprocess.run") as run:
            run.return_value = subprocess.CompletedProcess(
                args=make_my_resume_fit.build_codex_command(Path("/tmp/out")),
                returncode=0,
            )

            make_my_resume_fit.invoke_codex("rendered prompt", output_folder=Path("/tmp/out"))

        run.assert_called_once_with(
            [
                "codex",
                "exec",
                "--sandbox",
                "workspace-write",
                "--add-dir",
                "/tmp/out",
                "-",
            ],
            input="rendered prompt",
            text=True,
            check=False,
        )

    def test_invoke_codex_reports_missing_executable(self):
        with mock.patch("make_my_resume_fit.subprocess.run", side_effect=FileNotFoundError):
            with self.assertRaisesRegex(make_my_resume_fit.CodexInvocationError, "not found"):
                make_my_resume_fit.invoke_codex("prompt", output_folder=Path("/tmp/out"))

    def test_invoke_codex_reports_nonzero_exit(self):
        with mock.patch("make_my_resume_fit.subprocess.run") as run:
            run.return_value = subprocess.CompletedProcess(
                args=make_my_resume_fit.build_codex_command(Path("/tmp/out")),
                returncode=7,
            )

            with self.assertRaisesRegex(make_my_resume_fit.CodexInvocationError, "exit code 7"):
                make_my_resume_fit.invoke_codex("prompt", output_folder=Path("/tmp/out"))


class RunTests(unittest.TestCase):
    def test_run_validates_renders_and_invokes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            resume = root / "resume.tex"
            output = root / "out"
            resume.write_text("% resume", encoding="utf-8")

            with mock.patch("make_my_resume_fit.invoke_codex") as invoke:
                exit_code = make_my_resume_fit.run(
                    [
                        "--original-resume",
                        str(resume),
                        "--job-offer",
                        "https://example.com/a",
                        "--output-folder",
                        str(output),
                    ]
                )

                self.assertEqual(exit_code, 0)
                self.assertTrue(output.is_dir())
                prompt = invoke.call_args.args[0]
                self.assertIn(str(resume.resolve()), prompt)
                self.assertIn("- https://example.com/a", prompt)
                self.assertIn(str(output.resolve()), prompt)
                invoke.assert_called_once()
                self.assertEqual(invoke.call_args.kwargs["output_folder"], output.resolve())


if __name__ == "__main__":
    unittest.main()
