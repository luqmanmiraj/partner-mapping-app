"""Hero welcome banner widget."""

from __future__ import annotations

import html

import streamlit as st

from content_policies.hub_dashboard import HubDashboardPolicy
from theme.html_utils import render_html


def render_hero_banner(policy: HubDashboardPolicy) -> None:
    bullets_html = "".join(f"<li>{html.escape(b)}</li>" for b in policy.hero_bullets)
    render_html(
        f"""
        <div class="hero-card">
            <div>
                <h2>{html.escape(policy.hero_headline)}</h2>
                <ul class="hero-list">{bullets_html}</ul>
            </div>
            <div class="hero-devices">
                <div class="device-phone"><div class="device-screen"></div></div>
                <div class="device-laptop"><div class="device-screen"></div></div>
            </div>
        </div>
        """
    )
