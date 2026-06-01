"""Render raw HTML blocks (use instead of st.markdown unsafe_allow_html)."""

from __future__ import annotations

import streamlit as st


def render_html(body: str, *, width: str = "stretch") -> None:
    """Render HTML without markdown code-block escaping."""
    st.html(body.strip(), width=width)  # type: ignore[arg-type]


def render_styled_html(styles: str, body: str, *, width: str = "stretch") -> None:
    """Inject CSS in the event container, then render markup in the main canvas."""
    if styles.strip():
        render_html(f"<style>{styles}</style>")
    render_html(body, width=width)
