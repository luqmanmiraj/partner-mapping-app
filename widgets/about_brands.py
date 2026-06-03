"""Brand downloads section — matches .prototype/company/brands.html."""

from __future__ import annotations

import html

from theme.html_utils import render_html

_PREFIX = "nexus-about-brands"

_ICON_FILE = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23f39c12' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z'/%3e%3c/svg%3e"
)
_ICON_EYE = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23555555' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M15 12a3 3 0 11-6 0 3 3 0 016 0z'/%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z'/%3e%3c/svg%3e"
)
_ICON_DOWNLOAD = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23555555' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4'/%3e%3cpolyline points='7 10 12 15 17 10'/%3e%3cline "
    "x1='12' y1='15' x2='12' y2='3'/%3e%3c/svg%3e"
)
_ICON_DOWNLOAD_BTN = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23ffffff' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4'/%3e%3cpolyline points='7 10 12 15 17 10'/%3e%3cline "
    "x1='12' y1='15' x2='12' y2='3'/%3e%3c/svg%3e"
)


def about_brands_styles() -> str:
    p = _PREFIX
    return f"""
        .{p} {{
            width: 100%;
            max-width: 1140px;
            margin: 0 auto 1.5rem;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}

        .{p}__header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            flex-wrap: wrap;
            gap: 15px;
        }}

        .{p}__title {{
            font-size: 1.9rem;
            font-weight: 800;
            letter-spacing: -0.5px;
            color: #111111;
            margin: 0;
        }}

        .{p}__download-all {{
            background-color: #111111;
            color: #ffffff;
            border: none;
            border-radius: 4px;
            padding: 10px 18px;
            font-size: 0.95rem;
            font-weight: 700;
            cursor: default;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }}

        .{p}__download-all-icon {{
            width: 16px;
            height: 16px;
            background: center / contain no-repeat url("{_ICON_DOWNLOAD_BTN}");
        }}

        .{p}__grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
        }}

        .{p}__file-card {{
            background-color: #ffffff;
            border-radius: 6px;
            padding: 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.01);
            box-sizing: border-box;
        }}

        .{p}__file-info {{
            display: flex;
            align-items: center;
            gap: 14px;
            overflow: hidden;
            min-width: 0;
        }}

        .{p}__file-icon {{
            background-color: #fcf6ec;
            border-radius: 6px;
            width: 44px;
            height: 44px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }}

        .{p}__file-icon span {{
            width: 20px;
            height: 20px;
            background: center / contain no-repeat url("{_ICON_FILE}");
        }}

        .{p}__file-text {{
            display: flex;
            flex-direction: column;
            overflow: hidden;
            min-width: 0;
        }}

        .{p}__file-name {{
            font-size: 0.95rem;
            font-weight: 700;
            color: #111111;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            margin-bottom: 2px;
        }}

        .{p}__file-size {{
            font-size: 0.8rem;
            color: #888888;
            font-weight: 500;
        }}

        .{p}__actions {{
            display: flex;
            align-items: center;
            gap: 16px;
            margin-left: 10px;
            flex-shrink: 0;
        }}

        .{p}__action {{
            width: 18px;
            height: 18px;
            background: center / contain no-repeat;
            opacity: 0.85;
        }}

        .{p}__action--preview {{
            background-image: url("{_ICON_EYE}");
        }}

        .{p}__action--download {{
            background-image: url("{_ICON_DOWNLOAD}");
        }}

        @media (max-width: 992px) {{
            .{p}__grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}

        @media (max-width: 650px) {{
            .{p}__header {{
                flex-direction: column;
                align-items: flex-start;
            }}
            .{p}__download-all {{
                width: 100%;
                justify-content: center;
            }}
            .{p}__grid {{
                grid-template-columns: 1fr;
                gap: 12px;
            }}
        }}
    """


def inject_about_brands_styles() -> None:
    render_html(f"<style>{about_brands_styles()}</style>")


def _file_card_html(file_item: dict[str, str]) -> str:
    p = _PREFIX
    return f"""
    <div class="{p}__file-card">
        <div class="{p}__file-info">
            <div class="{p}__file-icon"><span aria-hidden="true"></span></div>
            <div class="{p}__file-text">
                <span class="{p}__file-name">{html.escape(file_item["name"])}</span>
                <span class="{p}__file-size">{html.escape(file_item["size"])}</span>
            </div>
        </div>
        <div class="{p}__actions">
            <span class="{p}__action {p}__action--preview" aria-label="Preview"></span>
            <span class="{p}__action {p}__action--download" aria-label="Download"></span>
        </div>
    </div>
    """


def build_about_brands_html(files: list[dict[str, str]]) -> str:
    p = _PREFIX
    cards = "".join(_file_card_html(item) for item in files)
    return f"""
    <section class="{p}">
        <div class="{p}__header">
            <h2 class="{p}__title">Our Brand</h2>
            <button type="button" class="{p}__download-all">
                <span class="{p}__download-all-icon" aria-hidden="true"></span>
                Download all files
            </button>
        </div>
        <div class="{p}__grid">{cards}</div>
    </section>
    """


def render_about_brands(files: list[dict[str, str]]) -> None:
    inject_about_brands_styles()
    render_html(build_about_brands_html(files), width="stretch")
