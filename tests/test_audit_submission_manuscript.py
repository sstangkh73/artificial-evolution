"""Tests for the submission audit's checks on the built manuscript PDF."""

import os
import sys
import unittest
from pathlib import Path

# Make scripts/ importable regardless of cwd.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

import audit_submission_manuscript as audit


TITLE = "When Does a *Better* Representation Pay?"
ABSTRACT = "\n\nArtificial foragers learn `values`.\nA second sentence.\n\n"
RENDERED = "When Does a Better\nRepresentation Pay?\nArtificial foragers learn values.\nA second sentence."


class PdfTextAuditTests(unittest.TestCase):
    def test_word_count_ignores_supported_subscript_markup(self):
        self.assertEqual(audit.words("paired *d*<sub>z</sub> effect"), ["paired", "d", "z", "effect"])

    def test_first_figure_citations_must_be_in_numeric_order(self):
        ordered = "Results cite Figure 1A, then Figure 2, Figure 3, Figure 4, and Figure 5."
        scrambled = "Results cite Figure 2A, then Figure 4, Figure 1, Figure 5, and Figure 3."
        self.assertEqual(audit.first_figure_citation_order(ordered), [1, 2, 3, 4, 5])
        self.assertEqual(audit.first_figure_citation_order(scrambled), [2, 4, 1, 5, 3])

    def test_citation_recognizes_multi_author_apa_forms(self):
        self.assertTrue(audit.cites_record("Dorin and Stepney (2024) distinguish forms.", "Dorin", "2024"))
        self.assertTrue(audit.cites_record("Prior work supports this (Dorin & Stepney, 2024).", "Dorin", "2024"))
        self.assertFalse(audit.cites_record("Dorin and Stepney discuss the field.", "Dorin", "2024"))

    def test_clean_rendering_passes(self):
        result = audit.audit_pdf_text(RENDERED + "\nCodex [Large language model].", TITLE, ABSTRACT)
        self.assertEqual(result["status"], "PASS")
        self.assertTrue(result["matches_manuscript"])

    def test_missing_required_author_metadata_fails(self):
        result = audit.audit_pdf_text(
            RENDERED,
            TITLE,
            ABSTRACT,
            ("Confirmed School", "https://orcid.org/0000-0000-0000-0000"),
        )
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(
            result["missing_author_metadata"],
            ["Confirmed School", "https://orcid.org/0000-0000-0000-0000"],
        )

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

    def test_confidence_interval_is_not_a_placeholder(self):
        self.assertEqual(audit.pdf_placeholders("B2-B3 [95% CI] = -5.431 [-8.826, -2.037]."), [])

    def test_front_matter_leak_is_reported(self):
        text = RENDERED + "\nTarget journal: Artificial Life (final requirements must be\nrechecked at submission)"
        result = audit.audit_pdf_text(text, TITLE, ABSTRACT)
        self.assertEqual(result["internal_notes"], ["Target journal:", "must be rechecked"])
        self.assertEqual(result["status"], "FAIL")

    def test_internal_figure_marker_leak_is_reported(self):
        result = audit.audit_pdf_text(RENDERED + "\nVECTOR_FIGURE_PAGE_3", TITLE, ABSTRACT)
        self.assertEqual(result["internal_notes"], ["VECTOR_FIGURE_PAGE_"])
        self.assertEqual(result["status"], "FAIL")

    def test_stale_pdf_does_not_match_manuscript(self):
        stale = "When Does a Better Representation Pay?\nArtificial foragers learn old values. A second sentence."
        result = audit.audit_pdf_text(stale, TITLE, ABSTRACT)
        self.assertFalse(result["matches_manuscript"])
        self.assertEqual(result["status"], "FAIL")

    def test_missing_pdf_is_reported_not_raised(self):
        absent = Path(__file__).with_name("definitely_absent_submission_test.pdf")
        self.assertFalse(absent.exists())
        result = audit.audit_pdf(absent, TITLE, ABSTRACT)
        self.assertFalse(result["present"])
        self.assertEqual(result["status"], "MISSING")


if __name__ == "__main__":
    unittest.main()
