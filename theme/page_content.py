"""Main page body wrapper — horizontal gutter for all sections below the top header."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

from theme.html_utils import inject_parent_styles

_PREFIX = "nexus-page-content"
_CONTAINER_KEY = "page_content"
_GUTTER = "2rem"

# Streamlit 1.50+ main canvas selectors (section.main is not used in the DOM).
_MAIN = '[data-testid="stMain"]'
_BLOCK = '[data-testid="stMainBlockContainer"].block-container'
_PAGE_CONTENT = f'{_MAIN} .st-key-{_CONTAINER_KEY}'


def page_content_styles() -> str:
    p = _PREFIX
    gutter = _GUTTER
    return f"""
        :root {{
            --nexus-content-gutter: {gutter};
        }}

        {_BLOCK},
        .block-container {{
            padding-left: 0 !important;
            padding-right: 0 !important;
        }}

        /* Padded canvas below the full-bleed top header */
        {_PAGE_CONTENT},
        {_MAIN} .stVerticalBlock.st-key-{_CONTAINER_KEY},
        {_MAIN} .{p} {{
            width: 100% !important;
            max-width: 100% !important;
            padding-left: {gutter} !important;
            padding-right: {gutter} !important;
            box-sizing: border-box !important;
        }}

        {_PAGE_CONTENT},
        {_MAIN} .stVerticalBlock.st-key-{_CONTAINER_KEY} {{
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
        }}

        {_PAGE_CONTENT} > div {{
            width: 100% !important;
            max-width: 100% !important;
            box-sizing: border-box !important;
        }}
    """


def inject_page_content_styles() -> None:
    inject_parent_styles(page_content_styles(), style_id="nexus-page-content")


def _assign_page_content_class() -> None:
    """Attach the semantic wrapper class to the Streamlit page-content container."""
    components.html(
        f"""
        <script>
        (function () {{
            const doc = window.parent.document;
            const selector = '{_PAGE_CONTENT}';
            function apply() {{
                const el = doc.querySelector(selector);
                if (el && !el.classList.contains('{_PREFIX}')) {{
                    el.classList.add('{_PREFIX}');
                }}
            }}
            apply();
            window.setTimeout(apply, 0);
        }})();
        </script>
        """,
        height=0,
    )


def render_page_content(render_fn: Callable[..., None], *args: Any, **kwargs: Any) -> None:
    """Render authenticated page body inside the padded ``nexus-page-content`` wrapper."""
    with st.container(key=_CONTAINER_KEY):
        render_fn(*args, **kwargs)

    _assign_page_content_class()
