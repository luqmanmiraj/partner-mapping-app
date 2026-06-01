"""Single Service Details Widget — matches .prototype/services/service-single.html."""

from __future__ import annotations

import html
from typing import Any
import calendar
import datetime

import streamlit as st

from data.services_fixtures import get_service
from theme.html_utils import render_html


def get_service_icon(service_id: str) -> str:
    """Return the correct FontAwesome icon class for the given service."""
    icons = {
        "marketing": "fa-regular fa-image",
        "supply_chain": "fa-solid fa-truck-fast",
        "tech_integration": "fa-solid fa-laptop-code",
        "sourcing": "fa-solid fa-handshake",
    }
    return icons.get(service_id, "fa-regular fa-star")


def get_month_name(m: int) -> str:
    """Return the French month label."""
    month_names = {
        1: "Janvier",
        2: "Février",
        3: "Mars",
        4: "Avril",
        5: "Mai",
        6: "Juin",
        7: "Juillet",
        8: "Août",
        9: "Septembre",
        10: "Octobre",
        11: "Novembre",
        12: "Décembre",
    }
    return month_names.get(m, "")


def get_calendar_grid(year: int, month: int) -> list[list[dict[str, Any]]]:
    """Dynamically calculate a Monday-first calendar grid with neighboring days."""
    first_day = datetime.date(year, month, 1)
    # firstweekday = 0 is Monday. first_day.weekday() returns 0 (Mon) to 6 (Sun).
    start_date = first_day - datetime.timedelta(days=first_day.weekday())

    grid = []
    current_date = start_date

    # Determine weeks needed (5 or 6)
    num_weeks = 5
    end_date = start_date + datetime.timedelta(days=35)
    last_day_num = calendar.monthrange(year, month)[1]
    last_day_date = datetime.date(year, month, last_day_num)
    if last_day_date >= end_date:
        num_weeks = 6

    for _ in range(num_weeks):
        week = []
        for _ in range(7):
            is_active_month = current_date.month == month
            # Mimic prototype: days < 15 in December 2025 are muted (already passed)
            is_muted = not is_active_month or (current_date.day < 15 and is_active_month)

            week.append({
                "day": current_date.day,
                "is_muted": is_muted,
                "is_active_month": is_active_month,
            })
            current_date += datetime.timedelta(days=1)
        grid.append(week)
    return grid


