"""My Company Contacts tab — matches .prototype/company/company_contacts-tab.html."""

from __future__ import annotations

import html

from theme.html_utils import render_html

_ROOT = "nexus-company-contacts"

_ICON_SEARCH = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%234a5568' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z'/%3e%3c/svg%3e"
)
_ICON_PLUS = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23ffffff' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M12 5v14m7-7H5'/%3e%3c/svg%3e"
)
_ICON_USER = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23718096' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z'/%3e%3c/svg%3e"
)
_ICON_MAP = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23718096' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z'/%3e%3ccircle "
    "stroke-linecap='round' stroke-linejoin='round' cx='12' cy='11' r='2'/%3e%3c/svg%3e"
)
_ICON_MAIL = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23718096' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z'/%3e%3c/svg%3e"
)
_ICON_DOTS = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='%23718096' "
    "viewBox='0 0 24 24'%3e%3ccircle cx='5' cy='12' r='2'/%3e%3ccircle cx='12' cy='12' r='2'/%3e%3ccircle cx='19' cy='12' r='2'/%3e%3c/svg%3e"
)
_ICON_CHEV_LEFT = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%234a5568' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M15 19l-7-7 7-7'/%3e%3c/svg%3e"
)
_ICON_CHEV_RIGHT = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%234a5568' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M9 5l7 7-7 7'/%3e%3c/svg%3e"
)


def company_contacts_tab_styles() -> str:
    return f"""
        .nexus-company-contacts {{
            width: 100%;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #111111;
        }}

        .nexus-company-contacts .dashboard-container {{
            width: 100%;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
            box-sizing: border-box;
        }}

        .nexus-company-contacts .control-bar {{
            display: flex;
            gap: 15px;
            margin-bottom: 25px;
            align-items: center;
            flex-wrap: wrap;
        }}

        .nexus-company-contacts .search-wrapper {{
            position: relative;
            flex: 1;
            min-width: 280px;
        }}

        .nexus-company-contacts .search-wrapper input {{
            width: 100%;
            padding: 10px 16px 10px 40px;
            font-size: 0.9rem;
            border: 1.5px solid #cbd5e0;
            border-radius: 6px;
            color: #2d3748;
            outline: none;
            box-sizing: border-box;
        }}

        .nexus-company-contacts .search-wrapper input::placeholder {{
            color: #a0aec0;
        }}

        .nexus-company-contacts .search-wrapper::before {{
            content: "";
            position: absolute;
            left: 14px;
            top: 50%;
            transform: translateY(-50%);
            width: 16px;
            height: 16px;
            background: url("{_ICON_SEARCH}") center / contain no-repeat;
            pointer-events: none;
            z-index: 5;
        }}

        .nexus-company-contacts .filter-dropdown {{
            padding: 10px 35px 10px 16px;
            font-size: 0.9rem;
            border: 1.5px solid #cbd5e0;
            border-radius: 6px;
            background-color: #ffffff;
            color: #2d3748;
            appearance: none;
            background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='10' height='6' viewBox='0 0 10 6'><path fill='%234a5568' d='M0 0l5 5 5-5z'/></svg>");
            background-repeat: no-repeat;
            background-position: right 14px center;
            outline: none;
            cursor: pointer;
        }}

        .nexus-company-contacts .add-contact-btn {{
            background-color: #0b0f19;
            color: #ffffff;
            border: none;
            border-radius: 6px;
            padding: 11px 20px;
            font-size: 0.9rem;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            margin-left: auto;
            cursor: pointer;
            transition: background-color 0.15s ease;
        }}

        .nexus-company-contacts .add-contact-btn:hover {{
            background-color: #1a2336;
        }}

        .nexus-company-contacts .add-contact-btn::before {{
            content: "";
            width: 14px;
            height: 14px;
            background: url("{_ICON_PLUS}") center / contain no-repeat;
        }}

        .nexus-company-contacts .contacts-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 35px;
        }}

        .nexus-company-contacts .contact-card {{
            background-color: #ffffff;
            border: 1.5px solid #e2e8f0;
            border-radius: 8px;
            overflow: hidden;
        }}

        .nexus-company-contacts .card-profile-header {{
            background-color: #f8fafc;
            padding: 16px;
            display: flex;
            align-items: center;
            gap: 14px;
            border-bottom: 1.5px solid #e2e8f0;
            position: relative;
            box-sizing: border-box;
        }}

        .nexus-company-contacts .profile-avatar {{
            width: 46px;
            height: 46px;
            border-radius: 50%;
            object-fit: cover;
            background-color: #cbd5e0;
            flex-shrink: 0;
        }}

        .nexus-company-contacts .profile-name-details {{
            display: flex;
            flex-direction: column;
            overflow: hidden;
            min-width: 0;
        }}

        .nexus-company-contacts .profile-name-details h4 {{
            font-size: 1rem;
            font-weight: 700;
            color: #1a1a1a;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            margin: 0 0 2px 0;
        }}

        .nexus-company-contacts .profile-name-details span {{
            font-size: 0.85rem;
            color: #718096;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .nexus-company-contacts .card-options-btn {{
            position: absolute;
            top: 16px;
            right: 14px;
            background: url("{_ICON_DOTS}") center / contain no-repeat;
            border: none;
            width: 18px;
            height: 18px;
            padding: 0;
            cursor: pointer;
        }}

        .nexus-company-contacts .card-meta-body {{
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            box-sizing: border-box;
        }}

        .nexus-company-contacts .meta-line {{
            display: flex;
            align-items: center;
            gap: 12px;
            color: #4a5568;
            font-size: 0.88rem;
        }}

        .nexus-company-contacts .meta-line::before {{
            content: "";
            width: 16px;
            height: 16px;
            flex-shrink: 0;
            background: center / contain no-repeat;
        }}

        .nexus-company-contacts .meta-line--user::before {{
            background-image: url("{_ICON_USER}");
        }}

        .nexus-company-contacts .meta-line--map::before {{
            background-image: url("{_ICON_MAP}");
        }}

        .nexus-company-contacts .meta-line--mail::before {{
            background-image: url("{_ICON_MAIL}");
        }}

        .nexus-company-contacts .pagination {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 8px;
            margin-top: 10px;
        }}

        .nexus-company-contacts .page-btn {{
            background: none;
            border: none;
            color: #4a5568;
            font-size: 0.9rem;
            font-weight: 600;
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 4px;
            cursor: pointer;
            text-decoration: none;
            padding: 0;
        }}

        .nexus-company-contacts .page-btn.active {{
            color: #1a1a1a;
            font-weight: 800;
        }}

        .nexus-company-contacts .page-btn.arrow-btn::after {{
            content: "";
            width: 14px;
            height: 14px;
            background: center / contain no-repeat;
            display: inline-block;
        }}

        .nexus-company-contacts .page-btn.arrow-btn--left::after {{
            background-image: url("{_ICON_CHEV_LEFT}");
        }}

        .nexus-company-contacts .page-btn.arrow-btn--right::after {{
            background-image: url("{_ICON_CHEV_RIGHT}");
        }}

        @media (max-width: 1024px) {{
            .nexus-company-contacts .contacts-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}

        @media (max-width: 730px) {{
            .nexus-company-contacts .control-bar {{
                flex-direction: column;
                align-items: stretch;
            }}
            .nexus-company-contacts .add-contact-btn {{
                margin-left: 0;
                justify-content: center;
            }}
            .nexus-company-contacts .contacts-grid {{
                grid-template-columns: 1fr;
                gap: 16px;
            }}
        }}
    """


