"""Resolve bundled images to Streamlit media URLs for use in HTML."""

from __future__ import annotations

import html
from pathlib import Path

from streamlit.elements.lib.image_utils import image_to_url
from streamlit.elements.lib.layout_utils import LayoutConfig


def asset_image_url(path: Path, image_id: str) -> str:
    if not path.is_file():
        return ""
    return image_to_url(
        str(path),
        layout_config=LayoutConfig(width="content"),
        clamp=False,
        channels="RGB",
        output_format="auto",
        image_id=image_id,
    )


def asset_img_tag(
    path: Path,
    *,
    css_class: str = "",
    width: int | None = None,
    height: int | None = None,
    image_id: str,
) -> str:
    url = asset_image_url(path, image_id)
    if not url:
        return ""
    cls = f' class="{css_class}"' if css_class else ""
    w = f' width="{width}"' if width else ""
    h = f' height="{height}"' if height else ""
    return f'<img src="{html.escape(url)}" alt=""{cls}{w}{h} />'
