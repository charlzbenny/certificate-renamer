"""Core logic for Certificate Renamer.

This module does not modify the user's original files. It matches numbered
image files to names and returns renamed file contents for a new ZIP archive.
"""
from pathlib import PurePosixPath
import re
from typing import Iterable

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def clean_filename(name: str) -> str:
    """Remove characters that are invalid in common Windows filenames."""
    name = re.sub(r'[<>:"/\\|?*]', "", name)
    name = re.sub(r"\s+", " ", name).strip().rstrip(".")
    return name


def get_clean_names(pasted_names: str) -> list[str]:
    """Parse pasted text and return non-empty sanitized names, one per line."""
    if not pasted_names:
        return []
    names = []
    for line in pasted_names.splitlines():
        cleaned = clean_filename(line)
        if cleaned:
            names.append(cleaned)
    return names


def prepare_renaming(files: Iterable[tuple[str, bytes]], pasted_names: str):
    """Validate numbered image files and return (mapping, errors, notices).

    Each file is (filename, bytes). Filenames may include ZIP subfolders.
    Numbering is taken from the final filename stem, e.g. folder/001.png -> 1.
    """
    names = get_clean_names(pasted_names)
    if not names:
        return [], ["Paste at least one name, one name per line."], []

    file_list = list(files)
    if not file_list:
        return [], ["No certificate files found. Please upload a ZIP archive or select certificate image files."], []

    numbered = {}
    errors = []
    notices = []

    for filename, content in file_list:
        path = PurePosixPath(filename.replace("\\", "/"))
        # Ignore macOS compression metadata files or hidden files
        if path.name.startswith("._") or path.name.startswith(".") or "__MACOSX" in path.parts:
            continue
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        match = re.fullmatch(r"0*(\d+)", path.stem)
        if not match:
            notices.append(f"Ignored file that is not numbered: {filename}")
            continue
        number = int(match.group(1))
        if number in numbered:
            errors.append(
                f"More than one image matches number {number}: "
                f"'{numbered[number][0]}' and '{filename}'."
            )
        else:
            numbered[number] = (filename, content, path.suffix.lower())

    if errors:
        return [], errors, notices

    expected = set(range(1, len(names) + 1))
    actual = set(numbered)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)

    if missing:
        errors.append("Missing numbered image(s): " + ", ".join(map(str, missing)))
    if extra:
        errors.append("Extra numbered image(s): " + ", ".join(map(str, extra)))
    if errors:
        errors.append(
            f"Names pasted: {len(names)}. Numbered images found: {len(numbered)}. "
            "No files have been changed."
        )
        return [], errors, notices

    targets = []
    seen = set()
    for number, name in enumerate(names, start=1):
        if not name:
            errors.append(f"Name on line {number} becomes empty after cleaning.")
            continue
        filename, content, extension = numbered[number]
        target = f"{name}{extension}"
        key = target.casefold()
        if key in seen:
            errors.append(f"Duplicate name would create the same filename: {target}")
        seen.add(key)
        targets.append({
            "number": number,
            "source": filename,
            "target": target,
            "content": content,
        })

    if errors:
        return [], errors, notices
    return targets, [], notices
