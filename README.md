# NEXUS Partner Mapping (Streamlit)

Streamlit web app for partner deposit upload, review workflows, hub portal views, and admin tooling. By default it runs in **demo mode** (in-memory BRD state, mock SSO). Optional Snowflake connectivity uses credentials from the parent repository.

## Prerequisites

- **Python 3.10+** (3.11 or 3.12 recommended)
- **Git** access to this repository
- For live Snowflake dashboards: a Snowflake destination account and the parent repo’s `scripts/snowflake_migrate/` setup (see below)

## Quick start (localhost)

Run all commands from the **`app/`** directory.

### 1. Clone and enter the app

If you have the full **nexus** monorepo:

```bash
cd /path/to/nexus/app
```

If you only have the `app` subfolder as its own repo, clone that repo and `cd` into it. Demo mode works without the parent repo; Snowflake features need the full tree (see [Optional: Snowflake](#optional-snowflake)).

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

You can also reuse a venv at the repo root (e.g. `source ../venv/bin/activate`).

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Start the app

```bash
streamlit run streamlit_app.py
```

Streamlit prints a local URL (typically **http://localhost:8501**). Open it in your browser.

### 5. Sign in and explore

1. On the **Connection** screen, click **Sign in with SSO**.
2. With default settings (`MOCK_SSO=true`), you are signed in without leaving localhost.
3. Use the sidebar **Dev persona** to switch between supplier, member, reviewer, and admin views.
4. Use **Upload** with sample Excel files from the parent folder `data smaples/` (if present in your clone).

## Environment variables (optional)

Nothing is required for a basic local run. Set these only when integrating with real services.

| Variable | Default | Purpose |
|----------|---------|---------|
| `MOCK_SSO` | `true` | When `true`, mock sign-in on localhost without HubSpot redirect |
| `SSO_LOGIN_URL` / `HUBSPOT_SSO_URL` | HubSpot login URL | Real SSO redirect when `MOCK_SSO=false` |
| `CREATE_ACCOUNT_URL` | Nexus marketing site | “Create an account” link on Connection screen |
| `HUBSPOT_MINT_URL` | (empty) | URL of `hubspot-mint` Lambda for JWT in dev |
| `HUBSPOT_COMPANY_ID` | (empty) | Company ID to mint a JWT on load (dev) |
| `UPLOAD_API_URL` | (empty) | AWS upload-ingest API; empty uses in-app demo flow |
| `jwt` query param | — | Pre-authenticated session when embedded in HubSpot iframe |

Example for real SSO (not typical on first setup):

```bash
export MOCK_SSO=false
export SSO_LOGIN_URL="https://your-idp.example/login"
streamlit run streamlit_app.py
```

Do not commit passwords or API keys. Use your shell environment or a local `.env` file that is gitignored.

## Optional: Snowflake

Some hub / dashboard paths read from Snowflake via `snowflake_client.py`. Credentials are loaded from:

```text
../scripts/snowflake_migrate/.env.migrate
```

From the **nexus** repo root:

```bash
cp scripts/snowflake_migrate/.env.migrate.example scripts/snowflake_migrate/.env.migrate
# Edit .env.migrate with SNOWFLAKE_DEST_* values (never commit this file)
```

Required keys in `.env.migrate`:

- `SNOWFLAKE_DEST_ACCOUNT`
- `SNOWFLAKE_DEST_USER`
- `SNOWFLAKE_DEST_PASSWORD`

Optional: `SNOWFLAKE_DEST_ROLE`, `SNOWFLAKE_DEST_WAREHOUSE`, `SNOWFLAKE_DEST_PASSCODE` (MFA).

Legacy standalone dashboard (Snowflake-focused UI):

```bash
streamlit run partner_dashboard.py
```

## Project layout

```text
app/
├── streamlit_app.py      # Main entry — use this for local dev
├── partner_dashboard.py  # Legacy Snowflake dashboard entry
├── requirements.txt
├── .streamlit/config.toml
├── auth/                 # Session, JWT, HubSpot bridge
├── pages/                # Partner, internal reviewer, admin, portal
├── services/             # Upload, review, closure, BRD state
├── data/                 # Loaders, fixtures, demo data
├── theme/                # Layout, styles, design tokens
└── widgets/              # Shared UI components
```

## Running tests

BRD service tests live in the parent repo. From **nexus** root with dev dependencies installed:

```bash
pip install -r requirements-dev.txt
pytest tests/test_brd_services.py -v
```

## Troubleshooting

| Issue | What to try |
|-------|-------------|
| `command not found: streamlit` | Activate the venv and run `pip install -r requirements.txt` again |
| Port 8501 in use | `streamlit run streamlit_app.py --server.port 8502` |
| Stuck on Connection after SSO click | Ensure `MOCK_SSO` is not set to `false` unless real SSO is configured |
| Snowflake connection errors | Confirm `scripts/snowflake_migrate/.env.migrate` exists and paths assume full nexus repo layout |
| Large Excel upload fails | Max upload is **250 MB** (see `.streamlit/config.toml`) |

## Related docs

- Repo-wide checklist: `../NEXT_STEPS.md`
- Snowflake migration: `../scripts/snowflake_migrate/`
