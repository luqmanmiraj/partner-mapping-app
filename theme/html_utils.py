"""Render raw HTML blocks (use instead of st.markdown unsafe_allow_html)."""

from __future__ import annotations

import json
import re

import streamlit as st
import streamlit.components.v1 as components

def render_html(body: str, *, width: str = "stretch") -> None:
    """Render HTML without markdown code-block escaping."""
    st.html(body.strip(), width=width)  # type: ignore[arg-type]


def _normalize_css(css: str) -> str:
    text = css.strip()
    text = re.sub(r"^<style[^>]*>\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*</style>\s*$", "", text, flags=re.IGNORECASE)
    return text.strip()


def render_st_html_page(css: str, html: str, *, width: str = "stretch") -> None:
    """One st.html call: styles + markup in the same iframe (styles apply reliably)."""
    stylesheet = _normalize_css(css)
    body = html.strip()
    document = f"<style>{stylesheet}</style>\n{body}"
    st.html(document, width=width)  # type: ignore[arg-type]


def render_styled_html(styles: str, body: str, *, width: str = "stretch") -> None:
    """Alias for render_st_html_page (style + body in one st.html)."""
    render_st_html_page(styles, body, width=width)


def inject_parent_styles(css: str, *, style_id: str) -> None:
    """
    Inject CSS into the Streamlit parent document.

    ``st.html`` / ``render_html`` styles live in an iframe and do not affect
    native widgets (buttons, containers, selectboxes). Use this for page layout
    and widget styling.
    """
    sheet = _normalize_css(css)
    components.html(
        f"""
        <script>
        (function () {{
            const doc = window.parent.document;
            const id = {json.dumps(style_id)};
            let el = doc.getElementById(id);
            if (!el) {{
                el = doc.createElement("style");
                el.id = id;
                doc.head.appendChild(el);
            }}
            el.textContent = {json.dumps(sheet)};
        }})();
        </script>
        """,
        height=0,
    )


def run_parent_script(script: str) -> None:
    """Run JavaScript in ``window.parent.document`` (main Streamlit DOM)."""
    components.html(
        f"<script>(function () {{{script}}})();</script>",
        height=0,
    )


def render_inline_html_page(
    css: str,
    html: str,
    *,
    head_markup: str = "",
    style_id: str = "inline-page-styles",
) -> None:
    """
    Render HTML in the main Streamlit document (markup only; CSS injected separately).

    ``st.markdown`` strips ``<style>`` tags, which would display CSS as plain text.
    """
    if head_markup.strip():
        st.markdown(head_markup.strip(), unsafe_allow_html=True)
    inject_parent_styles(css, style_id=style_id)
    st.markdown(html.strip(), unsafe_allow_html=True)
