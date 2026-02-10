# apps/quote/adapters/pdf/weasyprint_generator.py
import os
import platform
import sys


def _ensure_library_path():
    """On macOS, ensure Homebrew libs are discoverable by cffi/WeasyPrint."""
    if platform.system() != "Darwin":
        return
    homebrew_lib = "/opt/homebrew/lib" if platform.machine() == "arm64" else "/usr/local/lib"
    if not os.path.isdir(homebrew_lib):
        return
    fallback = os.environ.get("DYLD_FALLBACK_LIBRARY_PATH", "")
    if homebrew_lib not in fallback:
        os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = f"{homebrew_lib}:{fallback}" if fallback else homebrew_lib
        # cffi caches dlopen paths; reload if already imported
        if "cffi" in sys.modules:
            pass  # path set before weasyprint import is enough


class WeasyPrintPdfGenerator:
    """HTML -> PDF adapter using WeasyPrint (implements PdfGenerator Protocol)."""

    def generate(self, html: str, *, base_url: str | None = None) -> bytes:
        _ensure_library_path()
        import weasyprint  # lazy import: avoid loading C libs at Django startup

        doc = weasyprint.HTML(string=html, base_url=base_url)
        return doc.write_pdf()
