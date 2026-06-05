# HubSpot Integration Guide for Login

This document explains what to configure on the **HubSpot side** so the Streamlit app can authenticate users through HubSpot.

## Target Architecture

- User opens a HubSpot page (or private app page) that embeds this Streamlit app.
- HubSpot context identifies the company/contact.
- A backend mint endpoint creates a short-lived JWT for the app.
- Streamlit receives token as `jwt` query param and builds session from claims.

## 1) Required JWT Contract (must match app expectations)

The app currently reads these claims:

- `sub` (**required**): internal partner key (e.g. `MEYLE`, `NISSENS`)
- `type` (**required**): `supplier` or `member`
- `role` (optional): fallback is `PM_PARTNER_<sub>`
- `is_active` (optional): default `true`
- `default_currency` (optional): default `EUR`
- `exp` (**required**): unix timestamp expiry

Recommended extras:

- `iat`, `iss`, `aud`, `hubspot_company_id`, `hubspot_contact_id`

## 2) HubSpot-side prerequisites

- A HubSpot property that maps to your internal partner identifier:
  - Example: Company property `nexus_partner_key`
- Optional company property for declarant type:
  - Example: `nexus_declarant_type` with values `supplier` / `member`
- Optional company property for default currency:
  - Example: `nexus_default_currency`
- Optional company property for activation:
  - Example: `nexus_is_active`

## 3) Build/Deploy a JWT Mint Backend

HubSpot should **not** sign tokens directly in page JS.  
Use a secure backend (Lambda/Cloud Run/etc.) with private signing key.

Endpoint contract used by this app:

- URL stored in env `HUBSPOT_MINT_URL`
- Method: `POST`
- JSON body:

```json
{
  "hubspot_company_id": "123456789"
}
```

- JSON response:

```json
{
  "token": "<jwt>"
}
```

Security requirements:

- Sign with strong secret/private key
- TTL 5–15 minutes
- Validate caller (HubSpot origin, signed request, API key, or mTLS)
- Log mint events with company/contact IDs

## 4) HubSpot page setup

Use a HubSpot page/module that embeds Streamlit and appends the JWT:

1. Resolve current company/contact context in HubSpot
2. Call your mint backend with `hubspot_company_id`
3. Build iframe URL:
   - `https://<your-streamlit-host>/?jwt=<token>`
4. Render iframe

Important:

- Always URL-encode JWT
- Refresh token before expiry if session is long-lived
- Do not expose signing key in HubSpot frontend code

## 4.1) HubSpot App OAuth callback URL

Set this in your HubSpot app OAuth settings:

- `http://localhost:8505/auth/hubspot/callback` (local dev)

**Important:** Streamlit only runs `streamlit_app.py` at `/`. The callback path does not load the app by itself.

Use the local launcher:

```bash
python run_app.py
```

This starts:

- Streamlit on `http://localhost:8505/`
- A redirect proxy on `http://localhost:8505/` that forwards
  `/auth/hubspot/callback?code=...&state=...` → `http://localhost:8505/?code=...&state=...`

Open the app via **`http://localhost:8505/`** (proxy).

When HubSpot redirects to the callback URL, the app will:

1. Exchange `code` for an access token
2. Read token metadata (user/hub/app)
3. Show a callback result screen with user details
4. Wait for user to click **Continue** (black button)
5. Navigate to Dashboard and keep login in session for the browser session

## 5) Environment variables in Streamlit app

Configure these where Streamlit runs:

- `HUBSPOT_MINT_URL` (required for mint fallback/dev mint)
- `HUBSPOT_COMPANY_ID` (optional local dev only)
- `MOCK_SSO=false` for real SSO behavior
- `SSO_LOGIN_URL` / `HUBSPOT_SSO_URL` as needed

## 6) Validation Checklist

- [ ] HubSpot page can resolve `hubspot_company_id`
- [ ] Mint endpoint returns JWT with required claims
- [ ] Streamlit opens authenticated when `?jwt=...` is present
- [ ] Correct role/type/partner mapping in sidebar and pages
- [ ] Disabled partners (`is_active=false`) are blocked
- [ ] Expired JWT shows session-expired message

## 7) Troubleshooting

- **“Invalid authentication token”**: malformed JWT or missing required claims
- **“Session expired”**: `exp` too short or token stale before iframe load
- **Wrong partner data**: `sub` does not match internal partner key mapping
- **Mint fails**: verify `HUBSPOT_MINT_URL`, backend auth, and CORS/network path

