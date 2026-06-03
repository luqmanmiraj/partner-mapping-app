"""Help & Support Center Widget.

Approach requested by user:
    Render the full prototype CSS + HTML body in a single st.html() call.
    All CSS class names are prefixed with  ``hlp-``  to avoid global conflicts.
    The HTML structure mirrors help.html 1-to-1.

    FAQ accordion is handled with a <details>/<summary> pattern so it works
    inside the iframe sandbox without needing external JS.
"""

from __future__ import annotations

import streamlit as st

# ---------------------------------------------------------------------------
# FAQ data
# ---------------------------------------------------------------------------
_FAQ_ITEMS: list[dict[str, str]] = [
    {
        "q": "How do I update my company profile and contact information on the portal?",
        "a": (
            "Navigate to <strong>My Company</strong> in the sidebar, then select the "
            "<em>About</em> tab. Click <strong>Edit</strong> on any section to update "
            "your details. Changes are saved immediately and reflected across the network."
        ),
    },
    {
        "q": "How can I request access to a new Nexus service or programme?",
        "a": (
            "Go to <strong>Services</strong> in the left navigation menu. Browse the "
            "available services and click on any service card to view full details. "
            "Use the <strong>Book an appointment</strong> panel on the service page to "
            "schedule a consultation with the relevant Nexus team."
        ),
    },
    {
        "q": "Where can I find the latest news and partner announcements?",
        "a": (
            "The <strong>News &amp; Insights</strong> section (accessible from the sidebar) "
            "contains all NEXUS News, Member News, and Monthly Digest articles. "
            "Use the category filter to narrow down results."
        ),
    },
    {
        "q": "How do I submit a partner mapping file or declaration?",
        "a": (
            "Select <strong>Partner Mapping</strong> from the sidebar. Use the "
            "<em>Upload</em> tab to submit a new file, or the <em>History</em> tab to "
            "review previously submitted declarations. Supported formats: Excel (.xlsx)."
        ),
    },
    {
        "q": "Who do I contact if I have a technical issue with the platform?",
        "a": (
            "Use the <strong>Chat now</strong> button on the right panel of this page "
            "to reach our AI assistant instantly. For critical issues, email "
            "<a href='mailto:support@nexus.com' style='color:#000;font-weight:700;'>support@nexus.com</a> "
            "and our technical team will respond within one business day."
        ),
    },
    {
        "q": "How are new members onboarded to the Nexus Partner Portal?",
        "a": (
            "New members receive an automated welcome email with temporary credentials. "
            "After first login, a guided onboarding wizard will walk you through profile "
            "setup, document uploads, and service activation. Contact your regional Nexus "
            "representative if you have not received your credentials."
        ),
    },
]

# ---------------------------------------------------------------------------
# Category card definitions (icon SVG paths + label)
# ---------------------------------------------------------------------------
_CATEGORIES: list[dict[str, str]] = [
    {
        "label": "IT",
        "svg_paths": (
            "<path d='M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z'></path>"
            "<path d='M12 14c1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3 1.34 3 3 3z'></path>"
            "<path d='M12 2v2'></path><path d='M12 20v2'></path>"
            "<path d='M20 12h2'></path><path d='M2 12h2'></path>"
        ),
    },
    {
        "label": "Marketing",
        "svg_paths": (
            "<path d='M11 5h1a7 7 0 0 1 7 7v0a7 7 0 0 1-7 7h-1H3V5h8z'></path>"
            "<path d='M3 10h4'></path><path d='M3 14h4'></path><path d='M19 12h3'></path>"
        ),
    },
    {
        "label": "Sales",
        "svg_paths": (
            "<line x1='18' y1='20' x2='18' y2='10'></line>"
            "<line x1='12' y1='20' x2='12' y2='4'></line>"
            "<line x1='6' y1='20' x2='6' y2='14'></line>"
        ),
    },
]


# ---------------------------------------------------------------------------
# HTML builder
# ---------------------------------------------------------------------------