def inject_company_contacts_tab_styles() -> None:
    render_html(f"<style>{company_contacts_tab_styles()}</style>")


def _contact_card(contact: dict[str, str]) -> str:
    avatar = html.escape(contact.get("avatar", ""))
    return f"""
      <div class="contact-card">
        <div class="card-profile-header">
          <img class="profile-avatar" src="{avatar}" alt="">
          <div class="profile-name-details">
            <h4>{html.escape(contact["name"])}</h4>
            <span>{html.escape(contact["position"])}</span>
          </div>
          <button class="card-options-btn" aria-label="More options"></button>
        </div>
        <div class="card-meta-body">
          <div class="meta-line meta-line--user">
            <span>{html.escape(contact["segment"])}</span>
          </div>
          <div class="meta-line meta-line--map">
            <span>{html.escape(contact["region"])}</span>
          </div>
          <div class="meta-line meta-line--mail">
            <span>{html.escape(contact["email"])}</span>
          </div>
        </div>
      </div>
    """


def build_company_contacts_tab_html(contacts: list[dict[str, str]]) -> str:
    cards = "".join(_contact_card(c) for c in contacts)
    return f"""
    <div class="nexus-company-contacts">
      <div class="dashboard-container">
        <div class="control-bar">
          <div class="search-wrapper">
            <input type="text" placeholder="Search for a topic..." readonly>
          </div>
          <select class="filter-dropdown" disabled><option>Region</option></select>
          <button class="add-contact-btn">Add New Contact</button>
        </div>
        <main class="contacts-grid">
          {cards}
        </main>
        <footer class="pagination">
          <button class="page-btn arrow-btn arrow-btn--left" aria-label="Previous Page"></button>
          <button class="page-btn active">1</button>
          <button class="page-btn">2</button>
          <button class="page-btn">3</button>
          <button class="page-btn arrow-btn arrow-btn--right" aria-label="Next Page"></button>
        </footer>
      </div>
    </div>
    """


def render_company_contacts_tab(contacts: list[dict[str, str]]) -> None:
    inject_company_contacts_tab_styles()
    render_html(build_company_contacts_tab_html(contacts), width="stretch")

