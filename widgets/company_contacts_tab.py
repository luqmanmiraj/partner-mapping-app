"""My Company Contacts tab — help.py pattern from company_contacts-tab.html.

CSS/HTML use ``cmpc-`` prefixed classes (like ``hlp-`` on help). Rendered via one
``st.html`` call with ``width="stretch"`` for full-width layout.
"""

from __future__ import annotations

import html

import streamlit as st

_SVG_SEARCH = """<svg class="cmpc-search-icon-svg" viewBox="0 0 24 24" aria-hidden="true">
<circle cx="11" cy="11" r="7"></circle>
<line x1="21" y1="21" x2="16.65" y2="16.65"></line>
</svg>"""

_SVG_PLUS = """<svg class="cmpc-btn-icon-svg" viewBox="0 0 24 24" aria-hidden="true">
<line x1="12" y1="5" x2="12" y2="19"></line>
<line x1="5" y1="12" x2="19" y2="12"></line>
</svg>"""

_SVG_ELLIPSIS = """<svg class="cmpc-options-icon-svg" viewBox="0 0 24 24" aria-hidden="true">
<circle cx="5" cy="12" r="1.5" fill="currentColor" stroke="none"></circle>
<circle cx="12" cy="12" r="1.5" fill="currentColor" stroke="none"></circle>
<circle cx="19" cy="12" r="1.5" fill="currentColor" stroke="none"></circle>
</svg>"""

_SVG_USER = """<svg class="cmpc-meta-icon-svg" viewBox="0 0 24 24" aria-hidden="true">
<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
<circle cx="12" cy="7" r="4"></circle>
</svg>"""

_SVG_MAP = """<svg class="cmpc-meta-icon-svg" viewBox="0 0 24 24" aria-hidden="true">
<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
<circle cx="12" cy="10" r="3"></circle>
</svg>"""

_SVG_MAIL = """<svg class="cmpc-meta-icon-svg" viewBox="0 0 24 24" aria-hidden="true">
<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
<polyline points="22,6 12,13 2,6"></polyline>
</svg>"""

_SVG_CHEV_LEFT = """<svg class="cmpc-page-arrow-svg" viewBox="0 0 24 24" aria-hidden="true">
<polyline points="15 18 9 12 15 6"></polyline>
</svg>"""

_SVG_CHEV_RIGHT = """<svg class="cmpc-page-arrow-svg" viewBox="0 0 24 24" aria-hidden="true">
<polyline points="9 18 15 12 9 6"></polyline>
</svg>"""