def _page_css() -> str:
    """Return CSS styles with zero indentation to prevent markdown-it preformatting parsing issues."""
    return """
<style>
/* ---- Core resets ---- */
.hlp-page-wrapper * {
margin: 0;
padding: 0;
box-sizing: border-box;
}

.hlp-page-wrapper {
font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
background-color: #f4f5f6;
color: #000000;
padding: 32px;
min-height: 100vh;
}

/* ---- Container & split layout ---- */
.hlp-container {
max-width: 1200px;
margin: 0 auto;
}

.hlp-split-layout {
display: grid;
grid-template-columns: 1fr 320px;
gap: 40px;
align-items: start;
}

/* ---- Left panel ---- */
.hlp-left-panel {
display: flex;
flex-direction: column;
}

.hlp-left-panel h1 {
font-size: 1.8rem;
font-weight: 700;
margin-bottom: 24px;
color: #000000;
}

/* ---- Search bar ---- */
.hlp-search-wrapper {
position: relative;
width: 100%;
margin-bottom: 32px;
}

.hlp-search-input {
width: 100%;
padding: 14px 48px 14px 16px;
font-size: 0.95rem;
border: 1px solid #b3b3b3;
border-radius: 4px;
background-color: #ffffff;
outline: none;
color: #333333;
font-family: inherit;
}

.hlp-search-input:focus {
border-color: #888888;
box-shadow: 0 0 0 2px rgba(0,0,0,0.06);
}

.hlp-search-icon-svg {
position: absolute;
right: 18px;
top: 50%;
transform: translateY(-50%);
width: 18px;
height: 18px;
fill: none;
stroke: #000000;
stroke-width: 2.5;
stroke-linecap: round;
stroke-linejoin: round;
pointer-events: none;
}

/* ---- Category section ---- */
.hlp-selection-heading {
font-size: 0.9rem;
font-weight: 600;
color: #444444;
margin-bottom: 16px;
display: block;
}

.hlp-category-cards-row {
display: flex;
gap: 16px;
margin-bottom: 48px;
flex-wrap: wrap;
}

.hlp-category-card {
background-color: #ffffff;
border-radius: 8px;
width: 130px;
height: 110px;
display: flex;
flex-direction: column;
align-items: center;
justify-content: center;
gap: 12px;
box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
cursor: pointer;
transition: box-shadow 0.15s ease, transform 0.15s ease;
flex-shrink: 0;
}

.hlp-category-card:hover {
box-shadow: 0 4px 12px rgba(0, 0, 0, 0.10);
transform: translateY(-2px);
}

.hlp-category-icon-svg {
width: 26px;
height: 26px;
fill: none;
stroke: #f39c12;
stroke-width: 2;
stroke-linecap: round;
stroke-linejoin: round;
}

.hlp-category-card span {
font-size: 0.92rem;
font-weight: 700;
color: #000000;
}

/* ---- FAQ section ---- */
.hlp-faq-section-title {
font-size: 1.45rem;
font-weight: 700;
margin-bottom: 24px;
color: #000000;
}

.hlp-faq-accordion-container {
display: flex;
flex-direction: column;
}

/* Use <details>/<summary> for native accordion toggle */
.hlp-faq-item-row {
border-bottom: 1px solid #dcdcdc;
list-style: none;
}

.hlp-faq-item-row[open] .hlp-faq-toggle-svg {
transform: rotate(180deg);
}

.hlp-faq-summary {
padding: 20px 0;
display: flex;
justify-content: space-between;
align-items: center;
cursor: pointer;
list-style: none;
outline: none;
gap: 16px;
}

.hlp-faq-summary::-webkit-details-marker {
display: none;
}

.hlp-faq-question-text {
font-size: 0.95rem;
font-weight: 700;
line-height: 1.4;
color: #000000;
flex: 1;
}

.hlp-faq-toggle-svg {
width: 14px;
height: 14px;
fill: none;
stroke: #000000;
stroke-width: 2.5;
stroke-linecap: round;
stroke-linejoin: round;
flex-shrink: 0;
transition: transform 0.2s ease;
}

.hlp-faq-answer {
font-size: 0.88rem;
color: #444444;
line-height: 1.6;
padding: 0 0 20px 0;
max-width: 680px;
}

/* ---- Right sidebar callout widget ---- */
.hlp-sidebar-callout-widget {
background-color: #fff9f2;
border-radius: 8px;
padding: 24px;
box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.hlp-widget-icon-svg {
width: 28px;
height: 28px;
fill: none;
stroke: #000000;
stroke-width: 2;
stroke-linecap: round;
stroke-linejoin: round;
margin-bottom: 16px;
display: block;
}

.hlp-sidebar-callout-widget h3 {
font-size: 1.15rem;
font-weight: 700;
color: #000000;
margin-bottom: 12px;
}

.hlp-sidebar-callout-widget p {
font-size: 0.92rem;
color: #333333;
line-height: 1.5;
margin-bottom: 24px;
}

.hlp-btn-chat {
display: inline-block;
background-color: #0f1115;
color: #ffffff;
font-size: 0.85rem;
font-weight: 700;
padding: 10px 20px;
border: none;
border-radius: 4px;
cursor: pointer;
text-decoration: none;
font-family: inherit;
transition: background-color 0.15s ease;
}

.hlp-btn-chat:hover {
background-color: #2c3035;
}

/* ---- Popular topics tag cloud ---- */
.hlp-popular-topics {
margin-top: 28px;
padding-top: 24px;
border-top: 1px solid #e8e0d5;
}

.hlp-popular-topics h4 {
font-size: 0.82rem;
font-weight: 700;
color: #555555;
margin-bottom: 12px;
text-transform: uppercase;
letter-spacing: 0.04em;
}

.hlp-topic-tags {
display: flex;
flex-wrap: wrap;
gap: 8px;
}

.hlp-topic-tag {
display: inline-block;
background-color: #f0ebe4;
color: #333333;
font-size: 0.78rem;
font-weight: 600;
padding: 5px 12px;
border-radius: 20px;
cursor: pointer;
transition: background-color 0.15s ease;
}

.hlp-topic-tag:hover {
background-color: #e8ddd3;
}

/* ---- Responsive ---- */
@media (max-width: 900px) {
.hlp-split-layout {
grid-template-columns: 1fr;
gap: 32px;
}
.hlp-category-cards-row {
flex-wrap: wrap;
}
}
</style>
"""


