"""Paths to bundled static assets."""

from __future__ import annotations

from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = APP_ROOT / "assets" / "images"
ICONS_DIR = IMAGES_DIR / "icons"
NAV_ICONS_DIR = ICONS_DIR / "nav"


def image_path(name: str) -> Path:
    return IMAGES_DIR / name


def icon_path(name: str) -> Path:
    return ICONS_DIR / name


def nav_icon_path(name: str) -> Path:
    return NAV_ICONS_DIR / name
