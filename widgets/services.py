"""Services Catalog Widget — matches .prototype/services/services.html."""

from __future__ import annotations

import html
from typing import Any

import streamlit as st

from data.services_fixtures import SERVICES_LIST
from theme.html_utils import render_html

_PREFIX = "nexus-services-catalog"

_ICON_SEARCH = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23757575' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z'/%3e%3c/svg%3e"
)

_ICON_ARROW_RIGHT = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23000000' stroke-width='2.5' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M14 5l7 7m0 0l-7 7m7-7H3'/%3e%3c/svg%3e"
)

_ICON_STAR_REGULAR = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23f39c12' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 "
    "1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 "
    "0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.381-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z'/%3e%3c/svg%3e"
)


def services_catalog_styles() -> str:
    """Return CSS styles with zero indentation to prevent markdown preformatting parsing issues."""
    return f"""
<style>
/* --- Base Resets & Global Layout Styles --- */
.srv-page-wrapper * {{
margin: 0;
padding: 0;
box-sizing: border-box;
}}

.srv-page-wrapper {{
font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
background-color: #eeeeee;
color: #111111;
padding: 40px 24px;
min-height: 100vh;
}}

.srv-catalog-container {{
max-width: 1040px;
margin: 0 auto;
display: flex;
flex-direction: column;
gap: 16px;
}}

/* ==========================================
   SECTION 1: Header & Typography Content
   ========================================== */
.srv-catalog-header h1 {{
font-size: 1.55rem;
font-weight: 700;
color: #000000;
margin-bottom: 12px;
letter-spacing: -0.2px;
}}

.srv-catalog-header p {{
font-size: 0.95rem;
color: #111111;
line-height: 1.4;
margin-bottom: 8px;
}}

/* ==========================================
   SECTION 2: Input Controls Box
   ========================================== */
div[data-testid="stTextInput"].nexus-services-catalog-search-input {{
padding: 0 !important;
margin-bottom: 16px !important;
width: 100% !important;
}}

div[data-testid="stTextInput"].nexus-services-catalog-search-input label {{
display: none !important;
}}

div[data-testid="stTextInput"].nexus-services-catalog-search-input [data-testid="stTextInputRootElement"] {{
background-color: #fafafa !important;
border: 1px solid #757575 !important;
border-radius: 4px !important;
height: 48px !important;
box-sizing: border-box !important;
box-shadow: none !important;
position: relative !important;
}}

div[data-testid="stTextInput"].nexus-services-catalog-search-input [data-testid="stTextInputRootElement"]:focus-within {{
border-color: #f39c12 !important;
}}

div[data-testid="stTextInput"].nexus-services-catalog-search-input input {{
background-color: transparent !important;
color: #222222 !important;
font-size: 0.88rem !important;
padding: 12px 45px 12px 14px !important;
border: none !important;
box-shadow: none !important;
outline: none !important;
font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
height: 100% !important;
}}

div[data-testid="stTextInput"].nexus-services-catalog-search-input [data-testid="stTextInputRootElement"]::after {{
content: "";
position: absolute;
right: 16px;
top: 50%;
transform: translateY(-50%) scaleX(-1);
width: 18px;
height: 18px;
background: url("{_ICON_SEARCH}") center / contain no-repeat;
pointer-events: none;
display: block;
}}

/* ==========================================
   SECTION 3: Multi-column Flex Matrix Cards
   ========================================== */
.srv-catalog-grid {{
display: grid;
grid-template-columns: repeat(2, 1fr);
gap: 24px;
}}

.srv-catalog-card {{
background-color: #ffffff;
border-radius: 4px;
padding: 30px 24px 24px 24px;
display: flex;
gap: 16px;
position: relative;
box-shadow: 0 1px 2px rgba(0,0,0,0.02);
text-align: left;
}}

/* Custom Favorite Star Box Structural Layout */
.srv-star-badge-box {{
width: 36px;
height: 36px;
background-color: #f5f5f5;
border-radius: 4px;
display: flex;
align-items: center;
justify-content: center;
flex-shrink: 0;
}}

.srv-star-badge-icon {{
width: 17px;
height: 17px;
background: url("{_ICON_STAR_REGULAR}") center / contain no-repeat;
display: block;
}}

/* Inner Card Typography Content Details */
.srv-card-content {{
display: flex;
flex-direction: column;
width: 100%;
}}

.srv-card-content h2 {{
font-size: 1.05rem;
font-weight: 700;
color: #000000;
margin-bottom: 6px;
margin-top: 2px;
line-height: 1.2;
}}

.srv-card-content p {{
font-size: 0.86rem;
color: #555555;
line-height: 1.45;
margin-bottom: 30px;
}}

/* Dynamic Action Forward Redirect Links */
.srv-action-link-wrapper {{
margin-left: auto;
margin-top: auto;
display: inline-flex;
align-items: center;
gap: 8px;
text-decoration: none;
color: #000000;
cursor: pointer;
transition: color 0.15s ease;
}}

.srv-action-link-wrapper span {{
font-size: 0.92rem;
font-weight: 700;
}}

.srv-arrow-icon {{
width: 14px;
height: 14px;
background: url("{_ICON_ARROW_RIGHT}") center / contain no-repeat;
display: inline-block;
transition: transform 0.15s ease;
}}

.srv-action-link-wrapper:hover {{
color: #f39c12;
}}

.srv-action-link-wrapper:hover .srv-arrow-icon {{
transform: translateX(3px);
}}

/* ==========================================
   SECTION 4: Empty State
   ========================================== */
.srv-catalog-empty {{
text-align: center;
padding: 40px;
background-color: #ffffff;
border-radius: 4px;
color: #757575;
font-size: 0.9rem;
box-shadow: 0 1px 2px rgba(0,0,0,0.02);
}}

/* ==========================================
   SECTION 4.5: Hidden Single-Page Transition Buttons
   ========================================== */
div[class*="st-key-see_more_"] {{
position: absolute !important;
opacity: 0 !important;
width: 0 !important;
height: 0 !important;
overflow: hidden !important;
pointer-events: none !important;
margin: 0 !important;
padding: 0 !important;
border: none !important;
}}
.srv-hidden-triggers {{
display: none !important;
}}

/* ==========================================
   SECTION 5: Adaptive Breakpoint System
   ========================================== */
@media (max-width: 768px) {{
.srv-catalog-grid {{
grid-template-columns: 1fr;
gap: 16px;
}}
.srv-page-wrapper {{
padding: 24px 16px;
}}
}}
</style>
"""


