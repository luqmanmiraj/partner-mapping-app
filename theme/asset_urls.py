"""Resolve bundled images to embeddable URLs for use in HTML (data URIs)."""

from __future__ import annotations

import base64
import html
import mimetypes
from pathlib import Path


def file_data_uri(path: Path) -> str | None:
    """Return a data: URI for a local image file (works in st.html iframes and on Cloud)."""
    if not path.is_file():
        return None
    raw = path.read_bytes()
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    if mime == "image/svg+xml" or path.suffix.lower() == ".svg":
        mime = "image/svg+xml"
    encoded = base64.b64encode(raw).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def asset_image_url(path: Path, image_id: str = "") -> str:
    """Stable URL for a bundled asset (data URI; ``image_id`` kept for call-site compatibility)."""
    return file_data_uri(path) or ""


def asset_img_tag(
    path: Path,
    *,
    css_class: str = "",
    width: int | None = None,
    height: int | None = None,
    image_id: str = "",
) -> str:
    url = asset_image_url(path, image_id)
    if not url:
        return ""
    cls = f' class="{css_class}"' if css_class else ""
    w = f' width="{width}"' if width else ""
    h = f' height="{height}"' if height else ""
    return f'<img src="{html.escape(url)}" alt=""{cls}{w}{h} />'
