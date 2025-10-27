# apps/quote/adapters/pdf/playwright_generator.py
from playwright.sync_api import sync_playwright


class PlaywrightPdfGenerator:
    def generate(self, html: str, *, base_url: str | None = None) -> bytes:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(base_url=base_url or None)

            page.set_content(html, wait_until="networkidle")

            # Optionnels selon l'implémentation/fake de page
            if hasattr(page, "emulate_media"):
                try:
                    page.emulate_media(media="print")
                except Exception:
                    pass

            if hasattr(page, "add_style_tag"):
                try:
                    page.add_style_tag(
                        content="""
                      * {
                        -webkit-print-color-adjust: exact !important;
                        print-color-adjust: exact !important;
                        color-adjust: exact !important;
                      }
                      @media print {
                        * {
                          -webkit-print-color-adjust: exact !important;
                          print-color-adjust: exact !important;
                        }
                      }
                    """
                    )
                except Exception:
                    pass

            pdf = page.pdf(
                format="A4",
                margin={"top": "10mm", "right": "10mm", "bottom": "10mm", "left": "10mm"},
                print_background=True,
                prefer_css_page_size=True,
            )
            browser.close()
            return pdf