def _faq_rows_html() -> str:
    rows = []
    for item in _FAQ_ITEMS:
        rows.append(f"""<details class="hlp-faq-item-row">
<summary class="hlp-faq-summary">
<span class="hlp-faq-question-text">{item["q"]}</span>
<svg class="hlp-faq-toggle-svg" viewBox="0 0 24 24">
<polyline points="6 9 12 15 18 9"></polyline>
</svg>
</summary>
<div class="hlp-faq-answer">{item["a"]}</div>
</details>""")
    return "\n".join(rows)


def _category_cards_html() -> str:
    cards = []
    for cat in _CATEGORIES:
        cards.append(f"""<div class="hlp-category-card">
<svg class="hlp-category-icon-svg" viewBox="0 0 24 24">
{cat["svg_paths"]}
</svg>
<span>{cat["label"]}</span>
</div>""")
    return "\n".join(cards)


# ---------------------------------------------------------------------------
# HTML body builder
# ---------------------------------------------------------------------------
def _page_html() -> str:
    """Return HTML content body."""
    faq_rows = _faq_rows_html()
    cat_cards = _category_cards_html()

    return f"""<div class="hlp-page-wrapper">
<div class="hlp-container">
<div class="hlp-split-layout">

<!-- LEFT: main content -->
<main class="hlp-left-panel">

<h1>How can we help?</h1>

<div class="hlp-search-wrapper">
<input type="text" class="hlp-search-input" placeholder="Search for a topic...">
<svg class="hlp-search-icon-svg" viewBox="0 0 24 24">
<circle cx="11" cy="11" r="8"></circle>
<line x1="21" y1="21" x2="16.65" y2="16.65"></line>
</svg>
</div>

<span class="hlp-selection-heading">Or choose a category</span>

<div class="hlp-category-cards-row">
{cat_cards}
</div>

<section>
<h2 class="hlp-faq-section-title">Frequently asked questions</h2>
<div class="hlp-faq-accordion-container">
{faq_rows}
</div>
</section>

</main>

<!-- RIGHT: sidebar -->
<aside>
<div class="hlp-sidebar-callout-widget">
<svg class="hlp-widget-icon-svg" viewBox="0 0 24 24">
<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
</svg>
<h3>Need a quick answer?</h3>
<p>Ask our Nexus AI assistant for immediate help on platform usage, services, and partner processes.</p>
<button class="hlp-btn-chat">Chat now</button>

<div class="hlp-popular-topics">
<h4>Popular topics</h4>
<div class="hlp-topic-tags">
<span class="hlp-topic-tag">Partner mapping</span>
<span class="hlp-topic-tag">Onboarding</span>
<span class="hlp-topic-tag">Declarations</span>
<span class="hlp-topic-tag">Services</span>
<span class="hlp-topic-tag">Profile setup</span>
<span class="hlp-topic-tag">API access</span>
<span class="hlp-topic-tag">Reporting</span>
</div>
</div>
</div>
</aside>

</div>
</div>
</div>"""


# ---------------------------------------------------------------------------
# Public render function
# ---------------------------------------------------------------------------
def render_help_center() -> None:
    """Render the Help & Support Center page."""
    st.markdown(_page_css(), unsafe_allow_html=True)
    st.markdown(_page_html(), unsafe_allow_html=True)
