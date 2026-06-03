"""Partner pages wired to BRD declaration store."""

from __future__ import annotations

# Re-export for partner pages
from data.declaration_store import check_period_closed, load_deposit_detail, load_deposit_history

__all__ = ["load_deposit_history", "load_deposit_detail", "check_period_closed"]
