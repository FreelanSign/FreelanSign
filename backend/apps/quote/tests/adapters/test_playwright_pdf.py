# apps/quote/tests/adapters/test_playwright_pdf.py
from apps.quote.adapters.pdf.playwright_generator import PlaywrightPdfGenerator

class _FakePage:
    def set_content(self, html, wait_until): pass
    def pdf(self, **kwargs): return b"%PDF-mocked%"

class _FakeBrowser:
    def new_page(self, base_url=None): return _FakePage()
    def close(self): pass

class _FakeChromium:
    def launch(self, headless): return _FakeBrowser()

class _FakeP:
    chromium = _FakeChromium()
    def __enter__(self): return self
    def __exit__(self, exc_type, exc, tb): pass

def test_playwright_adapter_generates_pdf(monkeypatch):
    from apps.quote.adapters.pdf import playwright_generator as mod
    def _fake_sync_playwright(): return _FakeP()
    monkeypatch.setattr(mod, "sync_playwright", _fake_sync_playwright)

    gen = PlaywrightPdfGenerator()
    out = gen.generate("<html>ok</html>")
    assert isinstance(out, (bytes, bytearray))
    assert out.startswith(b"%PDF")
