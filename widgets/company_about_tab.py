"""My Company About tab — description, product ranges, and offers."""

from __future__ import annotations

import html
from typing import Any

from theme.html_utils import render_html

_PREFIX = "nexus-company-about"
_OFFER_IMAGE = (
    "https://images.unsplash.com/photo-1619642751034-765dfdf7c58e?auto=format&fit=crop&w=600&q=80"
)

_ICON_BUILDING = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23f39c12' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4'/%3e%3c/svg%3e"
)
_ICON_STAR = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23f39c12' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 "
    "1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 "
    "0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.381-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z'/%3e%3c/svg%3e"
)
_ICON_EDIT = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23718096' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M12 20h9M16.5 3.5a2.121 2.121 0 113 3L7 19l-4 1 1-4 12.5-12.5z'/%3e%3c/svg%3e"
)
_ICON_PLUS = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23ffffff' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M12 5v14m7-7H5'/%3e%3c/svg%3e"
)
_ICON_CLOCK = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23111111' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z'/%3e%3c/svg%3e"
)


def company_about_tab_styles() -> str:
    p = _PREFIX
    return f"""
        .nexus-company-about {{
            width: 100%;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            gap: 24px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #111111;
            box-sizing: border-box;
        }}

        .nexus-company-about .dashboard-card {{
            background-color: #ffffff;
            border-radius: 6px;
            padding: 30px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            position: relative;
        }}

        .nexus-company-about .card-header-row {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 16px;
        }}

        .nexus-company-about .card-title-icon {{
            width: 20px;
            height: 20px;
            background: center / contain no-repeat;
            display: inline-block;
        }}

        .nexus-company-about .card-title-icon--building {{
            background-image: url("{_ICON_BUILDING}");
        }}

        .nexus-company-about .card-title-icon--star {{
            background-image: url("{_ICON_STAR}");
        }}

        .nexus-company-about .dashboard-card h3 {{
            font-size: 1.4rem;
            font-weight: 700;
            color: #111111;
            margin: 0;
        }}

        .nexus-company-about .dashboard-card p {{
            font-size: 0.98rem;
            line-height: 1.6;
            color: #4a5568;
            margin: 0;
        }}

        /* Inline Action Utility Buttons */
        .nexus-company-about .edit-action-btn {{
            position: absolute;
            top: 25px;
            right: 25px;
            background-color: #edf2f7;
            border: none;
            color: #718096;
            width: 28px;
            height: 28px;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: background-color 0.15s ease;
        }}

        .nexus-company-about .edit-action-btn:hover {{
            background-color: #e2e8f0;
            color: #1a1a1a;
        }}

        .nexus-company-about .edit-action-btn::after {{
            content: "";
            width: 14px;
            height: 14px;
            background: url("{_ICON_EDIT}") center / contain no-repeat;
        }}

        /* Pill Badges Grid */
        .nexus-company-about .pill-box-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 5px;
        }}

        .nexus-company-about .range-pill {{
            background-color: #fdeed6;
            color: #4a3319;
            font-size: 0.88rem;
            font-weight: 600;
            padding: 6px 14px;
            border-radius: 6px;
        }}

        /* Commercial Offers Section */
        .nexus-company-about .offers-section-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 10px;
        }}

        .nexus-company-about .offers-section-header h2 {{
            font-size: 1.6rem;
            font-weight: 700;
            color: #111111;
            margin: 0;
        }}

        .nexus-company-about .add-offer-btn {{
            background-color: #0b0f19;
            color: #ffffff;
            border: none;
            border-radius: 4px;
            padding: 10px 18px;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: background-color 0.15s ease;
        }}

        .nexus-company-about .add-offer-btn:hover {{
            background-color: #1a2336;
        }}

        .nexus-company-about .add-offer-btn::before {{
            content: "";
            width: 14px;
            height: 14px;
            background: url("{_ICON_PLUS}") center / contain no-repeat;
        }}

        .nexus-company-about .offer-banner-card {{
            position: relative;
            border-radius: 6px;
            overflow: hidden;
            height: 200px;
            display: grid;
            grid-template-columns: 1.1fr 1fr;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        }}

        /* Offer Variant 1: Active Deal State */
        .nexus-company-about .offer-banner-card.active-state {{
            background: #111111 linear-gradient(135deg, #1f1406 0%, #0a0e17 100%);
        }}

        /* Offer Variant 2: Pending State styling */
        .nexus-company-about .offer-banner-card.pending-state {{
            background: #7f7f7f linear-gradient(135deg, #b3aba2 0%, #8d9199 100%);
        }}

        .nexus-company-about .offer-details-side {{
            padding: 30px 45px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            z-index: 2;
            box-sizing: border-box;
        }}

        .nexus-company-about .offer-tagline {{
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #cbd5e0;
            margin-bottom: 8px;
        }}

        .nexus-company-about .offer-details-side h3 {{
            color: #ffffff;
            font-size: 1.75rem;
            font-weight: 700;
            margin: 0 0 6px 0;
            letter-spacing: -0.5px;
        }}

        .nexus-company-about .offer-duration {{
            font-size: 0.88rem;
            color: #a0aec0;
            margin-bottom: 18px;
        }}

        .nexus-company-about .offer-banner-card.pending-state .offer-duration {{
            color: #e2e8f0;
        }}

        .nexus-company-about .offer-action-link {{
            background-color: #ffffff;
            color: #111111;
            border-radius: 4px;
            padding: 10px 22px;
            font-size: 0.95rem;
            font-weight: 700;
            text-decoration: none;
            width: fit-content;
            text-align: center;
            box-sizing: border-box;
        }}

        .nexus-company-about .offer-banner-card.pending-state .offer-action-link {{
            background-color: rgba(255, 255, 255, 0.5);
            color: #ffffff;
            pointer-events: none;
        }}

        /* Graphic Asset Container Side */
        .nexus-company-about .offer-media-side {{
            position: relative;
            background-image: url("{_OFFER_IMAGE}");
            background-position: center;
            background-size: cover;
            background-repeat: no-repeat;
        }}

        .nexus-company-about .offer-banner-card.pending-state .offer-media-side {{
            opacity: 0.35;
        }}

        /* Status and Control Overlays on Banners */
        .nexus-company-about .status-badge-container {{
            position: absolute;
            top: 20px;
            right: 20px;
            z-index: 5;
        }}

        .nexus-company-about .pending-status-pill {{
            background-color: #ffffff;
            color: #111111;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 6px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }}

        .nexus-company-about .pending-status-pill::before {{
            content: "";
            width: 14px;
            height: 14px;
            background: url("{_ICON_CLOCK}") center / contain no-repeat;
        }}

        .nexus-company-about .inline-banner-edit {{
            position: absolute;
            top: 20px;
            right: 20px;
            z-index: 5;
            cursor: pointer;
            width: 28px;
            height: 28px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .nexus-company-about .inline-banner-edit::after {{
            content: "";
            width: 14px;
            height: 14px;
            background: url("{_ICON_EDIT}") center / contain no-repeat;
            filter: brightness(0) invert(1);
            opacity: 0.7;
        }}

        @media (max-width: 850px) {{
            .nexus-company-about .offer-banner-card {{
                grid-template-columns: 1fr;
                height: auto;
            }}
            .nexus-company-about .offer-details-side {{
                padding: 35px 24px;
                align-items: center;
                text-align: center;
            }}
            .nexus-company-about .offer-media-side {{
                height: 160px;
            }}
            .nexus-company-about .status-badge-container {{
                top: auto;
                bottom: 180px;
                right: 20px;
            }}
            .nexus-company-about .inline-banner-edit {{
                top: auto;
                bottom: 180px;
                right: 20px;
            }}
        }}
    """


