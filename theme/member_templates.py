"""Helpers to render static member persona HTML prototypes via `st.html`."""

from __future__ import annotations

import html
import re
from functools import lru_cache
from pathlib import Path

import streamlit as st

from theme.html_utils import _normalize_css, render_styled_html


_ROOT = Path(__file__).resolve().parents[1]
_TEMPLATES_DIR = _ROOT / ".prototype" / "member_pages"

_FONT_AWESOME_CDN = (
    '<link rel="stylesheet" '
    'href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">'
)
_FONT_AWESOME_IMPORT = (
    "@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');"
)

# Streamlit-side layout overrides for member dashboard (appended inside st.html).
MEMBER_DASHBOARD_LAYOUT_CSS = """
.member-dashboard {
    background: transparent !important;
    padding: 0 !important;
    min-height: 0 !important;
}

.member-dashboard-container {
    max-width: none !important;
    width: 100% !important;
}
"""

MEMBER_OFFERS_LAYOUT_CSS = """
.member-offers {
    background: transparent !important;
    padding: 0 !important;
    align-items: stretch !important;
}

.member-offers-container {
    max-width: none !important;
    width: 100% !important;
}

.member-offers-search-icon,
.member-offers-time-left i,
.member-offers-download-btn i,
.member-offers-status i,
.member-offers-profile-link i,
.member-offers-page-btn i {
    color: inherit;
}

.member-offers-search-icon {
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 14px;
    color: #9ca3af;
    pointer-events: none;
}

.member-offers-time-left i,
.member-offers-status i {
    color: #6b7280;
}

.member-offers-download-btn i {
    font-size: 16px;
    color: #4b5563;
}

.member-offers-status i {
    color: #f59e0b;
}
"""

MEMBER_SUPPLIER_PORTFOLIO_LAYOUT_CSS = """
.supplier-portfolio {
    background: transparent !important;
    padding: 0 !important;
}

.supplier-portfolio-container {
    max-width: none !important;
    width: 100% !important;
}
"""

MEMBER_COMPANY_LAYOUT_CSS = """
.member-company-body {
    padding: 0 !important;
}

.member-company-container,
.member-company-contact-container,
.member-company-contact-content-body,
.member-company-media-container,
.member-company-idcard-container {
    max-width: none !important;
    width: 100% !important;
}

.member-company-container {
    padding: 0 !important;
}
"""

_MEMBER_PAGE_LAYOUT_CSS: dict[str, str] = {
    "member-dashboard": MEMBER_DASHBOARD_LAYOUT_CSS,
    "offers": MEMBER_OFFERS_LAYOUT_CSS,
    "supplier-portfolio": MEMBER_SUPPLIER_PORTFOLIO_LAYOUT_CSS,
}

_MEMBER_DASHBOARD_SALES_MARKER = "<!-- member-dashboard:sales -->"

_COMPANY_TAB_PANEL_SCOPE_CSS = """
.member-company-tab-panel--medias .member-company-media-root {
  background-color: #f4f6f8;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  color: #333333;
}

.member-company-tab-panel--idcard .member-company-idcard-root {
  background-color: #f3f4f6;
  padding: 16px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  color: #333333;
}

.member-company-tab-panel--idcard .member-company-idcard-content-section {
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}
"""

# CSS-only tabs: hidden radios + labels (no iframe, no JavaScript).
_COMPANY_TAB_CONTROLS = """
    <input type="radio" name="member-company-tab" id="member-company-tab-about" class="member-company-tab-radio" checked>
    <input type="radio" name="member-company-tab" id="member-company-tab-contacts" class="member-company-tab-radio">
    <input type="radio" name="member-company-tab" id="member-company-tab-medias" class="member-company-tab-radio">
    <input type="radio" name="member-company-tab" id="member-company-tab-idcard" class="member-company-tab-radio">
    <nav class="member-company-tabs-nav">
      <ul class="member-company-tabs-list">
        <li class="member-company-tab-item"><label for="member-company-tab-about">About</label></li>
        <li class="member-company-tab-item"><label for="member-company-tab-contacts">Contacts</label></li>
        <li class="member-company-tab-item"><label for="member-company-tab-medias">Medias</label></li>
        <li class="member-company-tab-item"><label for="member-company-tab-idcard">ID Card</label></li>
      </ul>
    </nav>
"""

