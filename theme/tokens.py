"""NEXUS design tokens — single source of truth for colors and typography."""

ORANGE = "#F58220"
ORANGE_LIGHT = "#FFF4EB"
SIDEBAR_BG = "#1C1C1E"
PAGE_BG = "#F4F4F5"
CARD_BG = "#FFFFFF"
TEXT_PRIMARY = "#1A1A1A"
TEXT_MUTED = "#6B7280"
GREEN = "#059669"
GREEN_BG = "#ECFDF5"
RED = "#DC2626"
RED_BG = "#FEF2F2"
BORDER = "#E5E7EB"
BLUE = "#2563EB"
BLUE_BG = "#EFF6FF"
AMBER = "#D97706"
AMBER_BG = "#FFFBEB"

STATUS_COLORS = {
    "Pending processing": ("#6B7280", "#F3F4F6"),
    "In review": (AMBER, AMBER_BG),
    "Validated": (GREEN, GREEN_BG),
    "Partially rejected": (AMBER, AMBER_BG),
    "Rejected": (RED, RED_BG),
    "Superseded": (TEXT_MUTED, PAGE_BG),
}

DEPOSIT_STATUSES = [
    "Pending processing",
    "In review",
    "Validated",
    "Partially rejected",
    "Rejected",
    "Superseded",
]

CURRENCIES = ["EUR", "USD", "GBP", "CHF", "PLN", "SEK", "NOK", "DKK", "CZK"]