def service_single_styles() -> str:
    """Return zero-indented stylesheet scoped under srv-single to prevent markdown preformatting issues."""
    return """<style>
.srv-single-page-wrapper * {
margin: 0;
padding: 0;
box-sizing: border-box;
}

.srv-single-page-wrapper {
font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
background-color: #eeeeee;
color: #111111;
padding: 40px 24px;
min-height: 100vh;
}

.srv-single-workspace-wrapper {
max-width: 1200px;
margin: 0 auto;
display: grid;
grid-template-columns: 1fr 380px;
gap: 24px;
align-items: start;
}

.srv-single-content-card-panel {
background-color: #ffffff;
border-radius: 4px;
padding: 24px;
box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}

.srv-single-left-stream-container {
display: flex;
flex-direction: column;
gap: 24px;
}

.srv-single-back-nav-link {
display: inline-flex;
align-items: center;
gap: 8px;
text-decoration: none;
color: #333333;
font-size: 0.85rem;
font-weight: 600;
margin-bottom: -8px;
cursor: pointer;
transition: color 0.15s ease;
}

.srv-single-back-nav-link:hover {
color: #f39c12;
}

.srv-single-service-profile-header {
display: flex;
gap: 16px;
align-items: flex-start;
}

.srv-single-service-icon-box {
width: 48px;
height: 48px;
border: 1.5px solid #bdc3c7;
border-radius: 4px;
display: flex;
align-items: center;
justify-content: center;
font-size: 1.25rem;
color: #333333;
flex-shrink: 0;
}

.srv-single-service-title-block h1 {
font-size: 1.45rem;
font-weight: 700;
color: #000000;
margin-bottom: 4px;
margin-top: 0;
line-height: 1.2;
}

.srv-single-service-title-block p {
font-size: 0.9rem;
color: #666666;
line-height: 1.4;
}

.srv-single-info-inner-block {
background-color: #f5f5f5;
border-radius: 4px;
padding: 20px;
text-align: left;
}

.srv-single-info-inner-block h3 {
font-size: 0.95rem;
font-weight: 700;
color: #000000;
margin-bottom: 10px;
margin-top: 0;
}

.srv-single-info-inner-block p {
font-size: 0.86rem;
color: #444444;
line-height: 1.5;
}

.srv-single-checklist-container {
display: flex;
flex-direction: column;
gap: 10px;
margin-top: 12px;
}

.srv-single-checklist-row {
display: flex;
align-items: center;
gap: 10px;
font-size: 0.86rem;
color: #444444;
}

.srv-single-checklist-row i {
color: #f39c12;
font-size: 0.95rem;
}

.srv-single-resources-grid-layout {
display: grid;
grid-template-columns: repeat(2, 1fr);
gap: 12px;
margin-top: 12px;
}

.srv-single-resource-mini-card {
background-color: #ffffff;
border: 1px solid #e0e0e0;
border-radius: 4px;
padding: 12px 16px;
display: flex;
align-items: center;
gap: 12px;
}

.srv-single-resource-icon-orange {
color: #f39c12;
font-size: 1.1rem;
}

.srv-single-resource-meta {
flex: 1;
display: flex;
flex-direction: column;
min-width: 0;
text-align: left;
}

.srv-single-resource-meta h4 {
font-size: 0.88rem;
font-weight: 700;
color: #111111;
white-space: nowrap;
overflow: hidden;
text-overflow: ellipsis;
margin: 0 0 2px 0;
}

.srv-single-resource-meta span {
font-size: 0.76rem;
color: #777777;
}

.srv-single-resource-actions-tray {
display: flex;
gap: 12px;
color: #777777;
font-size: 0.88rem;
}

.srv-single-resource-actions-tray i {
cursor: pointer;
transition: color 0.15s ease;
}

.srv-single-resource-actions-tray i:hover {
color: #f39c12;
}

.srv-single-contacts-section-title {
font-size: 1.1rem;
font-weight: 700;
color: #000000;
margin-bottom: 14px;
margin-top: 0;
text-align: left;
}

.srv-single-contacts-filter-bar {
display: flex;
gap: 12px;
margin-bottom: 16px;
}

.srv-single-contact-search-box {
position: relative;
flex: 1;
}

.srv-single-contact-search-box input {
width: 100%;
padding: 10px 35px 10px 12px;
font-size: 0.84rem;
border: 1px solid #cccccc;
border-radius: 4px;
outline: none;
box-sizing: border-box;
}

.srv-single-contact-search-box i {
position: absolute;
right: 12px;
top: 50%;
transform: translateY(-50%);
color: #333333;
cursor: pointer;
}

.srv-single-contact-dropdown-select {
padding: 10px 24px 10px 12px;
font-size: 0.84rem;
border: 1px solid #cccccc;
border-radius: 4px;
background-color: #ffffff;
color: #333333;
outline: none;
min-width: 140px;
cursor: pointer;
box-sizing: border-box;
}

.srv-single-contacts-cards-grid {
display: grid;
grid-template-columns: repeat(3, 1fr);
gap: 12px;
}

.srv-single-profile-mini-card {
border: 1px solid #e0e0e0;
border-radius: 4px;
overflow: hidden;
background-color: #ffffff;
display: flex;
flex-direction: column;
}

.srv-single-profile-card-header {
background-color: #f0f0f0;
padding: 12px;
display: flex;
flex-direction: column;
align-items: center;
text-align: center;
}

.srv-single-profile-card-header h4 {
font-size: 0.88rem;
font-weight: 700;
color: #000000;
margin: 0 0 2px 0;
}

.srv-single-profile-card-header span {
font-size: 0.78rem;
color: #555555;
margin-top: 2px;
}

.srv-single-profile-card-body {
padding: 12px;
display: flex;
flex-direction: column;
gap: 8px;
text-align: left;
}

.srv-single-profile-info-line {
display: flex;
align-items: center;
gap: 10px;
font-size: 0.78rem;
color: #555555;
}

.srv-single-profile-info-line i {
color: #777777;
width: 14px;
text-align: center;
}

.srv-single-pagination-row {
display: flex;
justify-content: center;
align-items: center;
gap: 16px;
margin-top: 16px;
font-size: 0.82rem;
color: #555555;
}

.srv-single-pagination-row i {
cursor: pointer;
transition: color 0.15s ease;
}

.srv-single-pagination-row i:hover {
color: #000000;
}

.srv-single-pagination-row span {
cursor: pointer;
transition: color 0.15s ease;
padding: 2px 6px;
}

.srv-single-pagination-row span:hover {
color: #000000;
}

.srv-single-pagination-row span.srv-single-active-page {
font-weight: 700;
color: #000000;
border-bottom: 2px solid #000000;
}

.srv-single-right-sidebar-panel {
display: flex;
flex-direction: column;
background-color: #ffffff;
border-radius: 4px;
overflow: hidden;
box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}

.srv-single-tracker-steps-header {
display: flex;
justify-content: space-around;
align-items: center;
padding: 16px 10px;
border-bottom: 1px solid #eeeeee;
background-color: #ffffff;
}

.srv-single-step-indicator-item {
display: flex;
flex-direction: column;
align-items: center;
gap: 6px;
position: relative;
flex: 1;
}

.srv-single-step-indicator-item::after {
content: '';
position: absolute;
top: 5px;
right: -50%;
width: 100%;
height: 1px;
background-color: #dddddd;
z-index: 1;
}

.srv-single-step-indicator-item:last-child::after {
display: none;
}

.srv-single-circle-node {
width: 12px;
height: 12px;
border: 1px solid #777777;
border-radius: 50%;
background-color: #ffffff;
z-index: 2;
}

.srv-single-step-indicator-item.srv-active .srv-single-circle-node {
background-color: #ffffff;
border-color: #111111;
}

.srv-single-step-indicator-item label {
font-size: 0.65rem;
font-weight: 700;
text-transform: uppercase;
color: #666666;
letter-spacing: 0.5px;
}

.srv-single-calendar-dark-section {
background-color: #141619;
color: #ffffff;
padding: 24px 20px;
display: flex;
flex-direction: column;
align-items: center;
}

.srv-single-calendar-host-profile {
display: flex;
flex-direction: column;
align-items: center;
margin-bottom: 16px;
}

.srv-single-calendar-host-profile img {
width: 44px;
height: 44px;
border-radius: 50%;
object-fit: cover;
margin-bottom: 12px;
}

.srv-single-calendar-host-profile h2 {
font-size: 0.95rem;
font-weight: 600;
text-align: center;
margin: 0;
color: #ffffff !important;
}

.srv-single-calendar-month-selector {
display: flex;
justify-content: center;
align-items: center;
gap: 20px;
width: 100%;
margin-bottom: 20px;
font-size: 0.84rem;
font-weight: 700;
}

.srv-single-calendar-month-selector i {
cursor: pointer;
font-size: 0.75rem;
padding: 4px;
transition: opacity 0.15s ease;
}

.srv-single-calendar-month-selector i:hover {
opacity: 0.8;
}

.srv-single-calendar-days-grid {
display: grid;
grid-template-columns: repeat(7, 1fr);
gap: 12px 6px;
width: 100%;
text-align: center;
}

.srv-single-day-header-label {
font-size: 0.65rem;
font-weight: 700;
color: #999999;
text-transform: uppercase;
margin-bottom: 4px;
}

.srv-single-day-numeric-cell {
font-size: 0.8rem;
height: 28px;
display: flex;
align-items: center;
justify-content: center;
cursor: pointer;
color: #ffffff;
transition: background-color 0.15s ease;
border-radius: 50%;
width: 28px;
height: 28px;
margin: 0 auto;
}

.srv-single-day-numeric-cell:hover:not(.srv-single-muted) {
background-color: rgba(255,255,255,0.15);
}

.srv-single-day-numeric-cell.srv-single-muted {
color: #444444;
pointer-events: none;
cursor: default;
}

.srv-single-day-numeric-cell.srv-single-selected-active {
background-color: #f39c12;
color: #141619;
font-weight: 700;
}

.srv-single-booking-interactive-body {
padding: 24px 20px;
display: flex;
flex-direction: column;
gap: 16px;
background-color: #ffffff;
}

.srv-single-booking-question-title {
font-size: 0.88rem;
font-weight: 700;
color: #000000;
text-align: left;
margin-top: 0;
margin-bottom: 0;
}

.srv-single-duration-toggle-row {
display: grid;
grid-template-columns: repeat(3, 1fr);
border: 1px solid #e0e0e0;
border-radius: 4px;
overflow: hidden;
}

.srv-single-duration-option-btn {
text-align: center;
padding: 10px 0;
font-size: 0.78rem;
font-weight: 600;
color: #666666;
background-color: #ffffff;
border: none;
cursor: pointer;
border-right: 1px solid #e0e0e0;
transition: all 0.15s ease;
}

.srv-single-duration-option-btn:last-child {
border-right: none;
}

.srv-single-duration-option-btn:hover:not(.srv-active) {
background-color: #f9f9f9;
}

.srv-single-duration-option-btn.srv-active {
background-color: #f39c12;
color: #ffffff;
}

.srv-single-timezone-stamp-meta {
font-size: 0.72rem;
color: #666666;
display: flex;
justify-content: space-between;
align-items: center;
margin-top: 4px;
}

.srv-single-timezone-stamp-meta select {
border: none;
background: transparent;
font-weight: 700;
color: #444444;
font-size: 0.72rem;
outline: none;
cursor: pointer;
}

.srv-single-time-slots-vertical-stack {
display: flex;
flex-direction: column;
gap: 8px;
max-height: 280px;
overflow-y: auto;
padding-right: 4px;
}

.srv-single-time-slot-option-row {
width: 100%;
padding: 12px;
border: 1px solid #e0e0e0;
border-radius: 4px;
background-color: #ffffff;
font-size: 0.84rem;
font-weight: 600;
color: #333333;
text-align: center;
cursor: pointer;
transition: all 0.15s ease;
outline: none;
}

.srv-single-time-slot-option-row:hover {
border-color: #111111;
background-color: #fafafa;
}

.srv-single-time-slots-vertical-stack::-webkit-scrollbar {
width: 4px;
}
.srv-single-time-slots-vertical-stack::-webkit-scrollbar-thumb {
background-color: #cccccc;
border-radius: 2px;
}

/* Hidden transition inputs & triggers styling */
.single-action-hidden {
position: absolute !important;
opacity: 0 !important;
width: 0 !important;
height: 0 !important;
overflow: hidden !important;
pointer-events: none !important;
}

@media (max-width: 992px) {
.srv-single-workspace-wrapper {
grid-template-columns: 1fr;
}
}

@media (max-width: 680px) {
.srv-single-contacts-cards-grid {
grid-template-columns: 1fr 1fr;
}
.srv-single-resources-grid-layout {
grid-template-columns: 1fr;
}
}

@media (max-width: 480px) {
.srv-single-contacts-cards-grid {
grid-template-columns: 1fr;
}
.srv-single-contacts-filter-bar {
flex-direction: column;
}
.srv-single-contact-dropdown-select {
width: 100%;
}
}
</style>
"""