def _page_html(filtered_services: list[dict[str, Any]], search_query: str) -> str:
    """Return the raw HTML page wrapper with header, grid, and catalog cards with zero leading indentation."""
    header_html = f"""<header class="srv-catalog-header">
<h1>Service Catalog</h1>
<p>Explore Nexus services and programmes. Select any service to view detailed resources, directory contacts, or schedule a session with our consultants.</p>
</header>"""

    if not filtered_services:
        grid_html = f"""<div class="srv-catalog-empty">No services found matching "{html.escape(search_query)}".</div>"""
    else:
        card_elements = []
        for service in filtered_services:
            service_id = service["id"]
            title_esc = html.escape(service["title"])
            desc_esc = html.escape(service["description"])
            
            card_elements.append(f"""<div class="srv-catalog-card">
<div class="srv-star-badge-box">
<span class="srv-star-badge-icon"></span>
</div>
<div class="srv-card-content">
<h2>{title_esc}</h2>
<p>{desc_esc}</p>
<a class="srv-action-link-wrapper" href="#" onclick="(window.parent.document.querySelector('.st-key-see_more_{service_id} button') || document.querySelector('.st-key-see_more_{service_id} button')).click(); return false;">
<span>See more</span>
<span class="srv-arrow-icon"></span>
</a>
</div>
</div>""")
        
        grid_html = f"""<main class="srv-catalog-grid">
{"".join(card_elements)}
</main>"""

    return f"""<div class="srv-page-wrapper">
<div class="srv-catalog-container">
{header_html}
{grid_html}
</div>
</div>"""


def render_services_catalog() -> None:
    """Render the Services Catalog dashboard with keyword filter."""
    # 1. Inject CSS stylesheet (zero-indented, using st.markdown)
    st.markdown(services_catalog_styles(), unsafe_allow_html=True)

    # 2. Render standard Streamlit text input search box styled exactly like prototype
    search_query = st.text_input(
        "Search for a topic...",
        key="services_search_input",
        placeholder="Search for a topic...",
        label_visibility="collapsed",
    )

    # Apply search class hook script
    st.html(
        f"""
        <script>
        (function() {{
            const els = window.parent.document.querySelectorAll('.st-key-services_search_input');
            els.forEach(el => {{
                if (!el.classList.contains('nexus-services-catalog-search-input')) {{
                    el.classList.add('nexus-services-catalog-search-input');
                }}
            }});
        }})();
        </script>
        """
    )

    # 3. Filtering Logic
    query = search_query.strip().lower()
    if query:
        filtered_services = [
            s
            for s in SERVICES_LIST
            if query in s["title"].lower() or query in s["description"].lower()
        ]
    else:
        filtered_services = SERVICES_LIST

    # 4. Render pure HTML grid container (zero-indented f-string)
    st.markdown(_page_html(filtered_services, search_query), unsafe_allow_html=True)

    # 5. Render invisible transition buttons at the bottom of the page
    st.write('<div class="srv-hidden-triggers">', unsafe_allow_html=True)
    for service in filtered_services:
        service_id = service["id"]
        if st.button("See more", key=f"see_more_{service_id}"):
            st.session_state.active_service_id = service_id
            st.rerun()
    st.write('</div>', unsafe_allow_html=True)
