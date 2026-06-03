"""My Company Contacts tab — prototype CSS from company_contacts-tab.html."""

from __future__ import annotations

import html

from theme.company_templates import render_company_tab_document


def _contact_card(contact: dict[str, str]) -> str:
    avatar = html.escape(contact.get("avatar", ""))
    return f"""<div class="contact-card">
<div class="card-profile-header">
<img class="profile-avatar" src="{avatar}" alt="Profile Headshot">
<div class="profile-name-details">
<h4>{html.escape(contact["name"])}</h4>
<span>{html.escape(contact["position"])}</span>
</div>
<button type="button" class="card-options-btn" aria-label="More options">
<i class="fa-solid fa-ellipsis"></i>
</button>
</div>
<div class="card-meta-body">
<div class="meta-line"><i class="fa-regular fa-user"></i> <span>{html.escape(contact["segment"])}</span></div>
<div class="meta-line"><i class="fa-solid fa-map-marker-alt"></i> <span>{html.escape(contact["region"])}</span></div>
<div class="meta-line"><i class="fa-regular fa-envelope"></i> <span>{html.escape(contact["email"])}</span></div>
</div>
</div>"""


def _page_html(contacts: list[dict[str, str]]) -> str:
    cards = "\n".join(_contact_card(c) for c in contacts)
    return f"""<div class="dashboard-container">
<div class="control-bar">
<div class="search-wrapper">
<i class="fa-solid fa-magnifying-glass search-icon"></i>
<input type="text" placeholder="Search for a topic..." readonly>
</div>
<select class="filter-dropdown" disabled><option>Region</option></select>
<button type="button" class="add-contact-btn">
<i class="fa-solid fa-plus"></i> Add New Contact
</button>
</div>
<main class="contacts-grid">
{cards}
</main>
<footer class="pagination">
<button type="button" class="page-btn arrow-btn" aria-label="Previous Page">
<i class="fa-solid fa-chevron-left"></i>
</button>
<button type="button" class="page-btn active">1</button>
<button type="button" class="page-btn">2</button>
<button type="button" class="page-btn">3</button>
<button type="button" class="page-btn arrow-btn" aria-label="Next Page">
<i class="fa-solid fa-chevron-right"></i>
</button>
</footer>
</div>"""


def render_company_contacts_tab(contacts: list[dict[str, str]]) -> None:
    render_company_tab_document("company_contacts-tab", _page_html(contacts))