def _offer_html(offer: dict[str, str]) -> str:
    state = offer.get("state", "active")
    is_pending = state == "pending"
    badge = ""
    edit = '<span class="inline-banner-edit" aria-label="Edit promo"></span>'
    if is_pending:
        badge = (
            '<div class="status-badge-container">'
            '<div class="pending-status-pill">Pending</div>'
            '</div>'
        )
        edit = ""

    return f"""
    <div class="offer-banner-card {"pending-state" if is_pending else "active-state"}">
        {edit}
        {badge}
        <div class="offer-details-side">
            <span class="offer-tagline">{html.escape(offer["tagline"])}</span>
            <h3>{html.escape(offer["title"])}</h3>
            <span class="offer-duration">{html.escape(offer["duration"])}</span>
            <a href="#" class="offer-action-link">{html.escape(offer["cta"])}</a>
        </div>
        <div class="offer-media-side"></div>
    </div>
    """


def build_company_about_tab_html(data: dict[str, Any]) -> str:
    pills = "".join(
        f'<span class="range-pill">{html.escape(item)}</span>'
        for item in data.get("product_ranges", [])
    )
    offers = "".join(_offer_html(offer) for offer in data.get("offers", []))

    return f"""
    <div class="nexus-company-about">
        <section class="dashboard-card">
            <button class="edit-action-btn" aria-label="Edit description"></button>
            <div class="card-header-row">
                <div class="card-title-icon card-title-icon--building"></div>
                <h3>About</h3>
            </div>
            <p>{html.escape(str(data["description"]))}</p>
        </section>

        <section class="dashboard-card">
            <button class="edit-action-btn" aria-label="Edit product ranges"></button>
            <div class="card-header-row">
                <div class="card-title-icon card-title-icon--star"></div>
                <h3>Expertise &amp; Product Ranges</h3>
            </div>
            <div class="pill-box-container">{pills}</div>
        </section>

        <section class="nexus-company-about" style="gap: 16px;">
            <div class="offers-section-header">
                <h2>Active offers</h2>
                <button class="add-offer-btn">Add New Offer</button>
            </div>
            {offers}
        </section>
    </div>
    """


def inject_company_about_tab_styles() -> None:
    render_html(f"<style>{company_about_tab_styles()}</style>")


def render_company_about_tab(data: dict[str, Any]) -> None:
    inject_company_about_tab_styles()
    render_html(build_company_about_tab_html(data), width="stretch")

