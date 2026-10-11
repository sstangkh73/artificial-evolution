import unittest

from scripts import build_redteam_revision_release_inventory as inventory


class RedteamRevisionReleaseInventoryTests(unittest.TestCase):
    def test_collects_all_revised_publication_documents(self):
        observed = {inventory.relative(path) for path in inventory.collect_artifacts()}
        expected = {
            "reports/publication_value_of_information_2026-09-13/AI_USE_LOG.md",
            "reports/publication_value_of_information_2026-09-13/LITERATURE_EVIDENCE_MATRIX_2026-09-14.md",
            "reports/publication_value_of_information_2026-09-13/ODD_MODEL_DESCRIPTION_DRAFT.en.md",
            "reports/publication_value_of_information_2026-09-13/README.th.md",
            "reports/publication_value_of_information_2026-09-13/SUBMISSION_CHECKLIST_2026-09-14.th.md",
            "reports/publication_value_of_information_2026-09-13/cover_letter_draft.en.md",
            "reports/publication_value_of_information_2026-09-13/manuscript_v0.en.md",
            "reports/publication_value_of_information_2026-09-13/references.bib",
            "reports/publication_value_of_information_2026-09-13/supplement/PUBLIC_ARCHIVE_MANIFEST.en.md",
            "reports/publication_value_of_information_2026-09-13/supplement/MECHANISM_TABLES.en.md",
        }
        self.assertTrue(expected <= observed, expected - observed)

    def test_excludes_self_referential_and_historical_manifests(self):
        observed = {path.resolve() for path in inventory.collect_artifacts()}
        self.assertNotIn(inventory.INVENTORY.resolve(), observed)
        self.assertNotIn(inventory.CHECKSUMS.resolve(), observed)
        self.assertNotIn(inventory.BASELINE.resolve(), observed)


if __name__ == "__main__":
    unittest.main()
