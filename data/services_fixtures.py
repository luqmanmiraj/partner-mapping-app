"""Mock data for the Services Catalog and Single Service Details views."""

from __future__ import annotations

from typing import Any

SERVICES_LIST: list[dict[str, Any]] = [
    {
        "id": "marketing",
        "title": "Marketing",
        "description": "Request customized point-of-sale materials, digital assets, or local campaign support for your regional network",
        "detailed_description": (
            "Our Marketing Service empowers Nexus members to amplify their regional presence and leverage brand assets "
            "effectively. From co-branded digital campaigns to physical point-of-sale materials, we provide comprehensive "
            "media design and visual strategy consulting."
        ),
        "expertise_title": "Expertise & Product Ranges",
        "expertise_desc": (
            "We specialize in international automotive aftermarket marketing, regional communication strategy, and "
            "collaborative co-marketing platforms. Our team ensures your local efforts align with global standards "
            "while delivering hyper-localized relevance."
        ),
        "checklist": [
            "Co-branded physical and digital point-of-sale banners.",
            "Local social media media assets and tailored campaign calendars.",
            "Visual consulting, typography sheets, and brand guide integration.",
            "Event-mapping collateral and regional workshop sponsorships."
        ],
        "resources": [
            {"name": "Marketing_Playbook_2026.pdf", "size": "4.2 MB"},
            {"name": "Co_Branding_Guidelines.pdf", "size": "1.8 MB"},
            {"name": "Digital_Asset_Pack_v2.zip", "size": "15.5 MB"},
            {"name": "POS_Catalog_PrintReady.pdf", "size": "8.9 MB"},
            {"name": "Regional_Campaign_Templates.docx", "size": "1.2 MB"},
            {"name": "Social_Media_Specs_Sheet.pdf", "size": "650 KB"}
        ],
        "contacts": [
            {
                "name": "Jean Dupont",
                "position": "Director of Communications",
                "region": "Europe",
                "email": "jean.dupont@nexus.com",
                "phone": "+33 6 12 34 56 78",
                "department": "Creative"
            },
            {
                "name": "Agnès Martinez",
                "position": "Lead Brand Consultant",
                "region": "Global",
                "email": "agnes.martinez@nexus.com",
                "phone": "+33 6 98 76 54 32",
                "department": "Consulting"
            },
            {
                "name": "Marie Laurent",
                "position": "POS Strategy Manager",
                "region": "Western Europe",
                "email": "marie.laurent@nexus.com",
                "phone": "+33 6 45 67 89 01",
                "department": "Operations"
            },
            {
                "name": "David Smith",
                "position": "Digital Outreach Coordinator",
                "region": "North America",
                "email": "david.smith@nexus.com",
                "phone": "+1 415 555 2671",
                "department": "Operations"
            },
            {
                "name": "Sophia Chen",
                "position": "APAC Marketing Advisor",
                "region": "Asia-Pacific",
                "email": "sophia.chen@nexus.com",
                "phone": "+65 6712 9012",
                "department": "Consulting"
            },
            {
                "name": "Carlos Gomez",
                "position": "LatAm Media Lead",
                "region": "Latin America",
                "email": "carlos.gomez@nexus.com",
                "phone": "+52 55 1234 5678",
                "department": "Creative"
            }
        ],
        "consultant": {
            "name": "Agnès Martinez",
            "avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=120&q=80"
        },
        "available_durations": ["15 min", "30 min", "1 heure"],
        "available_slots": ["09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "14:00", "14:30", "15:00"]
    },
    {
        "id": "supply_chain",
        "title": "Supply Chain & Logistics",
        "description": "Optimize your shipping pathways, warehouse processes, global shipping container bookings, and supply chain visibility.",
        "detailed_description": (
            "Logistical efficiency is the backbone of automotive distribution. Our Supply Chain & Logistics team "
            "helps Nexus partners minimize transit overheads, establish robust automated tracking, and source optimal shipping routes."
        ),
        "expertise_title": "Logistics Systems & Pathways",
        "expertise_desc": (
            "We offer guidance on shipping consolidation, customs clearance protocols, automated inventory management, "
            "and carbon-efficient transport networks."
        ),
        "checklist": [
            "Optimized multimodal shipping routes and vendor selection.",
            "Consolidated warehouse allocation analysis.",
            "Customs compliance checkups and EDI pipeline audits.",
            "IoT container tracking integration options."
        ],
        "resources": [
            {"name": "Logistics_Consolidation_Guide.pdf", "size": "3.5 MB"},
            {"name": "Customs_Quick_Reference_Sheet.pdf", "size": "1.1 MB"},
            {"name": "Transit_Time_Matrix_Excel.xlsx", "size": "2.4 MB"}
        ],
        "contacts": [
            {
                "name": "Marcus Vance",
                "position": "Director of Global Supply",
                "region": "Global",
                "email": "marcus.vance@nexus.com",
                "phone": "+44 20 7946 0192",
                "department": "Supply Chain"
            },
            {
                "name": "Helena Rostova",
                "position": "Logistics Network Designer",
                "region": "Europe",
                "email": "helena.rostova@nexus.com",
                "phone": "+49 89 2435 6789",
                "department": "Consulting"
            },
            {
                "name": "Kenji Tanaka",
                "position": "APAC Shipping Liaison",
                "region": "Asia-Pacific",
                "email": "kenji.tanaka@nexus.com",
                "phone": "+81 3 5555 8901",
                "department": "Operations"
            }
        ],
        "consultant": {
            "name": "Helena Rostova",
            "avatar": "https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&w=120&q=80"
        },
        "available_durations": ["30 min", "1 heure"],
        "available_slots": ["10:00", "11:00", "13:30", "14:30", "15:30"]
    },
    {
        "id": "tech_integration",
        "title": "Tech & Systems Integration",
        "description": "Deploy corporate systems, Snowflake data bridges, ERP connectors, and secure partner mapping pipelines.",
        "detailed_description": (
            "Empower your business operations with seamless digital tools. Our Tech Integration team aids partners "
            "in configuring Snowflake database pipelines, setting up HubSpot API triggers, and securing data exchanges."
        ),
        "expertise_title": "Integrations & Secure Pipelines",
        "expertise_desc": (
            "We design, build, and audit high-throughput data connections between automotive warehouse software, "
            "client ERP platforms, and central telemetry databases."
        ),
        "checklist": [
            "Snowflake database syncing and credential setup.",
            "HubSpot connection templates and auto-sync triggers.",
            "Secure inventory API endpoints (REST & gRPC).",
            "SSO and JWT token authorization structures."
        ],
        "resources": [
            {"name": "Snowflake_Bridge_Quickstart.pdf", "size": "5.1 MB"},
            {"name": "API_Endpoints_Specifications.json", "size": "800 KB"},
            {"name": "Security_and_JWT_Whitepaper.pdf", "size": "2.2 MB"}
        ],
        "contacts": [
            {
                "name": "Linus Sterling",
                "position": "Chief Systems Architect",
                "region": "Global",
                "email": "linus.sterling@nexus.com",
                "phone": "+1 650 555 0199",
                "department": "Engineering"
            },
            {
                "name": "Fatima Al-Sudairi",
                "position": "Lead Integration Engineer",
                "region": "Middle East & Europe",
                "email": "fatima.alsudairi@nexus.com",
                "phone": "+971 4 368 0000",
                "department": "Engineering"
            },
            {
                "name": "Sarah Miller",
                "position": "Technical Onboarding Specialist",
                "region": "North America",
                "email": "sarah.miller@nexus.com",
                "phone": "+1 415 555 8922",
                "department": "Support"
            }
        ],
        "consultant": {
            "name": "Sarah Miller",
            "avatar": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=120&q=80"
        },
        "available_durations": ["15 min", "30 min"],
        "available_slots": ["09:00", "09:30", "14:00", "14:30", "16:00"]
    },
    {
        "id": "sourcing",
        "title": "Sourcing & Procurement",
        "description": "Get access to exclusive global automotive supplier partnerships, contract templates, pricing books, and group ordering benefits.",
        "detailed_description": (
            "Leverage the collective bargaining power of the global Nexus network. Our Sourcing & Procurement program "
            "coordinates purchasing structures, pre-negotiated OEM pricing sheets, and supplier compliance standards."
        ),
        "expertise_title": "Sourcing Agreements & Volume Pricing",
        "expertise_desc": (
            "We offer direct support in finding and auditing regional replacement part suppliers, negotiating group purchasing "
            "contracts, and utilizing unified volume discount sheets."
        ),
        "checklist": [
            "Negotiated pricing templates for OEM replacement ranges.",
            "Group purchasing volume-aggregated discount structures.",
            "Supplier audit protocols and checklist criteria.",
            "Pre-vetted vendor portfolios by category."
        ],
        "resources": [
            {"name": "Supplier_Pricing_Schedules_2026.pdf", "size": "8.4 MB"},
            {"name": "Vendor_Compliance_Audit_Form.pdf", "size": "1.3 MB"},
            {"name": "Standard_Procurement_Contract_v4.docx", "size": "2.1 MB"}
        ],
        "contacts": [
            {
                "name": "Gérard Dubois",
                "position": "VP of Global Sourcing",
                "region": "Europe",
                "email": "gerard.dubois@nexus.com",
                "phone": "+33 1 76 54 32 10",
                "department": "Sourcing"
            },
            {
                "name": "Anita Desai",
                "position": "Supplier Integrity Auditor",
                "region": "APAC & India",
                "email": "anita.desai@nexus.com",
                "phone": "+91 22 2282 8990",
                "department": "Compliance"
            },
            {
                "name": "Göran Nyström",
                "position": "Procurement Specialist",
                "region": "Northern Europe",
                "email": "goran.nystrom@nexus.com",
                "phone": "+46 8 505 5600",
                "department": "Sourcing"
            }
        ],
        "consultant": {
            "name": "Gérard Dubois",
            "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=120&q=80"
        },
        "available_durations": ["30 min", "1 heure"],
        "available_slots": ["09:30", "11:30", "15:00", "16:00"]
    }
]


def get_service(service_id: str) -> dict[str, Any] | None:
    for service in SERVICES_LIST:
        if service["id"] == service_id:
            return service
    return None
