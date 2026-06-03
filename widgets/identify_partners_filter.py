"""Partner search filter bar — matches .prototype/sections/identify-partners.html."""

from __future__ import annotations

from theme.html_utils import render_html

_PREFIX = "nexus-identify-partners"

_SEARCH_ICON = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' "
    "fill='none' viewBox='0 0 24 24' stroke='%23111111' stroke-width='2.5'%3e"
    "%3ccircle cx='11' cy='11' r='8'/%3e%3cline x1='21' y1='21' x2='16.65' y2='16.65'/%3e"
    "%3c/svg%3e"
)
_CHEVRON_ICON = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' "
    "fill='none' viewBox='0 0 24 24' stroke='%23555555' stroke-width='2.5'%3e"
    "%3cpolyline points='6 9 12 15 18 9'/%3e%3c/svg%3e"
)


def identify_partners_styles() -> str:
    p = _PREFIX
    return f"""
        .{p} {{
            width: 100%;
            margin-bottom: 1.5rem;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }}

        .{p}__title {{
            font-size: 24px;
            font-weight: 700;
            color: #111111;
            margin: 0 0 24px 0;
            letter-spacing: -0.2px;
        }}

        .{p}__card {{
            background-color: #ffffff;
            border-radius: 4px;
            padding: 24px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            display: flex;
            gap: 12px;
            align-items: center;
            box-sizing: border-box;
        }}

        .{p}__search-wrap {{
            position: relative;
            flex: 1 1 auto;
            min-width: 0;
        }}

        .{p}__search-input {{
            width: 100%;
            height: 44px;
            padding: 0 40px 0 14px;
            font-size: 15px;
            color: #111111;
            background-color: #ffffff;
            border: 1px solid #757575;
            border-radius: 4px;
            box-sizing: border-box;
            outline: none;
        }}

        .{p}__search-input::placeholder {{
            color: #b0b0b0;
            opacity: 1;
        }}

        .{p}__search-icon {{
            position: absolute;
            right: 14px;
            top: 50%;
            transform: translateY(-50%);
            width: 18px;
            height: 18px;
            background: center / contain no-repeat url("{_SEARCH_ICON}");
            pointer-events: none;
        }}

        .{p}__select-wrap {{
            position: relative;
            min-width: 160px;
            flex-shrink: 0;
        }}

        .{p}__select {{
            width: 100%;
            height: 44px;
            padding: 0 36px 0 14px;
            font-size: 15px;
            color: #111111;
            background-color: #ffffff;
            border: 1px solid #757575;
            border-radius: 4px;
            box-sizing: border-box;
            cursor: pointer;
            outline: none;
            -webkit-appearance: none;
            -moz-appearance: none;
            appearance: none;
        }}

        .{p}__chevron {{
            position: absolute;
            right: 14px;
            top: 50%;
            transform: translateY(-50%);
            width: 10px;
            height: 10px;
            background: center / contain no-repeat url("{_CHEVRON_ICON}");
            pointer-events: none;
        }}

        .{p}__search-input:focus,
        .{p}__select:focus {{
            border-color: #111111;
            box-shadow: 0 0 0 1px #111111;
        }}

        @media (max-width: 768px) {{
            .{p}__card {{
                flex-direction: column;
                align-items: stretch;
            }}
            .{p}__select-wrap {{
                width: 100%;
            }}
        }}
    """


def inject_identify_partners_styles() -> None:
    render_html(f"<style>{identify_partners_styles()}</style>")


def build_identify_partners_html() -> str:
    p = _PREFIX
    return f"""
    <div class="{p}">
        <h2 class="{p}__title">Identify your partners and contact decision-makers directly</h2>
        <div class="{p}__card">
            <div class="{p}__search-wrap">
                <input type="text" class="{p}__search-input" placeholder="Search for a member"
                       aria-label="Search for a member">
                <span class="{p}__search-icon" aria-hidden="true"></span>
            </div>
            <div class="{p}__select-wrap">
                <select class="{p}__select" aria-label="Filter by Region">
                    <option value="" disabled selected hidden>Region</option>
                    <option value="north-america">North America</option>
                    <option value="europe">Europe</option>
                    <option value="asia">Asia</option>
                </select>
                <span class="{p}__chevron" aria-hidden="true"></span>
            </div>
            <div class="{p}__select-wrap">
                <select class="{p}__select" aria-label="Filter by Country">
                    <option value="" disabled selected hidden>Country</option>
                    <option value="us">United States</option>
                    <option value="uk">United Kingdom</option>
                    <option value="ca">Canada</option>
                </select>
                <span class="{p}__chevron" aria-hidden="true"></span>
            </div>
            <div class="{p}__select-wrap">
                <select class="{p}__select" aria-label="Filter by Product type">
                    <option value="" disabled selected hidden>Product type</option>
                    <option value="software">Software</option>
                    <option value="hardware">Hardware</option>
                    <option value="service">Services</option>
                </select>
                <span class="{p}__chevron" aria-hidden="true"></span>
            </div>
        </div>
    </div>
    """


def render_identify_partners_filter() -> None:
    inject_identify_partners_styles()
    render_html(build_identify_partners_html(), width="stretch")
