# NEXUS Partner Mapping — Stack & Architecture Summary

**Repository:** `Partner-mapping-app` (standalone clone of the nexus monorepo `app/` folder)  
**Product:** Streamlit web application for partner deposit upload, review workflows, hub portal views, and admin tooling for NEXUS (automotive aftermarket).

---

## Core technology stack

| Layer | Technology |
|-------|------------|
| **Language** | Python 3.10+ recommended (3.11 / 3.12); runs on 3.9+ in practice |
| **Web framework** | [Streamlit](https://streamlit.io/) ≥ 1.32 (single-page app with dynamic page routing) |
| **Data manipulation** | [pandas](https://pandas.pydata.org/) ≥ 2.0 |
| **Charts** | [Plotly](https://plotly.com/python/) ≥ 5.20 |
| **Database (optional)** | [Snowflake](https://www.snowflake.com/) via `snowflake-connector-python` ≥ 3.10 |
| **Excel / CSV uploads** | [openpyxl](https://openpyxl.readthedocs.io/) ≥ 3.1, stdlib `csv` |
| **Configuration** | Environment variables + [python-dotenv](https://github.com/theskumar/python-dotenv) (`.env.migrate`) |
| **Authentication tokens** | [PyJWT](https://pyjwt.readthedocs.io/) ≥ 2.8 + [cryptography](https://cryptography.io/) |
| **HTTP (stdlib)** | `urllib.request` for HubSpot JWT mint Lambda |
| **Package management** | `pip` + `requirements.txt` |
| **Local runtime** | `streamlit run streamlit_app.py` → default **http://localhost:8501** |

There is **no separate frontend build** (no React/Vue/npm). UI is Python + Streamlit widgets, custom HTML/CSS via `st.html` / `theme/styles.py`, and Google Fonts (Inter).

---

## Python dependencies (`requirements.txt`)

| Package | Role in this app |
|---------|------------------|
| `streamlit` | App shell, routing, session state, file upload, UI |
| `pandas` | Tables, metrics, Snowflake query results |
| `plotly` | Dashboard / sales charts (legacy `partner_dashboard.py` and widgets) |
| `snowflake-connector-python` | Live queries to destination Snowflake (`PM_PROD` database) |
| `python-dotenv` | Load `SNOWFLAKE_DEST_*` from `.env.migrate` |
| `PyJWT` / `cryptography` | Parse HubSpot / minted JWTs (RS256 verification helper available) |
| `openpyxl` | Parse `.xlsx` partner declaration uploads |

**Transitive highlights** (installed with the above): NumPy, Altair (Streamlit charts), Requests, Boto3 (via Snowflake connector), Tornado (Streamlit server).

---

## External systems & integrations

| System | Usage | Configuration |
|--------|--------|-----------------|
| **HubSpot SSO** | Login redirect; iframe JWT via query param | `MOCK_SSO`, `SSO_LOGIN_URL` / `HUBSPOT_SSO_URL` |
| **HubSpot mint Lambda** | Dev JWT minting by company ID | `HUBSPOT_MINT_URL`, `HUBSPOT_COMPANY_ID` |
| **Snowflake** | Hub dashboard, declarations, review queue, QA views | `scripts/snowflake_migrate/.env.migrate` or app-root `.env.migrate` (`SNOWFLAKE_DEST_*`) |
| **AWS upload API** | Production file ingest (planned) | `UPLOAD_API_URL` (stub — not wired) |
| **Nexus marketing site** | “Create an account” on login | `CREATE_ACCOUNT_URL` |

**Snowflake target (default):** database `PM_PROD`, schemas such as `REF`, `STAGING`, `APP`, `QA`, `OUTPUT` (see `snowflake_client.py`, `migrate_ref.py`, data loaders).

---

## Application architecture

### Entry points

| File | Purpose |
|------|---------|
| `streamlit_app.py` | **Primary entry** — auth gate, sidebar nav, role-based page dispatch |
| `partner_dashboard.py` | Legacy Snowflake-focused dashboard prototype |

### Routing model

- Not Streamlit multipage `pages/` auto-discovery; **manual registry** in `streamlit_app.py` (`HUB_PAGES`, `PARTNER_MAPPING_PAGES`, `REVIEWER_PAGES`, `ADMIN_PAGES`).
- Active page stored in `st.session_state.active_page`; modules loaded via `importlib` (`pages.*`).

### Layered layout

```text
Partner-mapping-app/
├── streamlit_app.py          # Main entry, page registry
├── partner_dashboard.py      # Legacy dashboard entry
├── snowflake_client.py       # Snowflake connection + SQL helpers
├── dashboard_data.py         # Hub metrics from Snowflake / demo
├── constants.py              # Upload limits (250 MB)
├── requirements.txt
├── .streamlit/config.toml    # Theme, server, upload size
├── .env.example              # Snowflake migrate template (do not commit secrets)
│
├── auth/                     # Session, JWT, HubSpot bridge, Snowflake scoping
├── pages/                    # UI screens by role
│   ├── auth/                 # SSO Connection login
│   ├── partner/              # Upload, history, dashboard, corrective
│   ├── internal/             # Review queue, bulk review, overlap, discrepancy
│   ├── portal/               # Hub dashboard, directory stubs
│   └── admin/                # Calibration, onboarding, closure stubs
├── services/                 # Business logic (BRD state, upload pipeline, review)
├── data/                     # Loaders: Snowflake queries + demo fixtures
├── widgets/                  # Reusable dashboard components (KPI, charts, hero)
├── theme/                    # Design tokens, global CSS, sidebar layout, assets paths
├── content_policies/         # Role-based hub dashboard visibility rules
├── scripts/snowflake_migrate/  # migrate_ref.py (DB constants, session activation)
└── assets/images/            # Static images (e.g. logo.jpg for login)
```

### UI / design system

- **`theme/tokens.py`** — NEXUS colors (orange `#F58220`, sidebar `#1C1C1E`, etc.).
- **`theme/styles.py`** — Global CSS injection (Inter font, sidebar, cards).
- **`theme/layout.py`** — Sidebar branding, nav, dev persona / role switcher.
- **`theme/html_utils.py`** — `render_html()` wrapper around `st.html`.
- **`theme/paths.py`** — `assets/images/` path helper.
- **`.streamlit/config.toml`** — Streamlit theme aligned with NEXUS brand; `maxUploadSize = 250` MB.

---

## Runtime modes

### Demo mode (default)

- **`MOCK_SSO=true`** — mock sign-in on localhost without HubSpot redirect.
- **`services/brd_state.py`** — in-memory deposits, partners, review state (`st.session_state`).
- **`data/demo_fixtures.py`** — fallback data when Snowflake is off or connection fails.
- **Dev persona switcher** — sidebar toggles supplier / member / reviewer / admin views.

### Live / integrated mode

- Set **`MOCK_SSO=false`** and real SSO URLs for production login.
- Enable Snowflake via session flag **`use_snowflake`** and valid **`.env.migrate`** credentials.
- Optional **`UPLOAD_API_URL`** for AWS Lambda ingestion (client stub present).
- **`jwt` query parameter** — pre-auth when embedded in HubSpot iframe.

---

## Authentication & authorization

| Component | Responsibility |
|-----------|----------------|
| `pages/auth/connection.py` | Login card, SSO button, create-account link |
| `auth/session.py` | `UserSession`, mock company map, role helpers (`is_partner`, `is_reviewer`, `is_admin`) |
| `auth/hubspot_bridge.py` | JWT from query string; optional mint Lambda call |
| `auth/jwt_utils.py` | Unverified / RS256 JWT decode |
| `auth/snowflake_session.py` | Role-scoped Snowflake connection; partner row filters |

**Roles:** partner (supplier/member hub + mapping), internal reviewer, admin.

---

## Data & file processing

| Area | Implementation |
|------|----------------|
| **Uploads** | `pages/partner/upload.py` → `services/upload_client.py` → `services/processing_pipeline.py` |
| **Parsing** | `services/file_parser.py` — CSV (encoding detection), Excel via pandas/openpyxl |
| **Review** | `services/review_service.py`, `pages/internal/*` |
| **Snowflake reads** | `data/declarations.py`, `dashboard_metrics.py`, `hub_dashboard_loader.py`, etc. |
| **Charts** | `widgets/sales_charts.py` (Plotly), KPI / ranking widgets |

---

## Streamlit configuration (`.streamlit/config.toml`)

- **Theme:** NEXUS orange primary, light gray page background, sans-serif font.
- **Server:** headless, XSRF protection, **250 MB** max upload.
- **Browser:** usage stats disabled.
- **Client:** minimal toolbar, expanded sidebar by default.

---

## Assets & static files

- **Recommended path:** `assets/images/` (brand logos, UI art).
- **Helper:** `theme/paths.py` → `image_path("logo.jpg")`.
- **Optional:** Streamlit `static/` folder + `server.enableStaticServing` for URL-based static assets (not required for current login implementation).

---

## Testing & quality

- **Unit tests** for BRD services live in the **parent nexus repo** (`pytest tests/test_brd_services.py`), not in this standalone tree.
- No dedicated CI config in this repo root from the current scan.

---

## Quick reference — run locally

```bash
python -m venv .venv
.venv/Scripts/activate          # Windows
pip install -r requirements.txt
streamlit run streamlit_app.py
```

See **README.md** for environment variables, Snowflake setup, and troubleshooting.

---

## Summary

**NEXUS Partner Mapping** is a **Python + Streamlit** line-of-business app with optional **Snowflake** analytics, **HubSpot**-centric auth, and an in-app **demo mode** for local development. Presentation is code-first (no JS framework); business rules sit in `services/`, I/O in `data/`, and screens in `pages/` and `widgets/`.
