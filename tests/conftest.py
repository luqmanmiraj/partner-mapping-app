"""Shared pytest fixtures (Streamlit session state, sample uploads)."""

from __future__ import annotations

from typing import Any

import pytest


class MockSessionState(dict):
    """Minimal stand-in for ``streamlit.runtime.state.session_state.SessionState``."""

    def __getattr__(self, key: str) -> Any:
        try:
            return self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc

    def __setattr__(self, key: str, value: Any) -> None:
        self[key] = value

    def __delattr__(self, key: str) -> None:
        try:
            del self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc


@pytest.fixture
def streamlit_session(monkeypatch: pytest.MonkeyPatch) -> MockSessionState:
    """Replace ``st.session_state`` for services and pages that use Streamlit storage."""
    import streamlit as st

    state = MockSessionState()
    monkeypatch.setattr(st, "session_state", state, raising=False)
    return state


@pytest.fixture
def brd_state(streamlit_session: MockSessionState) -> MockSessionState:
    """Initialize BRD demo state in the mock session."""
    from services.brd_state import init_brd_state

    init_brd_state()
    return streamlit_session


@pytest.fixture
def memory_state(streamlit_session: MockSessionState) -> MockSessionState:
    """Empty memory-store fallback buckets."""
    streamlit_session.memory_review_entries = {}
    streamlit_session.memory_global_templates = {}
    streamlit_session.memory_local_templates = {}
    return streamlit_session


@pytest.fixture
def sample_csv_bytes() -> bytes:
    return b"amount,partner,period\n1250.50,MEYLE,Q1-2026\n980.00,MEYLE,Q1-2026\n"


@pytest.fixture
def matching_calibration_files() -> tuple[tuple[str, bytes], tuple[str, bytes]]:
    a = b"sku,amount\n1,10\n"
    b = b"sku,amount\n2,20\n"
    return (("type_a.csv", a), ("type_b.csv", b))


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Tag tests by directory: unit, integration, isolation."""
    for item in items:
        path = str(item.path).replace("\\", "/")
        if "/integration/" in path:
            item.add_marker(pytest.mark.integration)
        elif "/isolation/" in path:
            item.add_marker(pytest.mark.isolation)
        else:
            item.add_marker(pytest.mark.unit)
