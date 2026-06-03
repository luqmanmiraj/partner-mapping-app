"""My Company News & Media tab — help.py pattern from company_news_media-tab.html.

CSS/HTML use ``cmpn-`` prefixed classes. Rendered via one ``st.html`` call with
``width="stretch"`` for full-width layout.
"""

from __future__ import annotations

import html
from typing import Any

import streamlit as st

_FEATURED_IMAGE = (
    "https://images.unsplash.com/photo-1619642751034-765dfdf7c58e?auto=format&fit=crop&w=600&q=80"
)
_SIDEBAR_IMG_1 = (
    "https://images.unsplash.com/photo-1486006920555-c77dce18193b?auto=format&fit=crop&w=300&q=80"
)
_SIDEBAR_IMG_2 = (
    "https://images.unsplash.com/photo-1517524206127-48bbd363f3d7?auto=format&fit=crop&w=300&q=80"
)
_VIDEO_BG = (
    "https://images.unsplash.com/photo-1486006920555-c77dce18193b?auto=format&fit=crop&w=500&q=80"
)
_GALLERY_BG = (
    "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=500&q=80"
)

_SVG_PLUS = """<svg class="cmpn-btn-icon-svg" viewBox="0 0 24 24" aria-hidden="true">
<line x1="12" y1="5" x2="12" y2="19"></line>
<line x1="5" y1="12" x2="19" y2="12"></line>
</svg>"""

_SVG_SEARCH = """<svg class="cmpn-search-icon-svg" viewBox="0 0 24 24" aria-hidden="true">
<circle cx="11" cy="11" r="7"></circle>
<line x1="21" y1="21" x2="16.65" y2="16.65"></line>
</svg>"""

_SVG_COPY = """<svg class="cmpn-doc-icon-svg" viewBox="0 0 24 24" aria-hidden="true">
<rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
<path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
</svg>"""

_SVG_ELLIPSIS = """<svg class="cmpn-action-icon-svg" viewBox="0 0 24 24" aria-hidden="true">
<circle cx="5" cy="12" r="1.5" fill="currentColor" stroke="none"></circle>
<circle cx="12" cy="12" r="1.5" fill="currentColor" stroke="none"></circle>
<circle cx="19" cy="12" r="1.5" fill="currentColor" stroke="none"></circle>
</svg>"""

_SVG_EYE = """<svg class="cmpn-action-icon-svg" viewBox="0 0 24 24" aria-hidden="true">
<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
<circle cx="12" cy="12" r="3"></circle>
</svg>"""

_SVG_DOWNLOAD = """<svg class="cmpn-action-icon-svg" viewBox="0 0 24 24" aria-hidden="true">
<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
<polyline points="7 10 12 15 17 10"></polyline>
<line x1="12" y1="15" x2="12" y2="3"></line>
</svg>"""

_SVG_PLAY = """<svg class="cmpn-play-icon-svg" viewBox="0 0 24 24" aria-hidden="true">
<circle cx="12" cy="12" r="10"></circle>
<polygon points="10 8 16 12 10 16 10 8" fill="#f39c12" stroke="none"></polygon>
</svg>"""

_SVG_ELLIPSIS_LIGHT = """<svg class="cmpn-top-options-svg" viewBox="0 0 24 24" aria-hidden="true">
<circle cx="5" cy="12" r="1.5" fill="#ffffff" stroke="none"></circle>
<circle cx="12" cy="12" r="1.5" fill="#ffffff" stroke="none"></circle>
<circle cx="19" cy="12" r="1.5" fill="#ffffff" stroke="none"></circle>
</svg>"""