def _page_css() -> str:
    """Prototype CSS with cmpc- prefix; zero indent like help.py; no max-width."""
    return """
<style>
.cmpc-page-wrapper * {
margin: 0;
padding: 0;
box-sizing: border-box;
}

.cmpc-page-wrapper {
font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
color: #111111;
width: 100%;
}

.cmpc-dashboard-container {
width: 100%;
margin: 0;
background-color: #ffffff;
border-radius: 8px;
padding: 30px;
box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.cmpc-control-bar {
display: flex;
gap: 15px;
margin-bottom: 25px;
align-items: center;
flex-wrap: wrap;
}

.cmpc-search-wrapper {
position: relative;
flex: 1;
min-width: 280px;
}

.cmpc-search-input {
width: 100%;
padding: 10px 16px 10px 40px;
font-size: 0.9rem;
border: 1.5px solid #cbd5e0;
border-radius: 6px;
color: #2d3748;
outline: none;
font-family: inherit;
}

.cmpc-search-input::placeholder {
color: #a0aec0;
}

.cmpc-search-icon-svg {
position: absolute;
left: 14px;
top: 50%;
transform: translateY(-50%);
width: 16px;
height: 16px;
fill: none;
stroke: #4a5568;
stroke-width: 2;
stroke-linecap: round;
stroke-linejoin: round;
pointer-events: none;
}

.cmpc-filter-dropdown {
padding: 10px 35px 10px 16px;
font-size: 0.9rem;
border: 1.5px solid #cbd5e0;
border-radius: 6px;
background-color: #ffffff;
color: #2d3748;
cursor: pointer;
outline: none;
appearance: none;
font-family: inherit;
background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='10' height='6' viewBox='0 0 10 6'><path fill='%234a5568' d='M0 0l5 5 5-5z'/></svg>");
background-repeat: no-repeat;
background-position: right 14px center;
}

.cmpc-add-contact-btn {
background-color: #0b0f19;
color: #ffffff;
border: none;
border-radius: 6px;
padding: 11px 20px;
font-size: 0.9rem;
font-weight: 600;
cursor: pointer;
display: inline-flex;
align-items: center;
gap: 8px;
margin-left: auto;
transition: background-color 0.15s ease;
font-family: inherit;
}

.cmpc-add-contact-btn:hover {
background-color: #1a2336;
}

.cmpc-btn-icon-svg {
width: 14px;
height: 14px;
fill: none;
stroke: #ffffff;
stroke-width: 2;
stroke-linecap: round;
stroke-linejoin: round;
flex-shrink: 0;
}

.cmpc-contacts-grid {
display: grid;
grid-template-columns: repeat(3, 1fr);
gap: 20px;
margin-bottom: 35px;
}

.cmpc-contact-card {
background-color: #ffffff;
border: 1.5px solid #e2e8f0;
border-radius: 8px;
overflow: hidden;
}

.cmpc-card-profile-header {
background-color: #f8fafc;
padding: 16px;
display: flex;
align-items: center;
gap: 14px;
border-bottom: 1.5px solid #e2e8f0;
position: relative;
}

.cmpc-profile-avatar {
width: 46px;
height: 46px;
border-radius: 50%;
object-fit: cover;
background-color: #cbd5e0;
flex-shrink: 0;
}

.cmpc-profile-name-details {
display: flex;
flex-direction: column;
overflow: hidden;
min-width: 0;
}

.cmpc-profile-name-details h4 {
font-size: 1rem;
font-weight: 700;
color: #1a1a1a;
white-space: nowrap;
overflow: hidden;
text-overflow: ellipsis;
margin-bottom: 2px;
}

.cmpc-profile-name-details span {
font-size: 0.85rem;
color: #718096;
white-space: nowrap;
overflow: hidden;
text-overflow: ellipsis;
}

.cmpc-card-options-btn {
position: absolute;
top: 16px;
right: 14px;
color: #718096;
background: none;
border: none;
cursor: pointer;
padding: 0;
display: flex;
align-items: center;
}

.cmpc-options-icon-svg {
width: 18px;
height: 18px;
}

.cmpc-card-meta-body {
padding: 16px;
display: flex;
flex-direction: column;
gap: 12px;
}

.cmpc-meta-line {
display: flex;
align-items: center;
gap: 12px;
color: #4a5568;
font-size: 0.88rem;
}

.cmpc-meta-icon-svg {
width: 16px;
height: 16px;
fill: none;
stroke: #718096;
stroke-width: 2;
stroke-linecap: round;
stroke-linejoin: round;
flex-shrink: 0;
}

.cmpc-pagination {
display: flex;
justify-content: center;
align-items: center;
gap: 8px;
margin-top: 10px;
}

.cmpc-page-btn {
background: none;
border: none;
color: #4a5568;
font-size: 0.9rem;
font-weight: 600;
width: 32px;
height: 32px;
display: flex;
align-items: center;
justify-content: center;
border-radius: 4px;
cursor: pointer;
padding: 0;
font-family: inherit;
}

.cmpc-page-btn.active {
color: #1a1a1a;
font-weight: 800;
}

.cmpc-page-arrow-svg {
width: 14px;
height: 14px;
fill: none;
stroke: #4a5568;
stroke-width: 2;
stroke-linecap: round;
stroke-linejoin: round;
}

@media (max-width: 1024px) {
.cmpc-contacts-grid {
grid-template-columns: repeat(2, 1fr);
}
}

@media (max-width: 730px) {
.cmpc-control-bar {
flex-direction: column;
align-items: stretch;
}
.cmpc-add-contact-btn {
margin-left: 0;
justify-content: center;
}
.cmpc-contacts-grid {
grid-template-columns: 1fr;
gap: 16px;
}
}
</style>
"""


def _contact_card(contact: dict[str, str]) -> str:
    avatar = html.escape(contact.get("avatar", ""))
    return f"""<div class="cmpc-contact-card">
<div class="cmpc-card-profile-header">
<img class="cmpc-profile-avatar" src="{avatar}" alt="Profile Headshot">
<div class="cmpc-profile-name-details">
<h4>{html.escape(contact["name"])}</h4>
<span>{html.escape(contact["position"])}</span>
</div>
<button type="button" class="cmpc-card-options-btn" aria-label="More options">{_SVG_ELLIPSIS}</button>
</div>
<div class="cmpc-card-meta-body">
<div class="cmpc-meta-line">{_SVG_USER}<span>{html.escape(contact["segment"])}</span></div>
<div class="cmpc-meta-line">{_SVG_MAP}<span>{html.escape(contact["region"])}</span></div>
<div class="cmpc-meta-line">{_SVG_MAIL}<span>{html.escape(contact["email"])}</span></div>
</div>
</div>"""


def _page_html(contacts: list[dict[str, str]]) -> str:
    cards = "\n".join(_contact_card(c) for c in contacts)
    return f"""<div class="cmpc-page-wrapper">
<div class="cmpc-dashboard-container">
<div class="cmpc-control-bar">
<div class="cmpc-search-wrapper">
{_SVG_SEARCH}
<input type="text" class="cmpc-search-input" placeholder="Search for a topic..." readonly>
</div>
<select class="cmpc-filter-dropdown" disabled><option>Region</option></select>
<button type="button" class="cmpc-add-contact-btn">
{_SVG_PLUS}
Add New Contact
</button>
</div>
<main class="cmpc-contacts-grid">
{cards}
</main>
<footer class="cmpc-pagination">
<button type="button" class="cmpc-page-btn" aria-label="Previous Page">{_SVG_CHEV_LEFT}</button>
<button type="button" class="cmpc-page-btn active">1</button>
<button type="button" class="cmpc-page-btn">2</button>
<button type="button" class="cmpc-page-btn">3</button>
<button type="button" class="cmpc-page-btn" aria-label="Next Page">{_SVG_CHEV_RIGHT}</button>
</footer>
</div>
</div>"""


def render_company_contacts_tab(contacts: list[dict[str, str]]) -> None:
    st.html(f"{_page_css()}{_page_html(contacts)}", width="stretch")  # type: ignore[arg-type]