def _generate_page_html(
    service: dict[str, Any],
    contacts_search: str,
    contacts_dept: str,
    current_page: int,
    active_month: int,
    active_year: int,
    selected_day: int,
    selected_duration: str,
) -> str:
    """Generate the complete premium scoped HTML for the Single Service view."""
    service_id = service["id"]
    title_esc = html.escape(service["title"])
    desc_esc = html.escape(service["description"])
    detail_desc_esc = html.escape(service["detailed_description"])
    exp_title_esc = html.escape(service["expertise_title"])
    exp_desc_esc = html.escape(service["expertise_desc"])

    # 1. Back button
    back_html = f"""<a href="#" class="srv-single-back-nav-link" onclick="triggerAction('back', '1'); return false;">
<i class="fa-solid fa-arrow-left"></i> Back to Service Catalog
</a>"""

    # 2. Left side profile header
    icon_cls = get_service_icon(service_id)
    header_html = f"""<div class="srv-single-service-profile-header">
<div class="srv-single-service-icon-box">
<i class="{icon_cls}"></i>
</div>
<div class="srv-single-service-title-block">
<h1>{title_esc}</h1>
<p>{desc_esc}</p>
</div>
</div>"""

    # 3. About section
    about_html = f"""<div class="srv-single-info-inner-block">
<h3>About</h3>
<p>{detail_desc_esc}</p>
</div>"""

    # 4. Expertise & Checklist section
    checklist_elements = []
    for item in service["checklist"]:
        checklist_elements.append(f"""<div class="srv-single-checklist-row">
<i class="fa-solid fa-circle-check"></i>
<span>{html.escape(item)}</span>
</div>""")

    expertise_html = f"""<div class="srv-single-info-inner-block">
<h3>{exp_title_esc}</h3>
<p>{exp_desc_esc}</p>
<div class="srv-single-checklist-container">
{"".join(checklist_elements)}
</div>
</div>"""

    # 5. Resources downloads section
    resource_cards = []
    for res in service["resources"]:
        res_name_esc = html.escape(res["name"])
        res_size_esc = html.escape(res["size"])
        resource_cards.append(f"""<div class="srv-single-resource-mini-card">
<i class="fa-regular fa-copy srv-single-resource-icon-orange"></i>
<div class="srv-single-resource-meta">
<h4>{res_name_esc}</h4>
<span>{res_size_esc}</span>
</div>
<div class="srv-single-resource-actions-tray">
<i class="fa-regular fa-eye" onclick="triggerAction('view_resource', '{res_name_esc}'); return false;"></i>
<i class="fa-solid fa-download" onclick="triggerAction('download_resource', '{res_name_esc}'); return false;"></i>
</div>
</div>""")

    resources_html = f"""<div class="srv-single-info-inner-block">
<h3>Resources</h3>
<div class="srv-single-resources-grid-layout">
{"".join(resource_cards)}
</div>
</div>"""

    # 6. Contacts Section with Directory Search / Filtering / Pagination
    # Gather distinct departments
    departments = sorted(list(set(c["department"] for c in service["contacts"])))
    dept_options = ["""<option value="All">Department</option>"""]
    for dept in departments:
        selected_attr = 'selected' if dept == contacts_dept else ''
        dept_options.append(f"""<option value="{html.escape(dept)}" {selected_attr}>{html.escape(dept)}</option>""")

    # Filter contacts list
    filtered_contacts = service["contacts"]
    if contacts_search.strip():
        kw = contacts_search.strip().lower()
        filtered_contacts = [
            c for c in filtered_contacts
            if kw in c["name"].lower() or kw in c["position"].lower() or kw in c["region"].lower()
        ]
    if contacts_dept != "All":
        filtered_contacts = [
            c for c in filtered_contacts
            if c["department"] == contacts_dept
        ]

    # Paginate contacts
    items_per_page = 3
    total_items = len(filtered_contacts)
    total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)

    if current_page > total_pages:
        current_page = total_pages
    if current_page < 1:
        current_page = 1

    start_idx = (current_page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_contacts = filtered_contacts[start_idx:end_idx]

    # Contact Cards Grid
    if not page_contacts:
        contacts_grid_html = """<div class="srv-single-info-inner-block" style="text-align:center; padding:30px; color:#777777;">No contacts found matching filters.</div>"""
    else:
        cards_list = []
        for c in page_contacts:
            name_esc = html.escape(c["name"])
            pos_esc = html.escape(c["position"])
            reg_esc = html.escape(c["region"])
            email_esc = html.escape(c["email"])
            phone_esc = html.escape(c["phone"])

            cards_list.append(f"""<div class="srv-single-profile-mini-card">
<div class="srv-single-profile-card-header">
<h4>{name_esc}</h4>
<span>{pos_esc}</span>
</div>
<div class="srv-single-profile-card-body">
<div class="srv-single-profile-info-line"><i class="fa-solid fa-map-marker-alt"></i> <span>{reg_esc}</span></div>
<div class="srv-single-profile-info-line"><i class="fa-regular fa-envelope"></i> <span>{email_esc}</span></div>
<div class="srv-single-profile-info-line"><i class="fa-solid fa-phone"></i> <span>{phone_esc}</span></div>
</div>
</div>""")
        contacts_grid_html = f"""<div class="srv-single-contacts-cards-grid">
{"".join(cards_list)}
</div>"""

    # Contacts Pagination Row
    pagination_html = ""
    if total_pages > 1:
        pag_numbers = []
        for p_idx in range(1, total_pages + 1):
            active_cls = "srv-single-active-page" if p_idx == current_page else ""
            pag_numbers.append(f"""<span class="{active_cls}" onclick="triggerAction('change_page', '{p_idx}'); return false;">{p_idx}</span>""")

        prev_click = f"triggerAction('change_page', '{current_page - 1}'); return false;" if current_page > 1 else "return false;"
        next_click = f"triggerAction('change_page', '{current_page + 1}'); return false;" if current_page < total_pages else "return false;"

        pagination_html = f"""<div class="srv-single-pagination-row">
<i class="fa-solid fa-chevron-left" onclick="{prev_click}"></i>
{"".join(pag_numbers)}
<i class="fa-solid fa-chevron-right" onclick="{next_click}"></i>
</div>"""

    contacts_section_html = f"""<div>
<h3 class="srv-single-contacts-section-title">Contacts</h3>
<div class="srv-single-contacts-filter-bar">
<div class="srv-single-contact-search-box">
<input type="text" id="member-search-field" placeholder="Search for a member..." value="{html.escape(contacts_search)}" onkeypress="if(event.key === 'Enter') {{ triggerAction('search_contacts', this.value); return false; }}">
<i class="fa-solid fa-magnifying-glass" onclick="triggerAction('search_contacts', document.getElementById('member-search-field').value);"></i>
</div>
<select class="srv-single-contact-dropdown-select" onchange="triggerAction('dept_contacts', this.value)">
{"".join(dept_options)}
</select>
</div>
{contacts_grid_html}
{pagination_html}
</div>"""

    # 7. Sidebar Panel: Progress Steps Header
    sidebar_tracker_html = """<div class="srv-single-tracker-steps-header">
<div class="srv-single-step-indicator-item srv-active">
<div class="srv-single-circle-node"></div>
<label>Choisir L'heure</label>
</div>
<div class="srv-single-step-indicator-item">
<div class="srv-single-circle-node"></div>
<label>Vos Informations</label>
</div>
</div>"""

    # 8. Sidebar Panel: Dark Calendar Core Component
    consultant_name_esc = html.escape(service["consultant"]["name"])
    consultant_avatar_esc = html.escape(service["consultant"]["avatar"])
    month_name_lbl = get_month_name(active_month)

    # Calculate Days Matrix cells
    cal_cells_list = []
    grid_matrix = get_calendar_grid(active_year, active_month)
    for week in grid_matrix:
        for cell in week:
            day_num = cell["day"]
            if cell["is_muted"]:
                cal_cells_list.append(f"""<span class="srv-single-day-numeric-cell srv-single-muted">{day_num}</span>""")
            else:
                is_selected = day_num == selected_day
                selected_cls = "srv-single-selected-active" if is_selected else ""
                cal_cells_list.append(f"""<span class="srv-single-day-numeric-cell {selected_cls}" onclick="triggerAction('select_day', '{day_num}'); return false;">{day_num}</span>""")

    calendar_dark_html = f"""<div class="srv-single-calendar-dark-section">
<div class="srv-single-calendar-host-profile">
<img src="{consultant_avatar_esc}" alt="Consultant Profile Photo">
<h2>Prenez rendez-vous avec {consultant_name_esc}</h2>
</div>

<div class="srv-single-calendar-month-selector">
<i class="fa-solid fa-chevron-left" onclick="triggerAction('prev_month', '1'); return false;"></i>
<span>{month_name_lbl} {active_year}</span>
<i class="fa-solid fa-chevron-right" onclick="triggerAction('next_month', '1'); return false;"></i>
</div>

<div class="srv-single-calendar-days-grid">
<span class="srv-single-day-header-label">Lun.</span>
<span class="srv-single-day-header-label">Mar.</span>
<span class="srv-single-day-header-label">Mer.</span>
<span class="srv-single-day-header-label">Jeu.</span>
<span class="srv-single-day-header-label">Ven.</span>
<span class="srv-single-day-header-label">Sam.</span>
<span class="srv-single-day-header-label">Dim.</span>

{"".join(cal_cells_list)}
</div>
</div>"""

    # 9. Sidebar Panel: Duration Toggle Selector
    dur_buttons_list = []
    for dur in service["available_durations"]:
        active_cls = "srv-active" if dur == selected_duration else ""
        dur_buttons_list.append(f"""<button class="srv-single-duration-option-btn {active_cls}" onclick="triggerAction('select_duration', '{dur}'); return false;">{dur}</button>""")

    # 10. Sidebar Panel: Dynamic Time Slots Grid
    selected_date_str = f"{selected_day} {month_name_lbl.lower()} {active_year}"
    slots_buttons_list = []
    for slot in service["available_slots"]:
        slots_buttons_list.append(f"""<button class="srv-single-time-slot-option-row" onclick="triggerAction('book_slot', '{slot}'); return false;">{slot}</button>""")

    booking_body_html = f"""<div class="srv-single-booking-interactive-body">
<h3 class="srv-single-booking-question-title">De combien de temps avez-vous besoin ?</h3>
<div class="srv-single-duration-toggle-row">
{"".join(dur_buttons_list)}
</div>

<h3 class="srv-single-booking-question-title" style="margin-top: 8px;">Quelle heure vous convient le mieux ?</h3>
<div class="srv-single-timezone-stamp-meta">
<span>Affichage des heures pour le <strong>{selected_date_str}</strong></span>
<select>
<option>UTC +01:00 Heure normale d'Europe centrale (Europe)</option>
</select>
</div>

<div class="srv-single-time-slots-vertical-stack">
{"".join(slots_buttons_list)}
</div>
</div>"""

    # Assemble everything into standard grid rows matching prototype 1-to-1
    return f"""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<div class="srv-single-page-wrapper">
<div class="srv-single-workspace-wrapper">

<div class="srv-single-left-stream-container">
{back_html}
<main class="srv-single-content-card-panel srv-single-left-stream-container">
{header_html}
{about_html}
{expertise_html}
{resources_html}
{contacts_section_html}
</main>
</div>

<aside class="srv-single-right-sidebar-panel">
{sidebar_tracker_html}
{calendar_dark_html}
{booking_body_html}
</aside>

</div>
</div>

<script>
function triggerAction(actionName, actionValue) {{
const inputEl = window.parent.document.querySelector('.st-key-service_single_action input');
const submitBtn = window.parent.document.querySelector('.st-key-service_single_submit button');
if (inputEl && submitBtn) {{
inputEl.value = actionName + ':' + actionValue;
inputEl.dispatchEvent(new Event('input', {{ bubbles: true }}));
submitBtn.click();
}}
}}
</script>
"""


def render_service_single(service_id: str) -> None:
    """Render the Single Service Details page with dynamic calendar booking and resource directory."""
    service = get_service(service_id)
    if not service:
        st.error("Service not found.")
        if st.button("Return to Catalog"):
            st.session_state.active_service_id = None
            st.rerun()
        return

    # 1. Initialize State variables
    search_key = f"contacts_search_{service_id}"
    dept_key = f"contacts_dept_{service_id}"
    page_key = f"contacts_page_{service_id}"
    month_key = f"cal_month_{service_id}"
    year_key = f"cal_year_{service_id}"
    day_key = f"selected_day_{service_id}"
    duration_key = f"selected_duration_{service_id}"

    if search_key not in st.session_state:
        st.session_state[search_key] = ""
    if dept_key not in st.session_state:
        st.session_state[dept_key] = "All"
    if page_key not in st.session_state:
        st.session_state[page_key] = 1
    if month_key not in st.session_state:
        st.session_state[month_key] = 12
    if year_key not in st.session_state:
        st.session_state[year_key] = 2025
    if day_key not in st.session_state:
        st.session_state[day_key] = 18
    if duration_key not in st.session_state:
        st.session_state[duration_key] = service["available_durations"][0]

    # 2. Inject Page Scoped Stylesheet (zero-indented)
    st.markdown(service_single_styles(), unsafe_allow_html=True)

    # 3. Success / Alert Banners at the top of the viewport
    booking_success_key = f"booking_success_{service_id}"
    booking_success = st.session_state.get(booking_success_key, "")
    if booking_success:
        st.success(booking_success)

    resource_msg_key = f"resource_message_{service_id}"
    resource_msg = st.session_state.get(resource_msg_key, "")
    if resource_msg:
        st.info(resource_msg)
        # Clear immediately so it only pops up once
        st.session_state[resource_msg_key] = ""

    # 4. Handle Programmatic Actions from JS triggers
    action_input = st.text_input(
        "action",
        key="service_single_action",
        label_visibility="collapsed",
    )
    # Hide the action text box using CSS
    st.html(
        """
        <script>
        (function() {
            const el = window.parent.document.querySelector('.st-key-service_single_action');
            if (el && !el.classList.contains('single-action-hidden')) {
                el.classList.add('single-action-hidden');
            }
        })();
        </script>
        """
    )

    if action_input.strip():
        # Clear action input immediately to prevent execution loops
        st.session_state.service_single_action = ""
        parts = action_input.split(":", 1)
        if len(parts) == 2:
            action, val = parts[0], parts[1]
            if action == "back":
                st.session_state.active_service_id = None
                st.rerun()
            elif action == "search_contacts":
                st.session_state[search_key] = val
                st.session_state[page_key] = 1
                st.rerun()
            elif action == "dept_contacts":
                st.session_state[dept_key] = val
                st.session_state[page_key] = 1
                st.rerun()
            elif action == "change_page":
                st.session_state[page_key] = int(val)
                st.rerun()
            elif action == "prev_month":
                m = st.session_state[month_key]
                y = st.session_state[year_key]
                if m == 1:
                    st.session_state[month_key] = 12
                    st.session_state[year_key] = y - 1
                else:
                    st.session_state[month_key] = m - 1
                st.rerun()
            elif action == "next_month":
                m = st.session_state[month_key]
                y = st.session_state[year_key]
                if m == 12:
                    st.session_state[month_key] = 1
                    st.session_state[year_key] = y + 1
                else:
                    st.session_state[month_key] = m + 1
                st.rerun()
            elif action == "select_day":
                st.session_state[day_key] = int(val)
                st.rerun()
            elif action == "select_duration":
                st.session_state[duration_key] = val
                st.rerun()
            elif action == "book_slot":
                month_lbl = get_month_name(st.session_state[month_key])
                date_str = f"{st.session_state[day_key]} {month_lbl.lower()} {st.session_state[year_key]}"
                st.session_state[booking_success_key] = (
                    f"Rendez-vous de **{st.session_state[duration_key]}** confirmé avec **{service['consultant']['name']}** "
                    f"le **{date_str}** à **{val}** ! Une confirmation a été envoyée à votre adresse email."
                )
                st.rerun()
            elif action == "view_resource":
                st.session_state[resource_msg_key] = f"Viewing asset **{val}**..."
                st.rerun()
            elif action == "download_resource":
                st.session_state[resource_msg_key] = f"Downloading asset **{val}**..."
                st.rerun()

    # 5. Render standard hidden submit button
    st.write('<div class="single-action-hidden">', unsafe_allow_html=True)
    st.button("submit", key="service_single_submit")
    st.write('</div>', unsafe_allow_html=True)

    # 6. Generate and render the pure premium HTML structure (zero-indented f-string)
    page_html = _generate_page_html(
        service=service,
        contacts_search=st.session_state[search_key],
        contacts_dept=st.session_state[dept_key],
        current_page=st.session_state[page_key],
        active_month=st.session_state[month_key],
        active_year=st.session_state[year_key],
        selected_day=st.session_state[day_key],
        selected_duration=st.session_state[duration_key],
    )
    st.markdown(page_html, unsafe_allow_html=True)
