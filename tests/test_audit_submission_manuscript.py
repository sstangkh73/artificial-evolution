"""Tests for the submission audit's checks on the built manuscript PDF."""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Make scripts/ importable regardless of cwd.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

import audit_submission_manuscript as audit


TITLE = "When Does a *Better* Representation Pay?"
ABSTRACT = "\n\nArtificial foragers learn `values`.\nA second sentence.\n\n"
RENDERED = "When Does a Better\nRepresentation Pay?\nArtificial foragers learn values.\nA second sentence."


class PdfTextAuditTests(unittest.TestCase):
    def test_clean_rendering_passes(self):
        result = audit.audit_pdf_text(RENDERED + "\nCodex [Large language model].", TITLE, ABSTRACT)
        self.assertEqual(result["status"], "PASS")
        self.assertTrue(result["matches_manuscript"])

    def test_builder_title_page_placeholders_are_reported(self):
        text = RENDERED + "\n[Affiliation]\n[Postal address]\n[Email; corresponding author]"
        result = audit.audit_pdf_text(text, TITLE, ABSTRACT)
        self.assertEqual(
            result["unresolved_placeholders"],
            ["[Affiliation]", "[Email; corresponding author]", "[Postal address]"],
        )
        self.assertEqual(result["status"], "FAIL")

    def test_placeholder_wrapped_across_lines_is_one_entry(self):
        text = "[Author confirmation required. Complete a CRediT\nstatement.]"
        self.assertEqual(
            audit.pdf_placeholders(text),
            ["[Author confirmation required. Complete a CRediT statement.]"],
        )

    def test_apa_descriptor_is_not_a_placeholder(self):
        self.assertEqual(audit.pdf_placeholders("OpenAI. (2026). Codex [Large language model]."), [])

    def test_front_matter_leak_is_reported(self):
        text = RENDERED + "\nTarget journal: Artificial Life (final requirements must be\nrechecked at submission)"
        result = audit.audit_pdf_text(text, TITLE, ABSTRACT)
        self.assertEqual(result["internal_notes"], ["Target journal:", "must be rechecked"])
        self.assertEqual(result["status"], "FAIL")

    def test_stale_pdf_does_not_match_manuscript(self):
        stale = "When Does a Better Representation Pay?\nArtificial foragers learn old values. A second sentence."
        result = audit.audit_pdf_text(stale, TITLE, ABSTRACT)
        self.assertFalse(result["matches_manuscript"])
        self.assertEqual(result["status"], "FAIL")

    def test_missing_pdf_is_reported_not_raised(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = audit.audit_pdf(Path(tmp) / "absent.pdf", TITLE, ABSTRACT)
        self.assertFalse(result["present"])
        self.assertEqual(result["status"], "MISSING")


if __name__ == "__main__":
    unittest.main()
