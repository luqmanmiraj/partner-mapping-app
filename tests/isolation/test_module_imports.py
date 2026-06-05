"""Isolation tests — application modules import without the full Streamlit runtime."""

from __future__ import annotations

import importlib
import sys

import pytest

# Representative modules per package (not every file — keeps CI fast).
SERVICE_MODULES = [
    "services.file_parser",
    "services.memory_store",
    "services.brd_state",
    "services.review_service",
    "services.admin_service",
    "services.closure_service",
    "services.processing_pipeline",
    "services.upload_client",
]

WIDGET_MODULES = [
    "widgets.hero_banner",
    "widgets.user_dropdown",
    "widgets.identify_partners_filter",
    "widgets.upcoming_features",
    "widgets.company_tabs",
    "widgets.overview_section",
]

PAGE_MODULES = [
    # pages.auth.connection is covered by tests/pages/test_connection.py;
    # reloading it here breaks monkeypatches on that module in the same pytest run.
    "pages.portal.hub_dashboard",
    "pages.portal.member_directory",
    "pages.partner.upload",
    "pages.internal.review_queue",
    "pages.admin.stubs",
]


@pytest.mark.parametrize("module_name", SERVICE_MODULES + WIDGET_MODULES + PAGE_MODULES)
def test_module_imports_cleanly(module_name: str) -> None:
    sys.modules.pop(module_name, None)
    mod = importlib.import_module(module_name)
    assert mod is not None


def test_services_do_not_import_pages() -> None:
    """Service layer should not depend on page modules."""
    import services.file_parser as fp
    import services.review_service as rs

    for path in (fp.__file__, rs.__file__):
        text = open(path, encoding="utf-8").read()
        assert "from pages." not in text
        assert "import pages." not in text
