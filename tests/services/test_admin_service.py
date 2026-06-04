"""Unit tests for services.admin_service."""

from __future__ import annotations

from services.admin_service import (
    activate_partner,
    calibrate_partner,
    deactivate_partner,
    update_system_config,
)
from services.brd_state import get_config, get_partner


def test_activate_and_deactivate_partner(brd_state) -> None:
    msg = activate_partner("NEWCO", "99999", "supplier", "USD")
    assert "NEWCO" in msg
    partner = get_partner("NEWCO")
    assert partner is not None
    assert partner.is_active is True
    assert partner.default_currency == "USD"

    deactivate_partner("NEWCO")
    assert get_partner("NEWCO").is_active is False


def test_calibrate_partner_stable_columns(
    brd_state,
    matching_calibration_files: tuple[tuple[str, bytes], tuple[str, bytes]],
) -> None:
    (n1, b1), (n2, b2) = matching_calibration_files
    msg = calibrate_partner("MEYLE", b1, n1, b2, n2)
    assert "stable" in msg.lower()
    assert get_partner("MEYLE").calibration_stable is True


def test_calibrate_partner_mismatched_columns(brd_state) -> None:
    msg = calibrate_partner(
        "MEYLE",
        b"a,b\n1,2\n",
        "a.csv",
        b"x,y,z\n1,2,3\n",
        "b.csv",
    )
    assert "differs" in msg.lower()
    assert get_partner("MEYLE").calibration_stable is False


def test_update_system_config(brd_state) -> None:
    update_system_config(0.85, 2.0, 15.0)
    cfg = get_config()
    assert cfg["confidence_threshold"] == 0.85
    assert cfg["discrepancy_alert_pct"] == 15.0
