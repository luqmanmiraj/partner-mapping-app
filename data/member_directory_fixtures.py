"""Demo data for the Member Directory page."""

from __future__ import annotations

from typing import Any

DEMO_COMPANIES: list[dict[str, Any]] = [
    {
        "id": "feu-vert-1",
        "name": "Feu Vert",
        "location": "France",
        "badge": "affiliate",
        "parent_company": "Nexus Group",
        "activity": "Manufacturer",
        "products": ["Injection", "Batteries", "Wipers"],
        "email": "contact@feuvert.com",
        "headquarters": "164 Av. Jean Jaurès, 69007 Lyon",
        "website": "www.feuvert.fr",
        "phone": "+ 33 01 02 03 04",
        "about": (
            "Global leader in automotive technology and services. We provide innovative "
            "solutions for connected, automated, and electrified mobility. Our expertise "
            "covers braking systems, steering, and engine management solutions."
        ),
        "contacts": [
            {
                "name": "Marie Dupont",
                "position": "Regional Director",
                "region": "Europe",
                "email": "marie.dupont@feuvert.com",
            },
            {
                "name": "Jean Martin",
                "position": "Sales Manager",
                "region": "France",
                "email": "jean.martin@feuvert.com",
            },
            {
                "name": "Sophie Laurent",
                "position": "Partnerships Lead",
                "region": "Western Europe",
                "email": "sophie.laurent@feuvert.com",
            },
        ],
        "sub_members": [
            {"name": "Feu Vert Lyon", "location": "Lyon, France"},
            {"name": "Feu Vert Paris", "location": "Paris, France"},
            {"name": "Feu Vert Marseille", "location": "Marseille, France"},
            {"name": "Feu Vert Bordeaux", "location": "Bordeaux, France"},
        ],
    },
    {
        "id": "feu-vert-2",
        "name": "Feu Vert",
        "location": "France",
        "badge": "affiliate",
        "parent_company": "Nexus Group",
        "activity": "Manufacturer",
        "products": ["Injection", "Batteries", "Wipers"],
        "email": "contact@feuvert.com",
        "headquarters": "164 Av. Jean Jaurès, 69007 Lyon",
        "website": "www.feuvert.fr",
        "phone": "+ 33 01 02 03 04",
        "about": (
            "Global leader in automotive technology and services. We provide innovative "
            "solutions for connected, automated, and electrified mobility."
        ),
        "contacts": [
            {
                "name": "Marie Dupont",
                "position": "Regional Director",
                "region": "Europe",
                "email": "marie.dupont@feuvert.com",
            },
            {
                "name": "Jean Martin",
                "position": "Sales Manager",
                "region": "France",
                "email": "jean.martin@feuvert.com",
            },
            {
                "name": "Sophie Laurent",
                "position": "Partnerships Lead",
                "region": "Western Europe",
                "email": "sophie.laurent@feuvert.com",
            },
        ],
        "sub_members": [
            {"name": "Feu Vert Lyon", "location": "Lyon, France"},
            {"name": "Feu Vert Paris", "location": "Paris, France"},
        ],
    },
    {
        "id": "feu-vert-3",
        "name": "Feu Vert",
        "location": "France",
        "badge": "affiliate",
        "parent_company": "Nexus Group",
        "activity": "Manufacturer",
        "products": ["Injection", "Batteries", "Wipers"],
        "email": "contact@feuvert.com",
        "headquarters": "164 Av. Jean Jaurès, 69007 Lyon",
        "website": "www.feuvert.fr",
        "phone": "+ 33 01 02 03 04",
        "about": (
            "Global leader in automotive technology and services. We provide innovative "
            "solutions for connected, automated, and electrified mobility."
        ),
        "contacts": [
            {
                "name": "Marie Dupont",
                "position": "Regional Director",
                "region": "Europe",
                "email": "marie.dupont@feuvert.com",
            },
            {
                "name": "Jean Martin",
                "position": "Sales Manager",
                "region": "France",
                "email": "jean.martin@feuvert.com",
            },
            {
                "name": "Sophie Laurent",
                "position": "Partnerships Lead",
                "region": "Western Europe",
                "email": "sophie.laurent@feuvert.com",
            },
        ],
        "sub_members": [
            {"name": "Feu Vert Lyon", "location": "Lyon, France"},
        ],
    },
    {
        "id": "feu-vert-member-1",
        "name": "Feu Vert",
        "location": "France",
        "badge": "member",
        "parent_company": "",
        "activity": "Manufacturer",
        "products": ["Injection", "Batteries", "Wipers"],
        "email": "contact@feuvert.com",
        "headquarters": "164 Av. Jean Jaurès, 69007 Lyon",
        "website": "www.feuvert.fr",
        "phone": "+ 33 01 02 03 04",
        "about": (
            "Global leader in automotive technology and services. We provide innovative "
            "solutions for connected, automated, and electrified mobility. Our expertise "
            "covers braking systems, steering, and engine management solutions."
        ),
        "contacts": [
            {
                "name": "Marie Dupont",
                "position": "Regional Director",
                "region": "Europe",
                "email": "marie.dupont@feuvert.com",
            },
            {
                "name": "Jean Martin",
                "position": "Sales Manager",
                "region": "France",
                "email": "jean.martin@feuvert.com",
            },
            {
                "name": "Sophie Laurent",
                "position": "Partnerships Lead",
                "region": "Western Europe",
                "email": "sophie.laurent@feuvert.com",
            },
        ],
        "sub_members": [
            {"name": "Feu Vert Lyon", "location": "Lyon, France"},
            {"name": "Feu Vert Paris", "location": "Paris, France"},
        ],
    },
    {
        "id": "feu-vert-member-2",
        "name": "Feu Vert",
        "location": "France",
        "badge": "member",
        "parent_company": "",
        "activity": "Manufacturer",
        "products": ["Injection", "Batteries", "Wipers"],
        "email": "contact@feuvert.com",
        "headquarters": "164 Av. Jean Jaurès, 69007 Lyon",
        "website": "www.feuvert.fr",
        "phone": "+ 33 01 02 03 04",
        "about": (
            "Global leader in automotive technology and services. We provide innovative "
            "solutions for connected, automated, and electrified mobility."
        ),
        "contacts": [
            {
                "name": "Marie Dupont",
                "position": "Regional Director",
                "region": "Europe",
                "email": "marie.dupont@feuvert.com",
            },
            {
                "name": "Jean Martin",
                "position": "Sales Manager",
                "region": "France",
                "email": "jean.martin@feuvert.com",
            },
            {
                "name": "Sophie Laurent",
                "position": "Partnerships Lead",
                "region": "Western Europe",
                "email": "sophie.laurent@feuvert.com",
            },
        ],
        "sub_members": [
            {"name": "Feu Vert Lyon", "location": "Lyon, France"},
        ],
    },
]


def get_company(company_id: str) -> dict[str, Any] | None:
    for company in DEMO_COMPANIES:
        if company["id"] == company_id:
            return company
    return None
