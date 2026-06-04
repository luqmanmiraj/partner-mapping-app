"""Integration tests — page modules expose render entrypoints and run with mocks."""

from __future__ import annotations

import importlib
import inspect
from typing import Callable

import pytest

# (module_path, callable_name) — mirrors streamlit_app.py registry + stubs.
PAGE_RENDERERS: list[tuple[str, str]] = [
    ("pages.portal.hub_dashboard", "render"),
    ("pages.portal.logs", "render"),
    ("pages.portal.member_directory", "render"),
    ("pages.portal.my_company", "render"),
    ("pages.portal.about", "render"),
    ("pages.portal.services", "render"),
    ("pages.portal.news", "render"),
    ("pages.portal.help", "render"),
    ("pages.portal.offers", "render"),
    ("pages.portal.supplier_portfolio", "render"),
    ("pages.partner.upload", "render"),
    ("pages.partner.history", "render"),
    ("pages.partner.dashboard", "render"),
    ("pages.partner.workflow_logs", "render"),
    ("pages.partner.corrective", "render"),
    ("pages.partner.deposit_detail", "render"),
    ("pages.internal.review_queue", "render"),
    ("pages.internal.review_detail", "render"),
    ("pages.internal.bulk_review", "render"),
    ("pages.internal.overlap", "render"),
    ("pages.internal.discrepancy", "render"),
    ("pages.admin.stubs", "render_calibration"),
    ("pages.admin.stubs", "render_onboarding"),
    ("pages.admin.stubs", "render_decommission"),
    ("pages.admin.stubs", "render_closure"),
    ("pages.admin.stubs", "render_system_config"),
    ("pages.admin.stubs", "render_post_closure_audit"),
    ("pages.auth.connection", "render"),
]


class _StreamlitContainer:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class _StreamlitSidebar:
    def __enter__(self):
        return _StreamlitContainer()

    def __exit__(self, *args):
        return False


@pytest.fixture
def mock_streamlit_ui(monkeypatch: pytest.MonkeyPatch, streamlit_session) -> None:
    """Stub common Streamlit UI calls so page render functions do not require a browser."""
    import streamlit as st

    monkeypatch.setattr(st, "set_page_config", lambda *a, **k: None)
    monkeypatch.setattr(st, "title", lambda *a, **k: None)
    monkeypatch.setattr(st, "header", lambda *a, **k: None)
    monkeypatch.setattr(st, "subheader", lambda *a, **k: None)
    monkeypatch.setattr(st, "markdown", lambda *a, **k: None)
    monkeypatch.setattr(st, "caption", lambda *a, **k: None)
    monkeypatch.setattr(st, "write", lambda *a, **k: None)
    monkeypatch.setattr(st, "error", lambda *a, **k: None)
    monkeypatch.setattr(st, "warning", lambda *a, **k: None)
    monkeypatch.setattr(st, "info", lambda *a, **k: None)
    monkeypatch.setattr(st, "success", lambda *a, **k: None)
    monkeypatch.setattr(st, "divider", lambda *a, **k: None)
    monkeypatch.setattr(st, "button", lambda *a, **k: False)
    monkeypatch.setattr(st, "text_input", lambda *a, **k: "")
    def _selectbox(*args, **kwargs):
        options = kwargs.get("options") or (args[1] if len(args) > 1 else ["All"])
        index = kwargs.get("index", 0)
        if isinstance(options, list) and options:
            return options[min(index, len(options) - 1)]
        return "All"

    monkeypatch.setattr(st, "selectbox", _selectbox)
    monkeypatch.setattr(st, "file_uploader", lambda *a, **k: None)
    monkeypatch.setattr(
        st,
        "columns",
        lambda spec, **kwargs: [
            _StreamlitContainer()
            for _ in range(spec if isinstance(spec, int) else len(spec))
        ],
    )
    monkeypatch.setattr(st, "tabs", lambda labels: [None] * len(labels))
    monkeypatch.setattr(st, "metric", lambda *a, **k: None)
    monkeypatch.setattr(st, "dataframe", lambda *a, **k: None)
    monkeypatch.setattr(st, "plotly_chart", lambda *a, **k: None)
    monkeypatch.setattr(st, "html", lambda *a, **k: None)
    monkeypatch.setattr(st, "container", lambda *a, **k: _StreamlitContainer())
    monkeypatch.setattr(st, "sidebar", _StreamlitSidebar())
    monkeypatch.setattr(st, "expander", lambda *a, **k: _StreamlitContainer())
    monkeypatch.setattr(st, "form", lambda *a, **k: _StreamlitContainer())
    monkeypatch.setattr(st, "form_submit_button", lambda *a, **k: False)
    monkeypatch.setattr(st, "checkbox", lambda *a, **k: False)
    monkeypatch.setattr(st, "toggle", lambda *a, **k: False)
    monkeypatch.setattr(st, "text_area", lambda *a, **k: "")
    monkeypatch.setattr(st, "number_input", lambda *a, **k: 0)
    monkeypatch.setattr(st, "multiselect", lambda *a, **k: [])
    monkeypatch.setattr(st, "radio", lambda *a, **k: (k.get("options") or [""])[0])
    monkeypatch.setattr(st, "download_button", lambda *a, **k: False)
    monkeypatch.setattr(st, "delta_generator", st, raising=False)
    monkeypatch.setattr(st, "rerun", lambda: None)
    monkeypatch.setattr(st, "stop", lambda: None)

    monkeypatch.setattr(
        "auth.session.get_session",
        lambda: __import__("auth.session", fromlist=["UserSession"]).UserSession(
            role_type="partner",
            partner_key="MEYLE",
            declarant_type="supplier",
            display_name="Meyle",
            hubspot_company_id="11111111",
        ),
    )
    monkeypatch.setattr(
        "auth.session.is_partner",
        lambda: True,
    )
    monkeypatch.setattr(
        "auth.session.is_reviewer",
        lambda: False,
    )
    monkeypatch.setattr(
        "auth.session.is_admin",
        lambda: False,
    )


@pytest.mark.parametrize("module_path,attr", PAGE_RENDERERS)
def test_page_renderer_importable(module_path: str, attr: str) -> None:
    mod = importlib.import_module(module_path)
    fn = getattr(mod, attr)
    assert callable(fn)


@pytest.mark.parametrize("module_path,attr", PAGE_RENDERERS)
def test_page_renderer_invokes_without_error(
    module_path: str,
    attr: str,
    mock_streamlit_ui,
    brd_state,
) -> None:
    mod = importlib.import_module(module_path)
    fn: Callable[..., None] = getattr(mod, attr)
    kwargs = {}
    if "active_page" in inspect.signature(fn).parameters:
        kwargs["active_page"] = "test_page"
    fn(**kwargs)
