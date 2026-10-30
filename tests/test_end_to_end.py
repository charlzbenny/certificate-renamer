"""End-to-end automated verification script for Certificate Renamer.

Encoding-safe for all Windows consoles (ASCII output tags).
"""
import io
import os
from pathlib import Path
import shutil
import sys
import zipfile

# Safe console output for Windows cmd/powershell
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from renamer import prepare_renaming, clean_filename, get_clean_names, SUPPORTED_EXTENSIONS


def run_e2e_tests():
    print("=== Running End-to-End Functional Tests ===")

    # 1. Test ZIP Upload scenario
    sample_dir = os.path.join(str(PROJECT_ROOT), "tests", "test_scratch_data")
    if os.path.exists(sample_dir):
        shutil.rmtree(sample_dir)
    os.makedirs(sample_dir, exist_ok=True)

    try:
        # Create dummy original files
        file_1_path = os.path.join(sample_dir, "1.jpg")
        file_2_path = os.path.join(sample_dir, "2.png")
        file_3_path = os.path.join(sample_dir, "3.webp")

        with open(file_1_path, "wb") as f:
            f.write(b"SAMPLE_IMAGE_CONTENT_1_JPG")
        with open(file_2_path, "wb") as f:
            f.write(b"SAMPLE_IMAGE_CONTENT_2_PNG")
        with open(file_3_path, "wb") as f:
            f.write(b"SAMPLE_IMAGE_CONTENT_3_WEBP")

        orig_1_content = open(file_1_path, "rb").read()
        orig_2_content = open(file_2_path, "rb").read()
        orig_3_content = open(file_3_path, "rb").read()

        # Pack into a Canva-like ZIP
        zip_path = os.path.join(sample_dir, "canva_export.zip")
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.write(file_1_path, "Canva Batch/1.jpg")
            zf.write(file_2_path, "Canva Batch/2.png")
            zf.write(file_3_path, "Canva Batch/3.webp")
            zf.writestr("Canva Batch/__MACOSX/._1.jpg", b"meta")

        # Read the ZIP just like app.py does
        uploaded_files = []
        with zipfile.ZipFile(zip_path) as archive:
            for item in archive.infolist():
                if item.is_dir():
                    continue
                uploaded_files.append((item.filename, archive.read(item)))

        # Scenario A: Perfect match & extension preservation
        pasted_names = """
        Aadya Thakur
        Aakash Ganguly
        Aarya Prakash
        """
        targets, errors, notices = prepare_renaming(uploaded_files, pasted_names)
        assert not errors, f"Expected no errors, got {errors}"
        assert len(targets) == 3, f"Expected 3 targets, got {len(targets)}"
        assert targets[0]["target"] == "Aadya Thakur.jpg"
        assert targets[1]["target"] == "Aakash Ganguly.png"
        assert targets[2]["target"] == "Aarya Prakash.webp"
        print("[PASS] Scenario A (Perfect ZIP match & extension preservation)")

        # Scenario B: Output ZIP generation & content verification
        output_zip = io.BytesIO()
        with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for item in targets:
                archive.writestr(item["target"], item["content"])

        output_zip.seek(0)
        with zipfile.ZipFile(output_zip, "r") as archive:
            entries = archive.namelist()
            assert "Aadya Thakur.jpg" in entries
            assert "Aakash Ganguly.png" in entries
            assert "Aarya Prakash.webp" in entries
            assert archive.read("Aadya Thakur.jpg") == b"SAMPLE_IMAGE_CONTENT_1_JPG"
        print("[PASS] Scenario B (Output ZIP generation & content verification)")

        # Scenario C: Original files on disk strictly untouched
        assert open(file_1_path, "rb").read() == orig_1_content
        assert open(file_2_path, "rb").read() == orig_2_content
        assert open(file_3_path, "rb").read() == orig_3_content
        assert os.path.exists(file_1_path)
        assert os.path.exists(file_2_path)
        assert os.path.exists(file_3_path)
        print("[PASS] Scenario C (Original source files strictly untouched)")

        # Scenario D: Missing numbers detection
        pasted_names_4 = """
        Aadya Thakur
        Aakash Ganguly
        Aarya Prakash
        Abdullah Farooq Khan
        """
        targets_d, errors_d, _ = prepare_renaming(uploaded_files, pasted_names_4)
        assert len(errors_d) > 0
        assert any("Missing numbered image(s): 4" in err for err in errors_d)
        print("[PASS] Scenario D (Missing number error caught)")

        # Scenario E: Duplicate recipient names producing conflicting filenames
        files_same_ext = [("1.jpg", b"content_1"), ("2.jpg", b"content_2")]
        pasted_names_dup = """
        Aadya Thakur
        Aadya Thakur
        """
        targets_e, errors_e, _ = prepare_renaming(files_same_ext, pasted_names_dup)
        assert len(errors_e) > 0, "Expected error on duplicate recipient name collision"
        assert any("Duplicate name would create the same filename" in err for err in errors_e)
        print("[PASS] Scenario E (Duplicate name conflict error caught)")

    finally:
        # Clean up scratch test data
        if os.path.exists(sample_dir):
            shutil.rmtree(sample_dir)
        print("[PASS] Scratch test data cleaned up.")

    print("=== All End-to-End Tests Passed Successfully! ===")


if __name__ == "__main__":
    run_e2e_tests()
