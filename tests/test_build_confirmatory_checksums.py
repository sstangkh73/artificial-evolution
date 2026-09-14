import hashlib
import tempfile
import unittest
from pathlib import Path

from scripts.build_confirmatory_checksums import build_manifest, collect_files


class ConfirmatoryChecksumTests(unittest.TestCase):
    def test_manifest_is_sorted_and_excludes_itself(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data").mkdir()
            (root / "data" / "b.txt").write_bytes(b"b")
            (root / "data" / "a.txt").write_bytes(b"a")
            output = root / "data" / "checksums.sha256"

            self.assertEqual(build_manifest(root, [Path("data")], output), 2)
            lines = output.read_text(encoding="utf-8").splitlines()
            self.assertEqual(
                lines,
                [
                    f"{hashlib.sha256(b'a').hexdigest()}  data/a.txt",
                    f"{hashlib.sha256(b'b').hexdigest()}  data/b.txt",
                ],
            )

    def test_rejects_files_outside_root(self):
        with tempfile.TemporaryDirectory() as root_dir, tempfile.TemporaryDirectory() as other_dir:
            root = Path(root_dir)
            outside = Path(other_dir) / "outside.txt"
            outside.write_text("x", encoding="utf-8")
            with self.assertRaises(ValueError):
                collect_files(root, [outside], root / "checksums.sha256")


if __name__ == "__main__":
    unittest.main()
