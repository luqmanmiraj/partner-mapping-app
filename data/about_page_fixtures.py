"""Demo content for the About portal page."""

from __future__ import annotations

from typing import Any

COVER_PROFILE: dict[str, Any] = {
    "name": "NEXUS Automotive",
    "banner_headline": "COMMITED TOGETHER.",
    "banner_highlight": "THE FUTURE IS OURS.",
    "headquarters": "164 Av. Jean Jaurès, 69007 Lyon",
    "website_label": "www.nexusautomotiveinternational.eu",
    "website_url": "https://www.nexusautomotiveinternational.eu",
    "social_links": [
        ("Instagram", "#"),
        ("LinkedIn", "#"),
        ("Facebook", "#"),
        ("X (Twitter)", "#"),
    ],
}

INTRO_PARAGRAPHS: list[str] = [
    (
        "NEXUS is the leading global automotive aftermarket community. With more than "
        "<span class=\"nexus-about-about__highlight\">637 distributor</span> members, "
        "<span class=\"nexus-about-about__highlight\">4,103 WDs</span> and "
        "<span class=\"nexus-about-about__highlight\">9,953 retail stores</span> affiliated in "
        "<span class=\"nexus-about-about__highlight\">146 countries</span>, allied with 90+ global "
        "manufacturers suppliers, NEXUS is a growth accelerator for its community."
    ),
    (
        "Established in 2014 by CEO Gaël Escribe, NEXUS Automotive International, the leading "
        "automotive aftermarket (AA) global community, is shaping the future of the AA."
    ),
]

PILLARS: list[dict[str, str]] = [
    {
        "title": "Intermediation",
        "description": (
            "Connect directly with the world's leading OEMs. We manage framework agreements "
            "to streamline your business."
        ),
    },
    {
        "title": "Intermediation",
        "description": (
            "Connect directly with the world's leading OEMs. We manage framework agreements "
            "to streamline your business."
        ),
    },
    {
        "title": "Intermediation",
        "description": (
            "Connect directly with the world's leading OEMs. We manage framework agreements "
            "to streamline your business."
        ),
    },
]

PILLARS_FEATURE: dict[str, Any] = {
    "title": "Lorem ipsum",
    "description": (
        "Thanks to an entrepreneurial, innovative and agile mindset, N! disrupts the industry "
        "bringing innovative solutions for a more sustainable, digital and connected mobility. "
        "At the same time, it supports its community of more than "
        "<span class=\"nexus-about-pillars__highlight\">637 members</span> in "
        "<span class=\"nexus-about-pillars__highlight\">146 countries</span>, allied with more than "
        "<span class=\"nexus-about-pillars__highlight\">90 global suppliers</span>, by providing "
        "services to accelerate their growth."
    ),
    "items": [
        {
            "title": "Lorem ipsum",
            "description": (
                "N! is offering new approaches and new ideas for a connected, global and "
                "consolidated world of tomorrow to accelerate the success of car and heavy duty "
                "spare parts and services distributors and manufacturers, through 16 regional "
                "structures that connect them."
            ),
        },
        {
            "title": "Lorem ipsum",
            "description": "NEXUS' consolidated turnover was more than 54 billion euros in 2025.",
        },
    ],
}

BRAND_FILES: list[dict[str, str]] = [
    {"name": "Brand Guidelines.pdf...", "size": "2 MB"},
    {"name": "Logotype.zip", "size": "2 MB"},
    {"name": "Other", "size": "2 MB"},
    {"name": "Brand Guidelines.pdf...", "size": "2 MB"},
    {"name": "Logotype.zip", "size": "2 MB"},
    {"name": "Other", "size": "2 MB"},
    {"name": "Brand Guidelines.pdf...", "size": "2 MB"},
    {"name": "Logotype.zip", "size": "2 MB"},
    {"name": "Brand Guidelines.pdf...", "size": "2 MB"},
]
