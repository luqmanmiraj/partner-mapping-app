"""About page intro section — matches .prototype/company/about.html."""

from __future__ import annotations

from theme.html_utils import render_html

_PREFIX = "nexus-about-about"


def about_about_styles() -> str:
    p = _PREFIX
    return f"""
        .{p} {{
            width: 100%;
            max-width: 1100px;
            margin: 0 auto 1.5rem;
            background-color: #ffffff;
            padding: 40px 45px;
            border-radius: 4px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}

        .{p}__title {{
            font-size: 1.8rem;
            font-weight: 700;
            color: #111111;
            margin: 0 0 24px 0;
        }}

        .{p}__text {{
            font-size: 1.05rem;
            line-height: 1.6;
            color: #555555;
            margin: 0 0 24px 0;
        }}

        .{p}__text:last-child {{
            margin-bottom: 0;
        }}

        .{p}__highlight {{
            color: #f39c12;
            font-weight: 700;
        }}

        @media (max-width: 768px) {{
            .{p} {{
                padding: 25px 20px;
            }}
            .{p}__title {{
                font-size: 1.5rem;
                margin-bottom: 18px;
            }}
            .{p}__text {{
                font-size: 0.95rem;
                margin-bottom: 18px;
            }}
        }}
    """


def inject_about_about_styles() -> None:
    render_html(f"<style>{about_about_styles()}</style>")


def build_about_about_html(paragraphs: list[str]) -> str:
    p = _PREFIX
    body = "".join(f'<p class="{p}__text">{text}</p>' for text in paragraphs)
    return f"""
    <section class="{p}">
        <h2 class="{p}__title">About</h2>
        {body}
    </section>
    """


def render_about_about(paragraphs: list[str]) -> None:
    inject_about_about_styles()
    render_html(build_about_about_html(paragraphs), width="stretch")