def _page_css() -> str:
    return f"""
<style>
.cmpn-page-wrapper * {{
margin: 0;
padding: 0;
box-sizing: border-box;
}}

.cmpn-page-wrapper {{
font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
color: #111111;
width: 100%;
}}

.cmpn-dashboard-container {{
width: 100%;
margin: 0;
background-color: #ffffff;
border-radius: 8px;
padding: 30px;
box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
display: flex;
flex-direction: column;
gap: 32px;
}}

.cmpn-control-bar {{
display: flex;
gap: 12px;
align-items: center;
flex-wrap: wrap;
}}

.cmpn-add-media-btn {{
background-color: #0b0f19;
color: #ffffff;
border: none;
border-radius: 4px;
padding: 10px 16px;
font-size: 0.88rem;
font-weight: 600;
cursor: pointer;
display: inline-flex;
align-items: center;
gap: 8px;
font-family: inherit;
}}

.cmpn-btn-icon-svg {{
width: 14px;
height: 14px;
fill: none;
stroke: #ffffff;
stroke-width: 2;
stroke-linecap: round;
stroke-linejoin: round;
flex-shrink: 0;
}}

.cmpn-filter-dropdown {{
padding: 10px 30px 10px 12px;
font-size: 0.88rem;
border: 1.5px solid #cbd5e0;
border-radius: 4px;
background-color: #ffffff;
color: #4a5568;
cursor: pointer;
outline: none;
appearance: none;
font-family: inherit;
background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='10' height='6' viewBox='0 0 10 6'><path fill='%234a5568' d='M0 0l5 5 5-5z'/></svg>");
background-repeat: no-repeat;
background-position: right 12px center;
min-width: 140px;
}}

.cmpn-search-wrapper {{
position: relative;
flex: 1;
min-width: 240px;
}}

.cmpn-search-input {{
width: 100%;
padding: 10px 40px 10px 16px;
font-size: 0.88rem;
border: 1.5px solid #cbd5e0;
border-radius: 4px;
color: #2d3748;
outline: none;
font-family: inherit;
}}

.cmpn-search-icon-svg {{
position: absolute;
right: 14px;
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
}}

.cmpn-section-header-row {{
display: flex;
justify-content: space-between;
align-items: flex-end;
margin-bottom: 16px;
}}

.cmpn-section-header-row h2 {{
font-size: 1.35rem;
font-weight: 700;
color: #111111;
}}

.cmpn-view-all-link {{
font-size: 0.88rem;
font-weight: 700;
color: #111111;
text-decoration: underline;
cursor: pointer;
}}

.cmpn-carousel-indicators {{
display: flex;
justify-content: center;
gap: 6px;
margin-top: 16px;
}}

.cmpn-dot {{
width: 8px;
height: 8px;
border-radius: 50%;
background-color: #cbd5e0;
display: inline-block;
}}

.cmpn-dot.active {{
background-color: #f39c12;
width: 24px;
border-radius: 4px;
}}

.cmpn-news-layout-grid {{
display: grid;
grid-template-columns: 1.1fr 1fr;
gap: 20px;
}}

.cmpn-news-featured-card {{
border: 1.5px solid #e2e8f0;
border-radius: 6px;
overflow: hidden;
display: flex;
flex-direction: column;
background-color: #ffffff;
}}

.cmpn-featured-image {{
height: 220px;
background: #2d3748 url('{_FEATURED_IMAGE}') center/cover no-repeat;
}}

.cmpn-news-card-body {{
padding: 16px;
display: flex;
flex-direction: column;
gap: 8px;
}}

.cmpn-news-date {{
font-size: 0.78rem;
color: #718096;
font-weight: 600;
}}

.cmpn-news-card-body h3 {{
font-size: 1.05rem;
font-weight: 700;
color: #111111;
}}

.cmpn-news-card-body p {{
font-size: 0.88rem;
color: #4a5568;
line-height: 1.5;
}}

.cmpn-news-read-more {{
font-size: 0.85rem;
font-weight: 700;
color: #111111;
text-decoration: underline;
margin-top: 4px;
cursor: pointer;
}}

.cmpn-news-sidebar-stack {{
display: flex;
flex-direction: column;
gap: 16px;
}}

.cmpn-news-row-card {{
border: 1.5px solid #e2e8f0;
border-radius: 6px;
overflow: hidden;
display: grid;
grid-template-columns: 160px 1fr;
background-color: #ffffff;
height: calc(50% - 8px);
}}

.cmpn-sidebar-img-1 {{
background: #2d3748 url('{_SIDEBAR_IMG_1}') center/cover no-repeat;
}}

.cmpn-sidebar-img-2 {{
background: #2d3748 url('{_SIDEBAR_IMG_2}') center/cover no-repeat;
}}

.cmpn-docs-list-stack {{
display: flex;
flex-direction: column;
gap: 12px;
}}

.cmpn-doc-row-item {{
background-color: #ffffff;
border: 1.5px solid #e2e8f0;
border-radius: 6px;
padding: 14px 20px;
display: flex;
align-items: center;
gap: 16px;
}}

.cmpn-doc-icon-box {{
background-color: #fffdf9;
border: 1.5px solid #fdeed6;
border-radius: 6px;
width: 40px;
height: 40px;
display: flex;
align-items: center;
justify-content: center;
flex-shrink: 0;
}}

.cmpn-doc-icon-svg {{
width: 20px;
height: 20px;
fill: none;
stroke: #f39c12;
stroke-width: 2;
stroke-linecap: round;
stroke-linejoin: round;
}}

.cmpn-doc-info-wrapper {{
flex: 1;
display: flex;
flex-direction: column;
min-width: 0;
}}

.cmpn-doc-info-wrapper h4 {{
font-size: 0.95rem;
font-weight: 700;
color: #111111;
}}

.cmpn-doc-info-wrapper span {{
font-size: 0.8rem;
color: #718096;
margin-top: 2px;
}}

.cmpn-doc-actions-wrapper {{
display: flex;
align-items: center;
gap: 16px;
}}

.cmpn-action-icon-svg {{
width: 18px;
height: 18px;
fill: none;
stroke: #718096;
stroke-width: 2;
stroke-linecap: round;
stroke-linejoin: round;
cursor: pointer;
}}

.cmpn-doc-actions-wrapper .cmpn-action-icon-svg:hover {{
stroke: #111111;
}}

.cmpn-media-triple-grid {{
display: grid;
grid-template-columns: repeat(3, 1fr);
gap: 20px;
}}

.cmpn-video-card-element {{
position: relative;
border-radius: 6px;
overflow: hidden;
height: 250px;
background: #111111 url('{_VIDEO_BG}') center/cover no-repeat;
display: flex;
align-items: flex-end;
}}

.cmpn-gallery-card-element {{
position: relative;
border-radius: 6px;
overflow: hidden;
height: 250px;
background: #111111 url('{_GALLERY_BG}') center/cover no-repeat;
display: flex;
align-items: flex-end;
}}

.cmpn-video-card-overlay {{
position: absolute;
inset: 0;
background: linear-gradient(to bottom, rgba(0,0,0,0.1) 40%, rgba(0,0,0,0.85) 100%);
z-index: 1;
}}

.cmpn-video-play-badge {{
position: absolute;
top: 50%;
left: 50%;
transform: translate(-50%, -50%);
z-index: 3;
opacity: 0.9;
cursor: pointer;
}}

.cmpn-play-icon-svg {{
width: 48px;
height: 48px;
fill: none;
stroke: #f39c12;
stroke-width: 1.5;
}}

.cmpn-video-card-content {{
position: relative;
z-index: 2;
padding: 16px;
color: #ffffff;
display: flex;
flex-direction: column;
gap: 4px;
width: 100%;
}}

.cmpn-video-card-content h4 {{
font-size: 0.95rem;
font-weight: 700;
}}

.cmpn-video-card-content p {{
font-size: 0.82rem;
color: #cbd5e0;
white-space: nowrap;
overflow: hidden;
text-overflow: ellipsis;
}}

.cmpn-top-right-options {{
position: absolute;
top: 14px;
right: 14px;
z-index: 3;
opacity: 0.8;
cursor: pointer;
display: flex;
}}

.cmpn-top-options-svg {{
width: 18px;
height: 18px;
}}

@media (max-width: 900px) {{
.cmpn-news-layout-grid {{
grid-template-columns: 1fr;
}}
.cmpn-news-row-card {{
height: auto;
grid-template-columns: 140px 1fr;
}}
.cmpn-media-triple-grid {{
grid-template-columns: 1fr 1fr;
}}
}}

@media (max-width: 600px) {{
.cmpn-control-bar {{
flex-direction: column;
align-items: stretch;
}}
.cmpn-search-wrapper {{
order: -1;
}}
.cmpn-media-triple-grid {{
grid-template-columns: 1fr;
}}
.cmpn-news-row-card {{
grid-template-columns: 1fr;
}}
.cmpn-news-row-card > div:first-child {{
height: 140px;
}}
}}
</style>
"""