_COMPANY_TAB_PANEL_CSS = """
.member-company-tab-radio {
  position: fixed;
  opacity: 0;
  width: 0;
  height: 0;
  margin: 0;
  padding: 0;
  pointer-events: none;
}

.member-company-tabs-list label {
  cursor: pointer;
  text-decoration: none;
  color: #6b7280;
  font-weight: 600;
  font-size: 14px;
  display: block;
}

.member-company-tab-panels > .member-company-tab-panel,
.member-company-tab-panels > main.member-company-tab-panel {
  display: none !important;
}

#member-company-tab-about:checked ~ .member-company-tab-panels > .member-company-tab-panel--about,
#member-company-tab-contacts:checked ~ .member-company-tab-panels > .member-company-tab-panel--contacts,
#member-company-tab-medias:checked ~ .member-company-tab-panels > .member-company-tab-panel--medias,
#member-company-tab-idcard:checked ~ .member-company-tab-panels > .member-company-tab-panel--idcard {
  display: block !important;
}

#member-company-tab-about:checked ~ .member-company-tabs-nav .member-company-tabs-list li:nth-child(1) label,
#member-company-tab-contacts:checked ~ .member-company-tabs-nav .member-company-tabs-list li:nth-child(2) label,
#member-company-tab-medias:checked ~ .member-company-tabs-nav .member-company-tabs-list li:nth-child(3) label,
#member-company-tab-idcard:checked ~ .member-company-tabs-nav .member-company-tabs-list li:nth-child(4) label {
  color: #111827;
}

#member-company-tab-about:checked ~ .member-company-tabs-nav .member-company-tabs-list li:nth-child(1),
#member-company-tab-contacts:checked ~ .member-company-tabs-nav .member-company-tabs-list li:nth-child(2),
#member-company-tab-medias:checked ~ .member-company-tabs-nav .member-company-tabs-list li:nth-child(3),
#member-company-tab-idcard:checked ~ .member-company-tabs-nav .member-company-tabs-list li:nth-child(4) {
  position: relative;
}

#member-company-tab-about:checked ~ .member-company-tabs-nav .member-company-tabs-list li:nth-child(1)::after,
#member-company-tab-contacts:checked ~ .member-company-tabs-nav .member-company-tabs-list li:nth-child(2)::after,
#member-company-tab-medias:checked ~ .member-company-tabs-nav .member-company-tabs-list li:nth-child(3)::after,
#member-company-tab-idcard:checked ~ .member-company-tabs-nav .member-company-tabs-list li:nth-child(4)::after {
  content: "";
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 2px;
  background-color: #ea580c;
}
"""


def _expand_document_write_loops(markup: str) -> str:
    """
    Expand simple `for (...) { document.write(`...`) }` blocks to static HTML.

    Streamlit `st.html` does not reliably execute this script pattern inside the
    iframe, so we pre-render the repeated template content.
    """
    pattern = re.compile(
        r"<script>\s*"
        r"(?:\/\/[^\n]*\n\s*)*"
        r"for\s*\(\s*let\s+([a-zA-Z_]\w*)\s*=\s*0\s*;\s*\1\s*<\s*(\d+)\s*;\s*\1\+\+\s*\)\s*"
        r"\{\s*document\.write\(\s*`([\s\S]*?)`\s*\)\s*;\s*\}\s*"
        r"</script>",
        flags=re.IGNORECASE,
    )

    def _replace(match: re.Match[str]) -> str:
        repeat = int(match.group(2))
        template = match.group(3)
        return template * repeat

    return pattern.sub(_replace, markup)


