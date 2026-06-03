"""Member directory map panel — displays bundled Google map image."""

from __future__ import annotations

from theme.asset_urls import asset_img_tag
from theme.html_utils import render_st_html_page
from theme.paths import image_path

_PREFIX = "nexus-member-map"
_MAP_IMAGE = "google-map.jpg"


def member_map_styles() -> str:
    p = _PREFIX
    return f"""
        .{p} {{
            width: 100%;
            box-sizing: border-box;
        }}

        .{p}__frame {{
            width: 100%;
            border-radius: 6px;
            overflow: hidden;
            background: #ffffff;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            border: 1px solid #eaeaea;
        }}

        .{p}__frame img {{
            display: block;
            width: 100%;
            height: auto;
            object-fit: cover;
        }}
    """


def build_member_map_html() -> str:
    p = _PREFIX
    img = asset_img_tag(
        image_path(_MAP_IMAGE),
        css_class=f"{p}__image",
        image_id="nexus-member-directory-map",
    )
    return f"""
    <div class="{p}">
        <div class="{p}__frame">
            {img}
        </div>
    </div>
    """


def render_member_directory_map() -> None:
    render_st_html_page(member_map_styles(), build_member_map_html(), width="stretch")
