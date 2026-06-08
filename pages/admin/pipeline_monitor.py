"""Admin — BRD pipeline step monitor (upload → notification)."""

from __future__ import annotations

import streamlit as st

from auth.snowflake_session import scoped_connection
from services.pipeline_log import BRD_PIPELINE_STEPS, list_pipeline_logs, list_recent_uploads
from theme.components import render_page_header, render_section_header

_STATUS_ICON = {
    "started": "🔄",
    "completed": "✅",
    "partial": "🟡",
    "skipped": "⏭️",
    "failed": "❌",
}


def _status_badge(status: str) -> str:
    icon = _STATUS_ICON.get(status.lower(), "•")
    return f"{icon} **{status}**"


def render(active_page: str = "admin_pipeline") -> None:
    render_page_header("Admin", subtitle="Pipeline monitor — BRD Steps 1–7")

    st.markdown(
        """
        Trace each partner upload through the data pipeline defined in the Business Requirements:
        **Parsing → Form Mapping → Auto-correction → Value Mapping → Auto-validation →
        Currency Conversion → Notification**.
        """
    )

    with st.expander("BRD pipeline reference (Steps 1–7)", expanded=False):
        for num, name, desc in BRD_PIPELINE_STEPS:
            st.markdown(f"**Step {num} — {name}:** {desc}")

    use_sf = st.session_state.get("use_snowflake", False)
    passcode = st.session_state.get("passcode", "")

    col1, col2 = st.columns(2)
    with col1:
        partner = st.selectbox(
            "Partner filter",
            ["All", "HELLA", "MEYLE", "TMD", "NISSENS", "BREMBO", "MEMBER_DE_001"],
            index=1,
        )
    with col2:
        upload_search = st.text_input(
            "Upload ID (optional)",
            value=st.session_state.get("last_pipeline_upload_id", ""),
            placeholder="DEP-XXXXXXXX",
        )

    with scoped_connection(passcode, force_demo=not use_sf) as conn:
        uploads = list_recent_uploads(partner_filter=partner, conn=conn, limit=25)

        render_section_header("Recent uploads", subtitle=f"{len(uploads)} deposit(s)")
        if not uploads:
            st.info("No uploads found. Sign in as HELLA (or another supplier), upload a CSV, then return here as Admin.")
            return

        options = []
        for u in uploads:
            uid = str(u.get("UPLOAD_ID", u.get("upload_id", "")))
            pk = str(u.get("PARTNER_KEY", u.get("partner_key", "")))
            fn = str(u.get("FILENAME", u.get("filename", "")))
            st_at = str(u.get("SUBMITTED_AT", u.get("submitted_at", "")))
            stat = str(u.get("STATUS", u.get("status", "")))
            options.append((uid, f"{uid} | {pk} | {fn} | {stat} | {st_at}"))

        labels = [o[1] for o in options]
        default_idx = 0
        if upload_search:
            for i, (uid, _) in enumerate(options):
                if uid == upload_search:
                    default_idx = i
                    break

        choice = st.selectbox("Select upload to inspect", labels, index=default_idx)
        upload_id = options[labels.index(choice)][0] if choice in labels else options[0][0]

        meta = next(
            (u for u in uploads if str(u.get("UPLOAD_ID", u.get("upload_id"))) == upload_id),
            {},
        )

        if meta:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Partner", str(meta.get("PARTNER_KEY", meta.get("partner_key", ""))))
            m2.metric("Lines", str(meta.get("LINE_COUNT", meta.get("line_count", ""))))
            m3.metric("Status", str(meta.get("STATUS", meta.get("status", ""))))
            m4.metric("Period", str(meta.get("PERIOD_LABEL", meta.get("period_label", ""))))

        logs = list_pipeline_logs(upload_id, conn=conn)

        render_section_header("Pipeline step log", subtitle=f"Upload `{upload_id}`")

        if not logs:
            st.warning("No pipeline logs for this upload yet. Re-upload after connecting to Snowflake.")
            return

        for row in logs:
            step = row.get("STEP_NUMBER", row.get("step_number", ""))
            name = row.get("STEP_NAME", row.get("step_name", ""))
            status = str(row.get("STATUS", row.get("status", "")))
            detail = str(row.get("DETAIL", row.get("detail", "")))
            target = str(row.get("SNOWFLAKE_TARGET", row.get("snowflake_target", "")) or "")
            ts = str(row.get("CREATED_AT", row.get("created_at", "")))

            with st.container(border=True):
                st.markdown(f"### Step {step} — {name}")
                st.markdown(_status_badge(status))
                st.write(detail)
                if target:
                    st.caption(f"Snowflake: `{target}`")
                if ts:
                    st.caption(ts)

        st.divider()
        st.subheader("Raw audit trail (session)")
        from services.brd_state import init_brd_state

        init_brd_state()
        audit_rows = [
            e
            for e in st.session_state.audit_log
            if upload_id in e.detail or "PIPELINE_STEP" in e.action
        ]
        if audit_rows:
            for e in audit_rows[:30]:
                st.text(f"{e.timestamp} | {e.actor} | {e.action} | {e.detail}")
        else:
            st.caption("Audit entries appear in the same browser session after upload.")
