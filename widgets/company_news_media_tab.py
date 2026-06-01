"""My Company News & Media tab — matches .prototype/company/company_news_media-tab.html."""

from __future__ import annotations

import html
from typing import Any

from theme.html_utils import render_html

_ROOT = "nexus-company-news"

_FEATURED_IMAGE = (
    "https://images.unsplash.com/photo-1619642751034-765dfdf7c58e?auto=format&fit=crop&w=600&q=80"
)
_SIDEBAR_IMAGES = {
    "sidebar-1": "https://images.unsplash.com/photo-1486006920555-c77dce18193b?auto=format&fit=crop&w=300&q=80",
    "sidebar-2": "https://images.unsplash.com/photo-1517524206127-48bbd363f3d7?auto=format&fit=crop&w=300&q=80",
}
_VIDEO_BG = (
    "https://images.unsplash.com/photo-1486006920555-c77dce18193b?auto=format&fit=crop&w=500&q=80"
)
_GALLERY_BG = (
    "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=500&q=80"
)

_ICON_PLUS = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23ffffff' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M12 5v14m7-7H5'/%3e%3c/svg%3e"
)
_ICON_SEARCH = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%234a5568' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z'/%3e%3c/svg%3e"
)
_ICON_DOC = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23f39c12' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z'/%3e%3c/svg%3e"
)
_ICON_DOTS = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='%23718096' "
    "viewBox='0 0 24 24'%3e%3ccircle cx='5' cy='12' r='2'/%3e%3ccircle cx='12' cy='12' r='2'/%3e%3ccircle cx='19' cy='12' r='2'/%3e%3c/svg%3e"
)
_ICON_EYE = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23718096' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M15 12a3 3 0 11-6 0 3 3 0 016 0z'/%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z'/%3e%3c/svg%3e"
)
_ICON_DOWNLOAD = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23718096' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4'/%3e%3c/svg%3e"
)
_ICON_PLAY = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23f39c12' stroke-width='1.5' viewBox='0 0 24 24'%3e%3ccircle cx='12' cy='12' r='10'/%3e%3cpath "
    "fill='%23f39c12' stroke='none' d='M10 8l6 4-6 4z'/%3e%3c/svg%3e"
)


