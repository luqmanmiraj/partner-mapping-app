"""Backward-compatible re-exports — use declaration_store."""

from data.declaration_store import (
    check_period_closed,
    load_deposit_detail,
    load_deposit_history,
)

__all__ = ["load_deposit_history", "load_deposit_detail", "check_period_closed"]
