"""Demo content for the My Company portal page."""

from __future__ import annotations

from typing import Any

OVERVIEW: dict[str, Any] = {
    "company_name": "Bosch Automotive",
    "logo_text": "BOSCH",
    "activity": "Manufacturer",
    "products": ["Injection", "Batteries", "Wipers"],
    "email": "contact@bosch.com",
    "headquarters": "164 Av. Jean Jaurès, 69007 Lyon",
    "website_label": "www.bosch-automotive.com",
    "website_url": "https://www.bosch-automotive.com",
    "phone": "+ 33 01 02 03 04",
    "social_links": [
        ("Instagram", "#"),
        ("LinkedIn", "#"),
        ("Facebook", "#"),
        ("X (Twitter)", "#"),
    ],
}

ABOUT_TAB: dict[str, Any] = {
    "description": (
        "Global leader in automotive technology and services. We provide innovative "
        "solutions for connected, automated, and electrified mobility. Our expertise "
        "covers braking systems, steering, and engine management solutions."
    ),
    "product_ranges": ["Injection", "Batteries", "Wipers"],
    "offers": [
        {
            "state": "active",
            "tagline": "Flash Offer",
            "title": "-15% on e-Mobility Battery ranges.",
            "duration": "Valid for all orders placed before March 15, 2025.",
            "cta": "Get offer now !",
        },
        {
            "state": "pending",
            "tagline": "Flash Offer",
            "title": "-15% on e-Mobility Battery ranges.",
            "duration": "Valid for all orders placed before March 15, 2025.",
            "cta": "Get offer now !",
        },
    ],
}

CONTACTS: list[dict[str, str]] = [
    {
        "name": "Jean Dupont",
        "position": "Regional Director",
        "segment": "Aftermarket",
        "region": "Europe",
        "email": "jean.dupont@bosch.com",
        "avatar": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=facearea&facepad=2&w=256&h=256&q=80",
    },
] * 9

NEWS_FEATURED: dict[str, str] = {
    "date": "Last Month",
    "title": "Title",
    "summary": "Vestibulum condimentum lectus mauris, eget iaculis sem tristique non.",
}

NEWS_SIDEBAR: list[dict[str, str]] = [
    {
        "date": "Last Month",
        "title": "Title",
        "summary": "Vestibulum condimentum lectus mauris, eget iaculis sem tristique non.",
        "image": "sidebar-1",
    },
    {
        "date": "Last Month",
        "title": "Title",
        "summary": "Vestibulum condimentum lectus mauris, eget iaculis sem tristique non.",
        "image": "sidebar-2",
    },
]

DOCUMENTS: list[dict[str, str]] = [
    {"name": "Title.pdf", "size": "2 MB"},
    {"name": "Title.pdf", "size": "2 MB"},
    {"name": "Title.pdf", "size": "2 MB"},
]

MEDIA_ITEMS: list[dict[str, str]] = [
    {
        "title": "Title",
        "summary": "Vestibulum condimentum lectus mauris, eget iaculis sem tristique non.",
        "kind": "video",
    },
] * 3

GALLERY_ITEMS: list[dict[str, str]] = [
    {
        "title": "Title",
        "summary": "Vestibulum condimentum lectus mauris, eget iaculis sem tristique non.",
    },
] * 3