def _extract_head_links(html: str) -> str:
    """Collect <link> tags from <head> (fonts, Font Awesome, etc.)."""
    head_match = re.search(
        r"<head[^>]*>(.*?)</head>",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not head_match:
        return ""
    links = re.findall(
        r'<link\b[^>]*(?:rel=["\']stylesheet["\']|rel=["\']preconnect["\'])[^>]*>',
        head_match.group(1),
        flags=re.IGNORECASE,
    )
    return "\n".join(links)


def _merge_head_links(*html_texts: str) -> str:
    """Merge CDN/font links from prototypes; always include Font Awesome."""
    seen: set[str] = set()
    ordered: list[str] = [_FONT_AWESOME_CDN]

    for text in html_texts:
        for link in _extract_head_links(text).splitlines():
            link = link.strip()
            if not link:
                continue
            # Skip broken relative stylesheet refs from prototypes (e.g. style.css).
            href_match = re.search(r"""href=["']([^"']+)["']""", link, flags=re.IGNORECASE)
            if href_match:
                href = href_match.group(1)
                if not href.startswith(("http://", "https://", "//")):
                    continue
            if link not in seen:
                seen.add(link)
                ordered.append(link)

    seen.add(_FONT_AWESOME_CDN)
    return "\n".join(ordered)


def _extract_all_styles(html: str) -> str:
    blocks = re.findall(
        r"<style[^>]*>(.*?)</style>",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return "\n".join(block.strip() for block in blocks if block.strip())


def _read_template_file(slug: str) -> str:
    path = _TEMPLATES_DIR / f"{slug}.html"
    if not path.is_file():
        raise FileNotFoundError(f"Member template not found: {path}")
    return path.read_text(encoding="utf-8")


def _extract_body_html(text: str) -> str:
    body_match = re.search(
        r"<body[^>]*>(.*?)</body>",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    body = body_match.group(1) if body_match else text
    return _expand_document_write_loops(body)


def _extract_div_with_class(html: str, class_name: str) -> str:
    """Return outer HTML of the first <div> whose class list contains class_name."""
    pattern = re.compile(
        rf'<div\s+class="[^"]*\b{re.escape(class_name)}\b[^"]*"[^>]*>',
        flags=re.IGNORECASE,
    )
    match = pattern.search(html)
    if not match:
        return ""

    start = match.start()
    depth = 1
    index = match.end()
    length = len(html)

    while index < length and depth > 0:
        next_open = html.find("<div", index)
        next_close = html.find("</div>", index)
        if next_close == -1:
            break
        if next_open != -1 and next_open < next_close:
            depth += 1
            index = next_open + 4
        else:
            depth -= 1
            index = next_close + 6
            if depth == 0:
                return html[start:index]

    return ""


def _extract_after_nav(html: str, nav_class: str) -> str:
    """Content siblings that follow a tab <nav> in a tab-specific prototype file."""
    match = re.search(
        rf'<nav[^>]*class="[^"]*\b{re.escape(nav_class)}\b[^"]*"[^>]*>.*?</nav>\s*(.*)',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return ""
    chunk = match.group(1).strip()
    # Drop the prototype file's outer container closing tag.
    return re.sub(r"</div>\s*$", "", chunk, count=1).strip()


def _extract_about_tab_content(body: str) -> str:
    match = re.search(
        r'<main\s+class="member-company-content"[^>]*>(.*?)</main>',
        body,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return match.group(1).strip() if match else ""


def _extract_company_shell(body: str) -> str:
    """Header block from member-company.html plus shared tab nav (no Streamlit tabs)."""
    match = re.search(
        r'(<div\s+class="member-company-container">\s*'
        r'<header\s+class="member-company-header">.*?</header>)',
        body,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return f'<div class="member-company-container">{_COMPANY_TAB_CONTROLS}'
    return f"{match.group(1).strip()}\n{_COMPANY_TAB_CONTROLS.strip()}"


@lru_cache(maxsize=None)
def _build_member_company_page() -> tuple[str, str, str]:
    """Assemble My Company: shell + tab panels; CSS-only show/hide (no iframe/JS)."""
    slugs = (
        "member-company",
        "member-company-contacts-tab",
        "member-company-media-tab",
        "member-company-idcard-tab",
    )
    texts = [_read_template_file(slug) for slug in slugs]
    head_links = _merge_head_links(*texts)
    css = "\n".join(
        filter(
            None,
            [_FONT_AWESOME_IMPORT]
            + [_extract_all_styles(text) for text in texts]
            + [_COMPANY_TAB_PANEL_CSS, _COMPANY_TAB_PANEL_SCOPE_CSS, MEMBER_COMPANY_LAYOUT_CSS],
        ),
    )

    bodies = [_extract_body_html(text) for text in texts]
    shell = _extract_company_shell(bodies[0])
    about_inner = _extract_about_tab_content(bodies[0])
    contacts_html = _extract_div_with_class(bodies[1], "member-company-contact-content-body")
    medias_html = _extract_after_nav(bodies[2], "member-company-media-tabs")
    idcard_html = _extract_div_with_class(bodies[3], "member-company-idcard-content-section")

    panels = f"""
    <div class="member-company-tab-panels">
      <main class="member-company-content member-company-tab-panel member-company-tab-panel--about">{about_inner}</main>
      <div class="member-company-tab-panel member-company-tab-panel--contacts">{contacts_html}</div>
      <div class="member-company-tab-panel member-company-tab-panel--medias">
        <div class="member-company-media-root">{medias_html}</div>
      </div>
      <div class="member-company-tab-panel member-company-tab-panel--idcard">
        <div class="member-company-idcard-root">{idcard_html}</div>
      </div>
    </div>
    """

    body = f"""
<div class="member-company-body">
  {shell}
  {panels}
  </div>
</div>
""".strip()

    return head_links, css, body


@lru_cache(maxsize=None)
def _load_member_template(slug: str) -> tuple[str, str, str]:
    """
    Load a member HTML prototype and return (head_links, css, body_html).

    The `slug` should match the HTML filename (without extension) under
    `.prototype/member_pages/`, e.g. `member-dashboard`, `offers`,
    `supplier-portfolio`, `member-company`.
    """
    text = _read_template_file(slug)
    head_links = _extract_head_links(text)
    css = _extract_all_styles(text)
    body = _extract_body_html(text)
    return head_links, css, body


@lru_cache(maxsize=1)
def _member_dashboard_body_parts() -> tuple[str, str]:
    """Split member dashboard prototype into HTML before/after the sales placeholder."""
    _, _, body = _load_member_template("member-dashboard")
    if _MEMBER_DASHBOARD_SALES_MARKER not in body:
        raise ValueError(
            f"Member dashboard template missing sales marker: {_MEMBER_DASHBOARD_SALES_MARKER}"
        )
    before, after = body.split(_MEMBER_DASHBOARD_SALES_MARKER, 1)
    return before.strip(), after.strip()


def _render_member_dashboard_document(body_fragment: str, *, width: str = "stretch") -> None:
    text = _read_template_file("member-dashboard")
    head_links = _merge_head_links(text)
    _, css, _ = _load_member_template("member-dashboard")
    layout_css = _MEMBER_PAGE_LAYOUT_CSS.get("member-dashboard", "")
    stylesheet = _normalize_css(f"{_FONT_AWESOME_IMPORT}\n{css}\n{layout_css}")
    document = f"{head_links}\n<style>{stylesheet}</style>\n{body_fragment.strip()}"
    st.html(document, width=width)  # type: ignore[arg-type]


def render_member_dashboard_overview(*, width: str = "stretch") -> None:
    """Overview KPI section from the member dashboard prototype."""
    before, _ = _member_dashboard_body_parts()
    fragment = f"{before.rstrip()}\n    </div>\n    </div>"
    _render_member_dashboard_document(fragment, width=width)


def render_member_dashboard_sales_header(
    title: str,
    last_updated: str,
    *,
    width: str = "stretch",
) -> None:
    """Sales section header styled like the member dashboard prototype."""
    safe_title = html.escape(title)
    safe_updated = html.escape(last_updated)
    fragment = f"""
<div class="member-dashboard">
    <div class="member-dashboard-container">
        <section>
            <div class="member-dashboard-section-header">
                <div class="member-dashboard-title-group">
                    <h2>{safe_title}</h2>
                    <span class="member-dashboard-last-updated">Last updated: {safe_updated}</span>
                </div>
            </div>
        </section>
    </div>
</div>
""".strip()
    _render_member_dashboard_document(fragment, width=width)


def render_member_dashboard_ranking(*, width: str = "stretch") -> None:
    """Ranking table section from the member dashboard prototype."""
    _, after = _member_dashboard_body_parts()
    fragment = f'<div class="member-dashboard">\n\n    <div class="member-dashboard-container">\n        {after.strip()}'
    _render_member_dashboard_document(fragment, width=width)


def render_member_template(slug: str, *, width: str = "stretch") -> None:
    """
    Render a member persona HTML prototype in a single `st.html` iframe.

    This keeps the CSS and HTML together so the Streamlit page matches the
    standalone prototype as closely as possible.
    """
    text = _read_template_file(slug)
    head_links = _merge_head_links(text)
    _, css, body = _load_member_template(slug)
    layout_css = _MEMBER_PAGE_LAYOUT_CSS.get(slug, "")
    stylesheet = _normalize_css(f"{_FONT_AWESOME_IMPORT}\n{css}\n{layout_css}")
    document = f"{head_links}\n<style>{stylesheet}</style>\n{body.strip()}"
    st.html(document, width=width)  # type: ignore[arg-type]


def render_member_company_tabs(*, width: str = "stretch") -> None:
    """
    My Company (member): shell + tab panels via st.html (styles apply correctly).

    Tabs use hidden radios + labels; CSS sibling selectors show/hide each panel
    (no JavaScript). Streamlit markdown strips ``<style>`` and would show raw CSS.
    """
    head_links, css, body = _build_member_company_page()
    stylesheet = _normalize_css(css)
    prefix = f"{head_links}\n" if head_links else ""
    document = f"{prefix}<style>{stylesheet}</style>\n{body.strip()}"
    st.html(document, width=width)  # type: ignore[arg-type]
