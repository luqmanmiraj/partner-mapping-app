"""My Company News & Media tab — prototype CSS from company_news_media-tab.html."""

from __future__ import annotations

import html
from typing import Any

from theme.company_templates import render_company_tab_document


def _carousel_dots() -> str:
    dots = '<span class="dot active"></span>' + "".join(
        '<span class="dot"></span>' for _ in range(4)
    )
    return f'<div class="carousel-indicators">{dots}</div>'


def _news_body(date: str, title: str, summary: str) -> str:
    return f"""<div class="news-card-body">
<span class="news-date">{html.escape(date)}</span>
<h3>{html.escape(title)}</h3>
<p>{html.escape(summary)}</p>
<span class="news-read-more">Read</span>
</div>"""


def _sidebar_image_class(image_key: str) -> str:
    return {"sidebar-1": "sidebar-img-1", "sidebar-2": "sidebar-img-2"}.get(
        image_key, "sidebar-img-1"
    )


def _sidebar_card(item: dict[str, str]) -> str:
    img_class = html.escape(_sidebar_image_class(item.get("image", "sidebar-1")))
    return f"""<article class="news-row-card">
<div class="{img_class}"></div>
{_news_body(item["date"], item["title"], item["summary"])}
</article>"""


def _doc_row(doc: dict[str, str]) -> str:
    return f"""<div class="doc-row-item">
<div class="doc-icon-box"><i class="fa-regular fa-copy"></i></div>
<div class="doc-info-wrapper">
<h4>{html.escape(doc["name"])}</h4>
<span>{html.escape(doc["size"])}</span>
</div>
<div class="doc-actions-wrapper">
<i class="fa-solid fa-ellipsis"></i>
<i class="fa-regular fa-eye"></i>
<i class="fa-solid fa-download"></i>
</div>
</div>"""


def _video_card(item: dict[str, str]) -> str:
    return f"""<div class="video-card-element">
<div class="video-card-overlay"></div>
<span class="top-right-options"><i class="fa-solid fa-ellipsis"></i></span>
<span class="video-play-badge"><i class="fa-regular fa-circle-play"></i></span>
<div class="video-card-content">
<h4>{html.escape(item["title"])}</h4>
<p>{html.escape(item["summary"])}</p>
</div>
</div>"""


def _gallery_card(item: dict[str, str]) -> str:
    return f"""<div class="gallery-card-element">
<div class="video-card-overlay"></div>
<span class="top-right-options"><i class="fa-solid fa-ellipsis"></i></span>
<div class="video-card-content">
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

    return f"""<div class="dashboard-container">
<div class="control-bar">
<button type="button" class="add-media-btn"><i class="fa-solid fa-plus"></i> Add Media</button>
<select class="filter-dropdown" disabled><option>Country</option></select>
<select class="filter-dropdown" disabled><option>Product</option></select>
<div class="search-wrapper">
<input type="text" placeholder="Search for a topic..." readonly>
<i class="fa-solid fa-magnifying-glass search-icon"></i>
</div>
</div>
<section>
<div class="section-header-row">
<h2>News</h2>
<a href="#" class="view-all-link">View all</a>
</div>
<div class="news-layout-grid">
<article class="news-featured-card">
<div class="featured-image"></div>
{_news_body(featured.get("date", ""), featured.get("title", ""), featured.get("summary", ""))}
</article>
<div class="news-sidebar-stack">
{sidebar_html}
</div>
</div>
{_carousel_dots()}
</section>
<section>
<div class="section-header-row">
<h2>Documents &amp; Catalogues</h2>
<a href="#" class="view-all-link">View all</a>
</div>
<div class="docs-list-stack">
{docs_html}
</div>
{_carousel_dots()}
</section>
<section>
<div class="section-header-row">
<h2>Videos</h2>
<a href="#" class="view-all-link">View all</a>
</div>
<div class="media-triple-grid">
{videos_html}
</div>
{_carousel_dots()}
</section>
<section>
<div class="section-header-row">
<h2>Gallery</h2>
<a href="#" class="view-all-link">View all</a>
</div>
<div class="media-triple-grid">
{gallery_html}
</div>
{_carousel_dots()}
</section>
</div>"""


def render_company_news_media_tab(data: dict[str, Any]) -> None:
    render_company_tab_document("company_news_media-tab", _page_html(data))