def company_news_media_tab_styles() -> str:
    return f"""
        .nexus-company-news {{
            width: 100%;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #111111;
        }}

        .nexus-company-news .dashboard-container {{
            width: 100%;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
            display: flex;
            flex-direction: column;
            gap: 32px;
            box-sizing: border-box;
        }}

        .nexus-company-news .control-bar {{
            display: flex;
            gap: 12px;
            align-items: center;
            flex-wrap: wrap;
        }}

        .nexus-company-news .add-media-btn {{
            background-color: #0b0f19;
            color: #ffffff;
            border: none;
            border-radius: 4px;
            padding: 10px 16px;
            font-size: 0.88rem;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            cursor: pointer;
            transition: background-color 0.15s ease;
        }}

        .nexus-company-news .add-media-btn:hover {{
            background-color: #1a2336;
        }}

        .nexus-company-news .add-media-btn::before {{
            content: "";
            width: 14px;
            height: 14px;
            background: url("{_ICON_PLUS}") center / contain no-repeat;
        }}

        .nexus-company-news .filter-dropdown {{
            padding: 10px 30px 10px 12px;
            font-size: 0.88rem;
            border: 1.5px solid #cbd5e0;
            border-radius: 4px;
            background-color: #ffffff;
            color: #4a5568;
            appearance: none;
            background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='10' height='6' viewBox='0 0 10 6'><path fill='%234a5568' d='M0 0l5 5 5-5z'/></svg>");
            background-repeat: no-repeat;
            background-position: right 12px center;
            min-width: 140px;
            outline: none;
            cursor: pointer;
        }}

        .nexus-company-news .search-wrapper {{
            position: relative;
            flex: 1;
            min-width: 240px;
        }}

        .nexus-company-news .search-wrapper input {{
            width: 100%;
            padding: 10px 40px 10px 16px;
            font-size: 0.88rem;
            border: 1.5px solid #cbd5e0;
            border-radius: 4px;
            color: #2d3748;
            outline: none;
            box-sizing: border-box;
        }}

        .nexus-company-news .search-wrapper::after {{
            content: "";
            position: absolute;
            right: 14px;
            top: 50%;
            transform: translateY(-50%);
            width: 16px;
            height: 16px;
            background: url("{_ICON_SEARCH}") center / contain no-repeat;
            pointer-events: none;
            z-index: 5;
        }}

        .nexus-company-news .section-header-row {{
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            margin-bottom: 16px;
        }}

        .nexus-company-news .section-header-row h2 {{
            font-size: 1.35rem;
            font-weight: 700;
            color: #111111;
            margin: 0;
        }}

        .nexus-company-news .view-all-link {{
            font-size: 0.88rem;
            font-weight: 700;
            color: #111111;
            text-decoration: underline;
            cursor: pointer;
        }}

        .nexus-company-news .carousel-indicators {{
            display: flex;
            justify-content: center;
            gap: 6px;
            margin-top: 16px;
        }}

        .nexus-company-news .dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: #cbd5e0;
            display: inline-block;
        }}

        .nexus-company-news .dot.active {{
            background-color: #f39c12;
            width: 24px;
            border-radius: 4px;
        }}

        .nexus-company-news .news-layout-grid {{
            display: grid;
            grid-template-columns: 1.1fr 1fr;
            gap: 20px;
        }}

        .nexus-company-news .news-featured-card {{
            border: 1.5px solid #e2e8f0;
            border-radius: 6px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            background-color: #ffffff;
        }}

        .nexus-company-news .featured-image {{
            height: 220px;
            background: #2d3748 url("{_FEATURED_IMAGE}") center/cover no-repeat;
        }}

        .nexus-company-news .news-card-body {{
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            box-sizing: border-box;
        }}

        .nexus-company-news .news-date {{
            font-size: 0.78rem;
            color: #718096;
            font-weight: 600;
        }}

        .nexus-company-news .news-card-body h3,
        .nexus-company-news .news-card-body h4 {{
            font-size: 1.05rem;
            font-weight: 700;
            color: #111111;
            margin: 0;
        }}

        .nexus-company-news .news-card-body p {{
            font-size: 0.88rem;
            color: #4a5568;
            line-height: 1.5;
            margin: 0;
        }}

        .nexus-company-news .news-read-more {{
            font-size: 0.85rem;
            font-weight: 700;
            color: #111111;
            text-decoration: underline;
            margin-top: 4px;
            cursor: pointer;
        }}

        .nexus-company-news .news-sidebar-stack {{
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}

        .nexus-company-news .news-row-card {{
            border: 1.5px solid #e2e8f0;
            border-radius: 6px;
            overflow: hidden;
            display: grid;
            grid-template-columns: 160px 1fr;
            background-color: #ffffff;
            flex: 1;
            min-height: 0;
        }}

        .nexus-company-news .news-row-card .row-thumb {{
            background: #2d3748 center/cover no-repeat;
            min-height: 100%;
        }}

        .nexus-company-news .docs-list-stack {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}

        .nexus-company-news .doc-row-item {{
            background-color: #ffffff;
            border: 1.5px solid #e2e8f0;
            border-radius: 6px;
            padding: 14px 20px;
            display: flex;
            align-items: center;
            gap: 16px;
            box-sizing: border-box;
        }}

        .nexus-company-news .doc-icon-box {{
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

        .nexus-company-news .doc-icon-box::before {{
            content: "";
            width: 20px;
            height: 20px;
            background: url("{_ICON_DOC}") center / contain no-repeat;
        }}

        .nexus-company-news .doc-info-wrapper {{
            flex: 1;
            display: flex;
            flex-direction: column;
            min-width: 0;
        }}

        .nexus-company-news .doc-info-wrapper h4 {{
            font-size: 0.95rem;
            font-weight: 700;
            color: #111111;
            margin: 0;
        }}

        .nexus-company-news .doc-info-wrapper span {{
            font-size: 0.8rem;
            color: #718096;
            margin-top: 2px;
        }}

        .nexus-company-news .doc-actions-wrapper {{
            display: flex;
            align-items: center;
            gap: 16px;
            flex-shrink: 0;
        }}

        .nexus-company-news .doc-actions-wrapper .action-icon {{
            width: 18px;
            height: 18px;
            background: center / contain no-repeat;
            cursor: pointer;
        }}

        .nexus-company-news .doc-actions-wrapper .action-icon--dots {{ background-image: url("{_ICON_DOTS}"); }}
        .nexus-company-news .doc-actions-wrapper .action-icon--eye {{ background-image: url("{_ICON_EYE}"); }}
        .nexus-company-news .doc-actions-wrapper .action-icon--download {{ background-image: url("{_ICON_DOWNLOAD}"); }}

        .nexus-company-news .media-triple-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
        }}

        .nexus-company-news .video-card-element,
        .nexus-company-news .gallery-card-element {{
            position: relative;
            border-radius: 6px;
            overflow: hidden;
            height: 250px;
            display: flex;
            align-items: flex-end;
            background: #111111 center/cover no-repeat;
        }}

        .nexus-company-news .video-card-element {{
            background-image: url("{_VIDEO_BG}");
        }}

        .nexus-company-news .gallery-card-element {{
            background-image: url("{_GALLERY_BG}");
        }}

        .nexus-company-news .video-card-overlay {{
            position: absolute;
            inset: 0;
            background: linear-gradient(to bottom, rgba(0,0,0,0.1) 40%, rgba(0,0,0,0.85) 100%);
            z-index: 1;
        }}

        .nexus-company-news .video-play-badge {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 48px;
            height: 48px;
            background: url("{_ICON_PLAY}") center / contain no-repeat;
            z-index: 3;
            opacity: 0.9;
            cursor: pointer;
        }}

        .nexus-company-news .video-card-content {{
            position: relative;
            z-index: 2;
            padding: 16px;
            color: #ffffff;
            display: flex;
            flex-direction: column;
            gap: 4px;
            width: 100%;
            box-sizing: border-box;
        }}

        .nexus-company-news .video-card-content h4 {{
            font-size: 0.95rem;
            font-weight: 700;
            margin: 0;
        }}

        .nexus-company-news .video-card-content p {{
            font-size: 0.82rem;
            color: #cbd5e0;
            margin: 0;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .nexus-company-news .top-right-options {{
            position: absolute;
            top: 14px;
            right: 14px;
            width: 18px;
            height: 18px;
            background: url("{_ICON_DOTS}") center / contain no-repeat;
            z-index: 3;
            opacity: 0.8;
            filter: brightness(0) invert(1);
            cursor: pointer;
        }}

        @media (max-width: 900px) {{
            .nexus-company-news .news-layout-grid {{
                grid-template-columns: 1fr;
            }}
            .nexus-company-news .news-row-card {{
                grid-template-columns: 140px 1fr;
            }}
            .nexus-company-news .media-triple-grid {{
                grid-template-columns: 1fr 1fr;
            }}
        }}

        @media (max-width: 600px) {{
            .nexus-company-news .control-bar {{
                flex-direction: column;
                align-items: stretch;
            }}
            .nexus-company-news .search-wrapper {{
                order: -1;
            }}
            .nexus-company-news .media-triple-grid {{
                grid-template-columns: 1fr;
            }}
            .nexus-company-news .news-row-card {{
                grid-template-columns: 1fr;
            }}
            .nexus-company-news .news-row-card .row-thumb {{
                height: 140px;
            }}
        }}
    """


