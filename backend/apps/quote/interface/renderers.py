# apps/quote/interface/renderers.py
from django.utils.encoding import force_bytes
from rest_framework.renderers import BaseRenderer


class PDFRenderer(BaseRenderer):
    media_type = "application/pdf"
    format = "pdf"
    charset = None  # très important: binaire
    render_style = "binary"  # indique à DRF que c'est du binaire

    def render(self, data, accepted_media_type=None, renderer_context=None):
        # Cas classiques
        if data is None:
            return b""
        if isinstance(data, (bytes, bytearray, memoryview)):
            return bytes(data)
        if isinstance(data, str):
            return data.encode("utf-8")

        # Fallback robuste (erreurs DRF, dicts, etc.)
        try:
            return force_bytes(data)
        except Exception:
            return force_bytes(str(data))
