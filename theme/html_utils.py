"""Render raw HTML blocks (use instead of st.markdown unsafe_allow_html)."""

from __future__ import annotations

import streamlit as st


def render_html(body: str) -> None:
    """Render HTML without markdown code-block escaping."""
    st.html(body.strip())
