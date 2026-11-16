"""Local PDF generation without permitting external resource fetches."""

import os
from pathlib import Path


def render_pdf(html: bytes) -> bytes:
    if os.name == "nt" and "WEASYPRINT_DLL_DIRECTORIES" not in os.environ:
        local = Path.cwd() / ".tools/windows-pdf/mingw64/bin"
        if local.is_dir():
            os.environ["WEASYPRINT_DLL_DIRECTORIES"] = str(local.resolve())
    try:
        from weasyprint import HTML  # type: ignore[import-untyped]
        from weasyprint.urls import (  # type: ignore[import-untyped]
            FatalURLFetchingError,
            URLFetcher,
        )
    except OSError as exc:
        raise ValueError(
            "PDF native libraries are missing. See docs/OUTPUTS.md for setup."
        ) from exc
    fetcher = URLFetcher(allowed_protocols=(), fail_on_errors=True)
    document = HTML(string=html.decode("utf-8"), url_fetcher=fetcher)
    try:
        result = document.write_pdf()
    except FatalURLFetchingError as exc:
        raise ValueError(
            "PDF contains blocked resource references; no output published."
        ) from exc
    if not isinstance(result, bytes):
        raise ValueError("PDF renderer returned no document.")
    return result
