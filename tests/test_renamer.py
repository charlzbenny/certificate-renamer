"""Unit tests for renamer.py."""
import io
from pathlib import Path
import sys
import unittest
import zipfile

# Ensure project root is in sys.path so renamer can be imported directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from renamer import clean_filename, get_clean_names, prepare_renaming, SUPPORTED_EXTENSIONS


class TestCertificateRenamer(unittest.TestCase):
    def test_clean_filename(self):
        self.assertEqual(clean_filename("Aadya Thakur"), "Aadya Thakur")
        self.assertEqual(clean_filename('Dr. Jane: Doe / Smith *?'), "Dr. Jane Doe Smith")
        self.assertEqual(clean_filename("Trailing Dot..."), "Trailing Dot")
        self.assertEqual(clean_filename("   Multiple    Spaces   "), "Multiple Spaces")

    def test_get_clean_names(self):
        text = "Aadya Thakur\n\nAakash Ganguly\n  \nAarya Prakash\n"
        names = get_clean_names(text)
        self.assertEqual(names, ["Aadya Thakur", "Aakash Ganguly", "Aarya Prakash"])

    def test_successful_matching_and_extension_preservation(self):
        files = [
            ("1.jpg", b"fake_jpg_content_1"),
            ("2.png", b"fake_png_content_2"),
            ("3.webp", b"fake_webp_content_3"),
        ]
        names = "Aadya Thakur\nAakash Ganguly\nAarya Prakash"
        targets, errors, notices = prepare_renaming(files, names)

        self.assertEqual(errors, [])
        self.assertEqual(notices, [])
        self.assertEqual(len(targets), 3)

        self.assertEqual(targets[0]["number"], 1)
        self.assertEqual(targets[0]["source"], "1.jpg")
        self.assertEqual(targets[0]["target"], "Aadya Thakur.jpg")
        self.assertEqual(targets[0]["content"], b"fake_jpg_content_1")

        self.assertEqual(targets[1]["number"], 2)
        self.assertEqual(targets[1]["source"], "2.png")
        self.assertEqual(targets[1]["target"], "Aakash Ganguly.png")
        self.assertEqual(targets[1]["content"], b"fake_png_content_2")

        self.assertEqual(targets[2]["number"], 3)
        self.assertEqual(targets[2]["source"], "3.webp")
        self.assertEqual(targets[2]["target"], "Aarya Prakash.webp")
        self.assertEqual(targets[2]["content"], b"fake_webp_content_3")

    def test_leading_zeros_support(self):
        files = [
            ("01.jpg", b"content_1"),
            ("002.jpg", b"content_2"),
        ]
        names = "Alice Smith\nBob Jones"
        targets, errors, notices = prepare_renaming(files, names)
        self.assertEqual(errors, [])
        self.assertEqual(len(targets), 2)
        self.assertEqual(targets[0]["target"], "Alice Smith.jpg")
        self.assertEqual(targets[1]["target"], "Bob Jones.jpg")

    def test_nested_zip_folder_support(self):
        files = [
            ("Certificates Batch/1.png", b"content_1"),
            ("Certificates Batch/2.png", b"content_2"),
        ]
        names = "Aadya Thakur\nAakash Ganguly"
        targets, errors, notices = prepare_renaming(files, names)
        self.assertEqual(errors, [])
        self.assertEqual(len(targets), 2)
        self.assertEqual(targets[0]["target"], "Aadya Thakur.png")

    def test_missing_numbered_images(self):
        files = [
            ("1.jpg", b"content_1"),
            ("3.jpg", b"content_3"),
        ]
        names = "Aadya Thakur\nAakash Ganguly\nAarya Prakash"
        targets, errors, notices = prepare_renaming(files, names)
        self.assertEqual(targets, [])
        self.assertTrue(any("Missing numbered image(s): 2" in err for err in errors))

    def test_extra_numbered_images(self):
        files = [
            ("1.jpg", b"content_1"),
            ("2.jpg", b"content_2"),
            ("3.jpg", b"content_3"),
        ]
        names = "Aadya Thakur\nAakash Ganguly"
        targets, errors, notices = prepare_renaming(files, names)
        self.assertEqual(targets, [])
        self.assertTrue(any("Extra numbered image(s): 3" in err for err in errors))

    def test_duplicate_image_numbers(self):
        files = [
            ("1.jpg", b"content_1_a"),
            ("01.png", b"content_1_b"),
        ]
        names = "Aadya Thakur"
        targets, errors, notices = prepare_renaming(files, names)
        self.assertEqual(targets, [])
        self.assertTrue(any("More than one image matches number 1" in err for err in errors))

    def test_duplicate_recipient_names_conflict(self):
        files = [
            ("1.jpg", b"content_1"),
            ("2.jpg", b"content_2"),
        ]
        names = "Aadya Thakur\nAadya Thakur"
        targets, errors, notices = prepare_renaming(files, names)
        self.assertEqual(targets, [])
        self.assertTrue(any("Duplicate name would create the same filename" in err for err in errors))

    def test_empty_files_or_names(self):
        # Empty names
        targets, errors, notices = prepare_renaming([("1.jpg", b"c")], "")
        self.assertEqual(targets, [])
        self.assertTrue(any("Paste at least one name" in err for err in errors))

        # Empty files
        targets, errors, notices = prepare_renaming([], "Aadya Thakur")
        self.assertEqual(targets, [])
        self.assertTrue(any("No certificate files found" in err for err in errors))

    def test_non_numbered_files_ignored_with_notice(self):
        files = [
            ("1.jpg", b"content_1"),
            ("notes.png", b"content_notes"),
        ]
        names = "Aadya Thakur"
        targets, errors, notices = prepare_renaming(files, names)
        self.assertEqual(errors, [])
        self.assertEqual(len(targets), 1)
        self.assertTrue(any("Ignored file that is not numbered: notes.png" in n for n in notices))

    def test_macos_metadata_silently_skipped(self):
        files = [
            ("1.jpg", b"content_1"),
            ("__MACOSX/._1.jpg", b"mac_meta"),
            (".DS_Store", b"ds"),
        ]
        names = "Aadya Thakur"
        targets, errors, notices = prepare_renaming(files, names)
        self.assertEqual(errors, [])
        self.assertEqual(len(targets), 1)
        self.assertEqual(notices, [])

    def test_zip_in_and_zip_out_roundtrip(self):
        in_memory_zip = io.BytesIO()
        with zipfile.ZipFile(in_memory_zip, "w") as zf:
            zf.writestr("1.jpg", b"image1")
            zf.writestr("2.png", b"image2")

        in_memory_zip.seek(0)
        loaded_files = []
        with zipfile.ZipFile(in_memory_zip, "r") as zf:
            for item in zf.infolist():
                if not item.is_dir():
                    loaded_files.append((item.filename, zf.read(item)))

        names = "Aadya Thakur\nAakash Ganguly"
        targets, errors, notices = prepare_renaming(loaded_files, names)
        self.assertEqual(errors, [])

        out_memory_zip = io.BytesIO()
        with zipfile.ZipFile(out_memory_zip, "w") as zf:
            for item in targets:
                zf.writestr(item["target"], item["content"])

        out_memory_zip.seek(0)
        with zipfile.ZipFile(out_memory_zip, "r") as zf:
            names_in_zip = zf.namelist()
            self.assertIn("Aadya Thakur.jpg", names_in_zip)
            self.assertIn("Aakash Ganguly.png", names_in_zip)
            self.assertEqual(zf.read("Aadya Thakur.jpg"), b"image1")
            self.assertEqual(zf.read("Aakash Ganguly.png"), b"image2")


if __name__ == "__main__":
    unittest.main()
