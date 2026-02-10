# apps/quote/tests/adapters/test_weasyprint_pdf.py
from apps.quote.adapters.pdf.weasyprint_generator import WeasyPrintPdfGenerator


def test_weasyprint_adapter_generates_pdf():
    gen = WeasyPrintPdfGenerator()
    out = gen.generate("<html><body><h1>Test</h1></body></html>")
    assert isinstance(out, (bytes, bytearray))
    assert out.startswith(b"%PDF")


def test_weasyprint_adapter_accepts_base_url():
    gen = WeasyPrintPdfGenerator()
    out = gen.generate(
        "<html><body><p>With base URL</p></body></html>",
        base_url="http://localhost:8000",
    )
    assert isinstance(out, (bytes, bytearray))
    assert out.startswith(b"%PDF")
