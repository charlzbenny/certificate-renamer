"""Certificate Renamer — Streamlit Web Application

A clean, modern, and reliable tool to rename Canva Bulk Create certificate exports
using recipient names in seconds.

Workflow:
1. Upload Canva certificates (ZIP archive or individual images)
2. Paste recipient names in exact sequential order
3. Preview & verify filename matches
4. Download renamed certificates as a new ZIP file (original files remain untouched)
"""

import io
from pathlib import PurePosixPath
import zipfile

import streamlit as st
from renamer import (
    SUPPORTED_EXTENSIONS,
    clean_filename,
    get_clean_names,
    prepare_renaming,
)

# -----------------------------------------------------------------------------
# 0. Page Configuration & Professional Light Theme Styles
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Certificate Renamer",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    /* Global Typography & Light-Theme Color Palette */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        color: #0F172A;
    }

    .main .block-container {
        max-width: 820px;
        padding-top: 2rem;
        padding-bottom: 4rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
    }

    /* Header styling */
    .hero-header {
        margin-bottom: 2rem;
        padding-bottom: 1.5rem;
        border-bottom: 1px solid #E2E8F0;
    }

    .hero-title {
        font-size: 1.85rem;
        font-weight: 700;
        color: #0F172A;
        letter-spacing: -0.02em;
        margin: 0 0 6px 0;
    }

    .hero-subtitle {
        font-size: 1.05rem;
        font-weight: 600;
        color: #1E3A8A;
        margin: 0 0 8px 0;
    }

    .hero-desc {
        font-size: 0.95rem;
        color: #475569;
        line-height: 1.55;
        margin: 0;
    }

    .hero-badges {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-top: 14px;
    }

    .badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.8rem;
        font-weight: 500;
        padding: 4px 10px;
        border-radius: 9999px;
        background-color: #F8FAFC;
        color: #334155;
        border: 1px solid #E2E8F0;
    }

    .badge-teal {
        background-color: #F0FDFA;
        color: #0F766E;
        border: 1px solid #CCFBF1;
    }

    /* Section Headings */
    .step-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: 1.5rem;
        margin-bottom: 6px;
    }

    .step-number {
        width: 26px;
        height: 26px;
        border-radius: 50%;
        background-color: #1E3A8A;
        color: #FFFFFF;
        font-size: 0.85rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .step-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0F172A;
        margin: 0;
    }

    .step-desc {
        font-size: 0.92rem;
        color: #475569;
        margin-bottom: 12px;
        line-height: 1.5;
    }

    /* Stat Pills & Feedback Banners */
    .pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.86rem;
        font-weight: 600;
        padding: 6px 12px;
        border-radius: 8px;
        margin-top: 6px;
        margin-bottom: 6px;
    }

    .pill-info { background-color: #EFF6FF; color: #1D4ED8; border: 1px solid #DBEAFE; }
    .pill-success { background-color: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; }
    .pill-warning { background-color: #FFFBEB; color: #B45309; border: 1px solid #FDE68A; }

    .callout {
        border-radius: 8px;
        padding: 12px 14px;
        font-size: 0.88rem;
        line-height: 1.5;
        margin-top: 10px;
        margin-bottom: 10px;
    }

    .callout-info { background-color: #F8FAFC; border: 1px solid #E2E8F0; color: #334155; }
    .callout-tip { background-color: #F0FDFA; border: 1px solid #CCFBF1; color: #115E59; }
    .callout-warning { background-color: #FFFBEB; border: 1px solid #FDE68A; color: #92400E; }

    /* Button Customization */
    div.stButton > button[kind="primary"] {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.6rem 1.4rem !important;
    }

    div.stButton > button[kind="primary"]:hover {
        background-color: #1D4ED8 !important;
    }

    div.stDownloadButton > button {
        background-color: #0D9488 !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.7rem 1.5rem !important;
    }

    div.stDownloadButton > button:hover {
        background-color: #0F766E !important;
    }

    /* Verification Table */
    .table-container {
        width: 100%;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        overflow: hidden;
        margin-top: 12px;
        margin-bottom: 16px;
    }

    .table-container table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.88rem;
    }

    .table-container th {
        background-color: #F8FAFC;
        color: #1E293B;
        font-weight: 600;
        text-align: left;
        padding: 10px 14px;
        border-bottom: 1px solid #E2E8F0;
    }

    .table-container td {
        padding: 9px 14px;
        border-bottom: 1px solid #F1F5F9;
        color: #334155;
    }

    .table-container tr:last-child td {
        border-bottom: none;
    }

    .footer-text {
        text-align: center;
        font-size: 0.82rem;
        color: #64748B;
        margin-top: 3.5rem;
        padding-top: 1.5rem;
        border-top: 1px solid #E2E8F0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero-header">
        <h1 class="hero-title">Certificate Renamer</h1>
        <div class="hero-subtitle">Give every Canva certificate its recipient's name — in seconds.</div>
        <p class="hero-desc">
            Upload your Canva export, paste the recipient names in the correct order,
            preview the matches, and download your renamed certificates.
        </p>
        <div class="hero-badges">
            <span class="badge badge-teal">✓ Canva Bulk Create Ready</span>
            <span class="badge">🔒 100% Local & In-Memory</span>
            <span class="badge">🛡 Originals Untouched</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Section 1: Upload Canva certificates
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="step-header">
        <span class="step-number">1</span>
        <h2 class="step-title">Upload your Canva export</h2>
    </div>
    <div class="step-desc">
        Download your certificates from Canva and upload the ZIP file here. You can also select multiple extracted certificate images.
    </div>
    """,
    unsafe_allow_html=True,
)

mode = st.radio(
    "Upload format selector",
    options=["Upload ZIP file", "Upload extracted images"],
    horizontal=True,
    label_visibility="collapsed",
)

uploaded_files: list[tuple[str, bytes]] = []

if mode == "Upload ZIP file":
    zip_upload = st.file_uploader(
        "Upload Canva export (.zip)",
        type=["zip"],
        accept_multiple_files=False,
        help="Upload the ZIP file downloaded directly from Canva Bulk Create.",
    )
    if zip_upload is not None:
        try:
            with zipfile.ZipFile(io.BytesIO(zip_upload.getvalue())) as archive:
                for item in archive.infolist():
                    if item.is_dir():
                        continue
                    path = PurePosixPath(item.filename)
                    # Ignore macOS metadata or hidden files
                    if (
                        path.name.startswith("._")
                        or path.name.startswith(".")
                        or "__MACOSX" in path.parts
                    ):
                        continue
                    if path.suffix.lower() in SUPPORTED_EXTENSIONS:
                        uploaded_files.append((item.filename, archive.read(item)))

            if uploaded_files:
                st.markdown(
                    f"""
                    <div class="pill pill-success">
                        ✓ Archive loaded: <strong>{zip_upload.name}</strong> ({len(uploaded_files)} certificate image{'s' if len(uploaded_files) != 1 else ''} detected)
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    """
                    <div class="pill pill-warning">
                        ⚠ No supported image files (.jpg, .jpeg, .png, .webp) detected in this ZIP archive.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        except zipfile.BadZipFile:
            st.error("The selected file is not a valid ZIP archive. Please select a valid Canva ZIP.")
else:
    images_upload = st.file_uploader(
        "Upload extracted certificate images",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True,
        help="Hold Ctrl or Shift to select multiple certificate images from your computer.",
    )
    if images_upload:
        for f in images_upload:
            uploaded_files.append((f.name, f.getvalue()))
        st.markdown(
            f"""
            <div class="pill pill-success">
                ✓ {len(uploaded_files)} certificate image{'s' if len(uploaded_files) != 1 else ''} selected.
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown(
    """
    <div class="callout callout-info">
        <strong>Supported formats:</strong> This version supports numbered <code>.jpg</code>, <code>.jpeg</code>, <code>.png</code>, and <code>.webp</code> certificates (e.g. <code>1.png</code>, <code>2.jpg</code>, <code>3.webp</code>).
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Section 2: Enter recipient names
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="step-header">
        <span class="step-number">2</span>
        <h2 class="step-title">Paste recipient names</h2>
    </div>
    <div class="step-desc">
        Paste one name per line, in the exact same order as the numbered certificates in your Canva export.
    </div>
    """,
    unsafe_allow_html=True,
)

names_text = st.text_area(
    "Recipient names (one per line)",
    height=190,
    placeholder="Aadya Thakur\nAakash Ganguly\nAarya Prakash\nAbdullah Farooq Khan",
    help="Names must match the numbering of your certificates: Line 1 -> 1.png, Line 2 -> 2.png, etc.",
    label_visibility="collapsed",
)

# Compute live name statistics
clean_names = get_clean_names(names_text)
name_count = len(clean_names)
file_count = len(uploaded_files)

# Dynamic match counter feedback
if name_count > 0 or file_count > 0:
    if file_count > 0 and name_count == file_count:
        st.markdown(
            f"""
            <div class="pill pill-success">
                ✓ {name_count} recipient name{'s' if name_count != 1 else ''} entered • Exact match with {file_count} uploaded certificate{'s' if file_count != 1 else ''}
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif file_count > 0 and name_count != file_count:
        st.markdown(
            f"""
            <div class="pill pill-warning">
                ℹ {name_count} recipient name{'s' if name_count != 1 else ''} entered vs {file_count} uploaded certificate{'s' if file_count != 1 else ''}
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="pill pill-info">
                {name_count} recipient name{'s' if name_count != 1 else ''} entered
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown(
    """
    <div class="callout callout-tip">
        <strong>Important:</strong> Matching is strictly positional. The first name matches certificate <strong>1</strong>, the second name matches certificate <strong>2</strong>, and so on. Please confirm your order before renaming.
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Section 3: Preview and verify
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="step-header">
        <span class="step-number">3</span>
        <h2 class="step-title">Review before renaming</h2>
    </div>
    <div class="step-desc">
        Review the planned filename changes and verify accuracy before downloading.
    </div>
    """,
    unsafe_allow_html=True,
)

# Input signature to prevent downloading stale results if inputs are edited
input_signature = (
    len(uploaded_files),
    tuple(sorted(f[0] for f in uploaded_files)),
    names_text.strip(),
)

col_preview, _ = st.columns([1, 1])
with col_preview:
    preview_button = st.button("Preview filenames", type="primary", use_container_width=True)

if preview_button:
    if not uploaded_files:
        st.session_state["preview_cache"] = {
            "sig": input_signature,
            "errors": ["No certificate files have been uploaded. Please upload a ZIP or select certificate images."],
            "mapping": [],
            "notices": [],
        }
    elif not names_text.strip():
        st.session_state["preview_cache"] = {
            "sig": input_signature,
            "errors": ["No recipient names have been entered. Please paste your recipient list above."],
            "mapping": [],
            "notices": [],
        }
    else:
        mapping, errors, notices = prepare_renaming(uploaded_files, names_text)
        st.session_state["preview_cache"] = {
            "sig": input_signature,
            "errors": errors,
            "mapping": mapping,
            "notices": notices,
        }

preview_cache = st.session_state.get("preview_cache")

if preview_cache:
    is_stale = preview_cache.get("sig") != input_signature

    if is_stale:
        st.markdown(
            """
            <div class="callout callout-warning">
                <strong>Inputs changed:</strong> You modified your uploaded files or recipient list. Click <strong>Preview filenames</strong> again to update the preview table and download button.
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Display non-critical notices (e.g. non-numbered files ignored)
    for notice in preview_cache.get("notices", []):
        st.info(f"ℹ {notice}")

    errors = preview_cache.get("errors", [])
    mapping = preview_cache.get("mapping", [])

    if errors:
        st.markdown(
            """
            <div style="background-color: #FEF2F2; border: 1px solid #FCA5A5; border-radius: 8px; padding: 14px 18px; margin-top: 12px; margin-bottom: 12px;">
                <div style="font-weight: 700; color: #991B1B; margin-bottom: 6px;">
                    Please address these issues before renaming:
                </div>
                <ul style="margin: 0; padding-left: 20px; color: #B91C1C; font-size: 0.9rem; line-height: 1.6;">
            """
            + "".join(f"<li>{err}</li>" for err in errors)
            + """
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    elif mapping and not is_stale:
        st.markdown(
            f"""
            <div style="background-color: #F0FDF4; border: 1px solid #86EFAC; border-radius: 8px; padding: 12px 16px; margin-top: 12px; margin-bottom: 12px; color: #166534; font-weight: 600; font-size: 0.92rem;">
                ✓ Verification successful! All {len(mapping)} certificate files match recipient names perfectly.
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Build readable verification table
        rows_html = "".join(
            f"""
            <tr>
                <td style="font-weight: 600; color: #1E3A8A; width: 20%;">{item['number']}</td>
                <td style="font-family: monospace; color: #475569; width: 40%;">{item['source']}</td>
                <td style="font-weight: 500; color: #0F172A; width: 40%;">
                    <span style="background-color: #F1F5F9; padding: 2px 8px; border-radius: 4px; font-family: monospace; border: 1px solid #E2E8F0;">
                        {item['target']}
                    </span>
                </td>
            </tr>
            """
            for item in mapping
        )

        st.markdown(
            f"""
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Certificate #</th>
                            <th>Original filename</th>
                            <th>New filename</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ---------------------------------------------------------------------
        # Section 4: Download renamed certificates
        # ---------------------------------------------------------------------
        st.markdown(
            """
            <div class="step-header">
                <span class="step-number">4</span>
                <h2 class="step-title">Download renamed certificates</h2>
            </div>
            <div class="step-desc">
                Your renamed certificates will be packed into a new ZIP file. Your original files remain unchanged.
            </div>
            """,
            unsafe_allow_html=True,
        )

        output_zip = io.BytesIO()
        with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for item in mapping:
                archive.writestr(item["target"], item["content"])

        zip_bytes = output_zip.getvalue()

        col_download, _ = st.columns([1, 1])
        with col_download:
            st.download_button(
                label=f"Download renamed certificates (.zip) — {len(mapping)} files",
                data=zip_bytes,
                file_name="renamed_certificates.zip",
                mime="application/zip",
                type="primary",
                use_container_width=True,
            )

        st.markdown(
            f"""
            <div style="font-size: 0.84rem; color: #64748B; margin-top: 6px;">
                ✓ {len(mapping)} certificates packaged • Archive size: {len(zip_bytes) / 1024:.1f} KB
            </div>
            """,
            unsafe_allow_html=True,
        )

# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="footer-text">
        <strong>Certificate Renamer</strong> • MCA Software Project • Canva Bulk Create Workflow Helper
    </div>
    """,
    unsafe_allow_html=True,
)