def _carousel_dots() -> str:
    dots = '<span class="cmpn-dot active"></span>' + "".join(
        '<span class="cmpn-dot"></span>' for _ in range(4)
    )
    return f'<div class="cmpn-carousel-indicators">{dots}</div>'


def _news_body(date: str, title: str, summary: str) -> str:
    return f"""<div class="cmpn-news-card-body">
<span class="cmpn-news-date">{html.escape(date)}</span>
<h3>{html.escape(title)}</h3>
<p>{html.escape(summary)}</p>
<span class="cmpn-news-read-more">Read</span>
</div>"""


def _sidebar_image_class(image_key: str) -> str:
    return {"sidebar-1": "cmpn-sidebar-img-1", "sidebar-2": "cmpn-sidebar-img-2"}.get(
        image_key, "cmpn-sidebar-img-1"
    )


def _sidebar_card(item: dict[str, str]) -> str:
    img_class = html.escape(_sidebar_image_class(item.get("image", "sidebar-1")))
    return f"""<article class="cmpn-news-row-card">
<div class="{img_class}"></div>
{_news_body(item["date"], item["title"], item["summary"])}
</article>"""


def _doc_row(doc: dict[str, str]) -> str:
    return f"""<div class="cmpn-doc-row-item">
<div class="cmpn-doc-icon-box">{_SVG_COPY}</div>
<div class="cmpn-doc-info-wrapper">
<h4>{html.escape(doc["name"])}</h4>
<span>{html.escape(doc["size"])}</span>
</div>
<div class="cmpn-doc-actions-wrapper">
{_SVG_ELLIPSIS}
{_SVG_EYE}
{_SVG_DOWNLOAD}
</div>
</div>"""


