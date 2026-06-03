"""Profile dropdown — .prototype/sections/user-dropdown.html."""

from __future__ import annotations

import html

from auth.session import UserSession, get_session
from theme.html_utils import inject_parent_styles, render_html

_PREFIX = "nexus-user-dropdown"

_INFO_ICON = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' "
    "viewBox='0 0 24 24' fill='none' stroke='%23111' stroke-width='2' "
    "stroke-linecap='round' stroke-linejoin='round'%3e%3cpath d='M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2'/%3e"
    "%3ccircle cx='12' cy='7' r='4'/%3e%3c/svg%3e"
)
_LOGOUT_ICON = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' "
    "viewBox='0 0 24 24' fill='none' stroke='%23e53e3e' stroke-width='2.2' "
    "stroke-linecap='round' stroke-linejoin='round'%3e%3cpath d='M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4'/%3e"
    "%3cpolyline points='16 17 21 12 16 7'/%3e%3cline x1='21' y1='12' x2='9' y2='12'/%3e%3c/svg%3e"
)


def user_dropdown_styles() -> str:
    p = _PREFIX
    return f"""
        .{p} .profile-dropdown {{
            width: 280px;
            background-color: #ffffff;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
            border: 1px solid rgba(0, 0, 0, 0.04);
            box-sizing: border-box;
        }}

        .{p} .dropdown-header {{
            background-color: #111111;
            padding: 24px 20px;
            text-align: center;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}

        .{p} .user-name {{
            color: #ffffff;
            font-size: 18px;
            font-weight: 700;
            letter-spacing: -0.2px;
            margin: 0;
            line-height: 1.2;
        }}

        .{p} .user-email {{
            color: #cccccc;
            font-size: 13px;
            font-weight: 400;
            word-break: break-all;
        }}

        .{p} .dropdown-menu-list {{
            list-style: none;
            padding: 12px 0;
            margin: 0;
            display: flex;
            flex-direction: column;
        }}

        .{p} .menu-item {{
            width: 100%;
        }}

        .{p} .menu-link {{
            width: 100%;
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 14px 24px;
            background: none;
            border: none;
            text-align: left;
            font-size: 15px;
            font-weight: 500;
            cursor: pointer;
            text-decoration: none;
            transition: background-color 0.15s ease;
            box-sizing: border-box;
        }}

        .{p} .link-info {{
            color: #111111;
        }}

        .{p} .link-info:hover {{
            background-color: #f5f5f5;
        }}

        .{p} .link-logout {{
            color: #e53e3e;
        }}

        .{p} .link-logout:hover {{
            background-color: #fff5f5;
        }}

        .{p} .menu-icon {{
            flex-shrink: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            width: 20px;
            height: 20px;
            background: center / contain no-repeat;
        }}

        .{p} .menu-icon--info {{
            background-image: url("{_INFO_ICON}");
        }}

        .{p} .menu-icon--logout {{
            background-image: url("{_LOGOUT_ICON}");
        }}
    """


def inject_user_dropdown_styles() -> None:
    inject_parent_styles(user_dropdown_styles(), style_id="nexus-user-dropdown")


def _user_email(session: UserSession) -> str:
    key = (session.partner_key or "user").lower().replace("_", ".")
    return f"{key}@nexus.com"


def build_user_dropdown_html(session: UserSession | None = None) -> str:
    session = session or get_session()
    p = _PREFIX
    name = html.escape(session.display_name or "User")
    email = html.escape(_user_email(session))

    return f"""
    <div class="{p}">
        <div class="profile-dropdown">
            <div class="dropdown-header">
                <h2 class="user-name">{name}</h2>
                <span class="user-email">{email}</span>
            </div>
            <ul class="dropdown-menu-list">
                <li class="menu-item">
                    <span class="menu-link link-info">
                        <span class="menu-icon menu-icon--info" aria-hidden="true"></span>
                        Information
                    </span>
                </li>
                <li class="menu-item">
                    <span class="menu-link link-logout">
                        <span class="menu-icon menu-icon--logout" aria-hidden="true"></span>
                        Log out
                    </span>
                </li>
            </ul>
        </div>
    </div>
    """