def inject_company_news_media_tab_styles() -> None:
    render_html(f"<style>{company_news_media_tab_styles()}</style>")


def _carousel_dots() -> str:
    dots = ['<span class="dot active"></span>']
    dots.extend('<span class="dot"></span>' for _ in range(4))
    return f'<div class="carousel-indicators">{"".join(dots)}</div>'


def _news_body(date: str, title: str, summary: str, heading: str = "h3") -> str:
    return f"""
      <div class="news-card-body">
        <span class="news-date">{html.escape(date)}</span>
        <{heading}>{html.escape(title)}</{heading}>
        <p>{html.escape(summary)}</p>
        <span class="news-read-more">Read</span>
      </div>
    """


def _sidebar_card(item: dict[str, str]) -> str:
    img_key = item.get("image", "sidebar-1")
    img_url = html.escape(_SIDEBAR_IMAGES.get(img_key, _SIDEBAR_IMAGES["sidebar-1"]))
    return f"""
      <article class="news-row-card">
        <div class="row-thumb" style="background-image:url('{img_url}');"></div>
        {_news_body(item["date"], item["title"], item["summary"], "h3")}
      </article>
    """


def _doc_row(doc: dict[str, str]) -> str:
    return f"""
      <div class="doc-row-item">
        <div class="doc-icon-box"></div>
        <div class="doc-info-wrapper">
          <h4>{html.escape(doc["name"])}</h4>
          <span>{html.escape(doc["size"])}</span>
        </div>
        <div class="doc-actions-wrapper">
          <span class="action-icon action-icon--dots" aria-hidden="true"></span>
          <span class="action-icon action-icon--eye" aria-hidden="true"></span>
          <span class="action-icon action-icon--download" aria-hidden="true"></span>
        </div>
      </div>
    """