def _video_card(item: dict[str, str]) -> str:
    return f"""<div class="cmpn-video-card-element">
<div class="cmpn-video-card-overlay"></div>
<span class="cmpn-top-right-options">{_SVG_ELLIPSIS_LIGHT}</span>
<span class="cmpn-video-play-badge">{_SVG_PLAY}</span>
<div class="cmpn-video-card-content">
<h4>{html.escape(item["title"])}</h4>
<p>{html.escape(item["summary"])}</p>
</div>
</div>"""


def _gallery_card(item: dict[str, str]) -> str:
    return f"""<div class="cmpn-gallery-card-element">
<div class="cmpn-video-card-overlay"></div>
<span class="cmpn-top-right-options">{_SVG_ELLIPSIS_LIGHT}</span>
<div class="cmpn-video-card-content">
<h4>{html.escape(item["title"])}</h4>
<p>{html.escape(item["summary"])}</p>
</div>
</div>"""


def _page_html(data: dict[str, Any]) -> str:
    featured = data.get("featured", {})
    sidebar = data.get("sidebar", [])
    documents = data.get("documents", [])
    videos = data.get("videos", [])
    gallery = data.get("gallery", [])

    sidebar_html = "\n".join(_sidebar_card(item) for item in sidebar)
    docs_html = "\n".join(_doc_row(doc) for doc in documents)
    videos_html = "\n".join(_video_card(item) for item in videos)
    gallery_html = "\n".join(_gallery_card(item) for item in gallery)

    return f"""<div class="cmpn-page-wrapper">
<div class="cmpn-dashboard-container">
<div class="cmpn-control-bar">
<button type="button" class="cmpn-add-media-btn">{_SVG_PLUS} Add Media</button>
<select class="cmpn-filter-dropdown" disabled><option>Country</option></select>
<select class="cmpn-filter-dropdown" disabled><option>Product</option></select>
<div class="cmpn-search-wrapper">
<input type="text" class="cmpn-search-input" placeholder="Search for a topic..." readonly>
{_SVG_SEARCH}
</div>
</div>
<section>
<div class="cmpn-section-header-row">
<h2>News</h2>
<span class="cmpn-view-all-link">View all</span>
</div>
<div class="cmpn-news-layout-grid">
<article class="cmpn-news-featured-card">
<div class="cmpn-featured-image"></div>
{_news_body(featured.get("date", ""), featured.get("title", ""), featured.get("summary", ""))}
</article>
<div class="cmpn-news-sidebar-stack">
{sidebar_html}
</div>
</div>
{_carousel_dots()}
</section>
<section>
<div class="cmpn-section-header-row">
<h2>Documents &amp; Catalogues</h2>
<span class="cmpn-view-all-link">View all</span>
</div>
<div class="cmpn-docs-list-stack">
{docs_html}
</div>
{_carousel_dots()}
</section>
<section>
<div class="cmpn-section-header-row">
<h2>Videos</h2>
<span class="cmpn-view-all-link">View all</span>
</div>
<div class="cmpn-media-triple-grid">
{videos_html}
</div>
{_carousel_dots()}
</section>
<section>
<div class="cmpn-section-header-row">
<h2>Gallery</h2>
<span class="cmpn-view-all-link">View all</span>
</div>
<div class="cmpn-media-triple-grid">
{gallery_html}
</div>
{_carousel_dots()}
</section>
</div>
</div>"""


def render_company_news_media_tab(data: dict[str, Any]) -> None:
    st.html(f"{_page_css()}{_page_html(data)}", width="stretch")  # type: ignore[arg-type]
