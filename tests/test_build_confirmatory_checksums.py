import hashlib
import tempfile
import unittest
from pathlib import Path

from scripts.build_confirmatory_checksums import build_manifest, collect_files, refresh_manifest


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

    def test_refresh_preserves_existing_path_scope(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data").mkdir()
            tracked = root / "data" / "tracked.txt"
            ignored = root / "data" / "new.txt"
            tracked.write_bytes(b"old")
            ignored.write_bytes(b"new")
            output = root / "checksums.sha256"
            output.write_text(f"{'0' * 64}  data/tracked.txt\n", encoding="utf-8")

            self.assertEqual(refresh_manifest(root, output), 1)
            self.assertEqual(
                output.read_text(encoding="utf-8").splitlines(),
                [f"{hashlib.sha256(b'old').hexdigest()}  data/tracked.txt"],
            )


if __name__ == "__main__":
    unittest.main()