def _video_card(item: dict[str, str]) -> str:
    return f"""
      <div class="video-card-element">
        <div class="video-card-overlay"></div>
        <span class="top-right-options" aria-hidden="true"></span>
        <span class="video-play-badge" aria-hidden="true"></span>
        <div class="video-card-content">
          <h4>{html.escape(item["title"])}</h4>
          <p>{html.escape(item["summary"])}</p>
        </div>
      </div>
    """


def _gallery_card(item: dict[str, str]) -> str:
    return f"""
      <div class="gallery-card-element">
        <div class="video-card-overlay"></div>
        <span class="top-right-options" aria-hidden="true"></span>
        <div class="video-card-content">
          <h4>{html.escape(item["title"])}</h4>
          <p>{html.escape(item["summary"])}</p>
        </div>
      </div>
    """


def build_company_news_media_tab_html(data: dict[str, Any]) -> str:
    featured = data.get("featured", {})
    sidebar = data.get("sidebar", [])
    documents = data.get("documents", [])
    videos = data.get("videos", [])
    gallery = data.get("gallery", [])

    sidebar_html = "".join(_sidebar_card(item) for item in sidebar)
    docs_html = "".join(_doc_row(doc) for doc in documents)
    videos_html = "".join(_video_card(item) for item in videos)
    gallery_html = "".join(_gallery_card(item) for item in gallery)

    return f"""
    <div class="nexus-company-news">
      <div class="dashboard-container">
        <div class="control-bar">
          <button class="add-media-btn">Add Media</button>
          <select class="filter-dropdown" disabled><option>Country</option></select>
          <select class="filter-dropdown" disabled><option>Product</option></select>
          <div class="search-wrapper">
            <input type="text" placeholder="Search for a topic..." readonly>
          </div>
        </div>

        <section>
          <div class="section-header-row">
            <h2>News</h2>
            <span class="view-all-link">View all</span>
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
            <span class="view-all-link">View all</span>
          </div>
          <div class="docs-list-stack">
            {docs_html}
          </div>
          {_carousel_dots()}
        </section>

        <section>
          <div class="section-header-row">
            <h2>Videos</h2>
            <span class="view-all-link">View all</span>
          </div>
          <div class="media-triple-grid">
            {videos_html}
          </div>
          {_carousel_dots()}
        </section>

        <section>
          <div class="section-header-row">
            <h2>Gallery</h2>
            <span class="view-all-link">View all</span>
          </div>
          <div class="media-triple-grid">
            {gallery_html}
          </div>
          {_carousel_dots()}
        </section>
      </div>
    </div>
    """


def render_company_news_media_tab(data: dict[str, Any]) -> None:
    inject_company_news_media_tab_styles()
    render_html(build_company_news_media_tab_html(data), width="stretch")
