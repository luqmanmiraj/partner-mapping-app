"""Full BRD pipeline engine — Steps 1–7 with Snowflake persistence."""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from typing import Any

from services import snowflake_store
from services.file_parser import ParseResult
from services.memory_store import resolve_template
from services.pipeline_log import PipelineLogger

CANONICAL_FIELDS = (
    "product_category",
    "counterparty_member",
    "counterparty_supplier",
    "amount",
    "currency",
    "period",
)

DIMENSIONS = (
    "product_category",
    "counterparty_member",
    "counterparty_supplier",
)


def _save_proposal_session(
    *,
    proposal_id: str,
    upload_id: str,
    partner_key: str,
    dimension: str,
    source_value: str,
    proposed_target: str,
    confidence_score: float,
) -> None:
    from services.brd_state import MappingProposal, save_proposal

    save_proposal(
        MappingProposal(
            proposal_id=proposal_id,
            partner_key=partner_key,
            upload_id=upload_id,
            dimension=dimension,
            source_value=source_value,
            proposed_target=proposed_target,
            confidence_score=confidence_score,
            status="Pending",
        )
    )


@dataclass
class DimensionResult:
    dimension: str
    source_value: str
    proposed_target: str
    confidence: float
    memory_scope: str  # LOCAL, GLOBAL, CORTEX, NONE


@dataclass
class LineResult:
    line_number: int
    raw: dict[str, str]
    canonical: dict[str, str]
    corrections: list[str]
    dimensions: dict[str, DimensionResult] = field(default_factory=dict)
    amount_local: float = 0.0
    amount_eur: float = 0.0
    pending_final_rate: bool = False
    fully_validated: bool = False


@dataclass
class PipelineResult:
    upload_id: str
    partner_key: str
    status: str
    line_results: list[LineResult]
    auto_validated: int = 0
    in_review: int = 0
    rejected: int = 0
    local_total: float = 0.0
    eur_total: float = 0.0
    pending_final_rate: bool = False
    validation_source: str = "NONE"
    column_mapping: dict[str, str] = field(default_factory=dict)
    rejection_reasons: list[str] = field(default_factory=list)


def apply_form_mapping(row: dict[str, str], column_mapping: dict[str, str]) -> dict[str, str]:
    """Step 2 — map partner columns to canonical names."""
    if not column_mapping:
        out = {k: str(v).strip() for k, v in row.items()}
        for field_name in CANONICAL_FIELDS:
            out.setdefault(field_name, "")
        return out

    canonical: dict[str, str] = {}
    lower_map = {k.lower(): k for k in row.keys()}
    for src_col, canon in column_mapping.items():
        key = lower_map.get(src_col.lower(), src_col)
        if key in row:
            canonical[canon] = str(row[key]).strip()
    for field_name in CANONICAL_FIELDS:
        canonical.setdefault(field_name, "")
    if not canonical.get("amount"):
        for k, v in row.items():
            if k.lower() in ("amount", "total", "turnover", "value"):
                canonical["amount"] = str(v).strip()
                break
    return canonical


def auto_correct_line(canonical: dict[str, str]) -> tuple[dict[str, str], list[str]]:
    """Step 3 — trivial fixes (trim, amount/date normalization)."""
    fixes: list[str] = []
    out = dict(canonical)

    for key, val in list(out.items()):
        if not isinstance(val, str):
            continue
        stripped = val.strip()
        if stripped != val:
            out[key] = stripped
            fixes.append(f"{key}: trimmed whitespace")

    if out.get("amount"):
        raw = out["amount"].replace("€", "").replace(" ", "").strip()
        if "," in raw and "." not in raw:
            normalized = raw.replace(",", ".")
            out["amount"] = normalized
            fixes.append("amount: normalized decimal comma → dot")
        else:
            out["amount"] = raw.replace(",", "")

    for date_key in ("period",):
        val = out.get(date_key, "")
        m = re.match(r"^(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})$", val)
        if m:
            d, mo, y = m.groups()
            y = y if len(y) == 4 else f"20{y}"
            iso = f"{y}-{int(mo):02d}-{int(d):02d}"
            out[date_key] = iso
            fixes.append(f"{date_key}: normalized date → {iso}")

    return out, fixes


def _parse_amount(value: str) -> float:
    try:
        return float(str(value).replace(",", "").replace("€", "").strip() or 0)
    except ValueError:
        return 0.0


def map_dimension(
    conn,
    *,
    partner_key: str,
    dimension: str,
    source_value: str,
    threshold: float,
) -> DimensionResult:
    """Step 4 — LOCAL → GLOBAL → Cortex/taxonomy fallback."""
    sv = (source_value or "").strip()[:2000]
    if not sv:
        return DimensionResult(dimension, sv, "", 0.0, "NONE")

    if conn is not None:
        local = snowflake_store.lookup_value_memory(conn, partner_key, dimension, sv)
        if local:
            return DimensionResult(dimension, sv, local, 1.0, "LOCAL")

        global_hit = snowflake_store.lookup_value_memory(conn, "", dimension, sv)
        if global_hit:
            return DimensionResult(dimension, sv, global_hit, 0.95, "GLOBAL")

        cortex = snowflake_store.cortex_propose(conn, dimension=dimension, source_value=sv)
        if cortex:
            target, conf = cortex
            return DimensionResult(dimension, sv, target, conf, "CORTEX")

    # Session/offline heuristic
    target = f"GA-{abs(hash(sv)) % 100000:05d}"
    conf = 0.72 if len(sv) > 3 else 0.5
    return DimensionResult(dimension, sv, target, conf, "CORTEX")


def process_lines(
    conn,
    *,
    parsed: ParseResult,
    partner_key: str,
    period: str,
    currency: str,
    column_mapping: dict[str, str],
    threshold: float,
    plog: PipelineLogger | None = None,
) -> list[LineResult]:
    """Steps 2–5 per line."""
    results: list[LineResult] = []
    total_corrections = 0

    for i, row in enumerate(parsed.lines[:5000], start=1):
        raw = {k: str(v) for k, v in row.items()}
        canonical = apply_form_mapping(raw, column_mapping)
        canonical, fixes = auto_correct_line(canonical)
        if not canonical.get("currency"):
            canonical["currency"] = currency
        if not canonical.get("period"):
            canonical["period"] = period
        total_corrections += len(fixes)

        amount = _parse_amount(canonical.get("amount", "0"))
        eur, pending = amount, False
        line_currency = canonical.get("currency", currency) or currency
        if conn is not None:
            eur, pending = snowflake_store.convert_to_eur(conn, amount, line_currency, period)
        elif line_currency.upper() != "EUR":
            rates = {"USD": 0.92, "GBP": 1.17, "PLN": 0.23, "CHF": 1.05}
            eur = round(amount * rates.get(line_currency.upper(), 1.0), 2)
            pending = True

        dims: dict[str, DimensionResult] = {}
        for dim in DIMENSIONS:
            field_key = {
                "product_category": "product_category",
                "counterparty_member": "counterparty_member",
                "counterparty_supplier": "counterparty_supplier",
            }[dim]
            source = canonical.get(field_key, "")
            dims[dim] = map_dimension(
                conn, partner_key=partner_key, dimension=dim, source_value=source, threshold=threshold
            )

        fully = all(d.confidence >= threshold and d.proposed_target for d in dims.values())
        results.append(
            LineResult(
                line_number=i,
                raw=raw,
                canonical=canonical,
                corrections=fixes,
                dimensions=dims,
                amount_local=amount,
                amount_eur=eur,
                pending_final_rate=pending,
                fully_validated=fully,
            )
        )

    if plog:
        if total_corrections:
            plog.log(3, "Auto-correction", "completed", f"Applied {total_corrections} trivial fix(es) across lines")
        else:
            plog.log(3, "Auto-correction", "completed", "No trivial anomalies — lines passed auto-correction")

    return results


def run_pipeline(
    conn,
    *,
    upload_id: str,
    partner_key: str,
    declarant_type: str,
    filename: str,
    file_bytes: bytes,
    period: str,
    currency: str,
    comment: str,
    parsed: ParseResult,
    threshold: float,
    is_corrective: bool = False,
    supersedes_upload_id: str = "",
    plog: PipelineLogger | None = None,
) -> PipelineResult:
    """Execute BRD steps 2–7 and persist to Snowflake when conn is set."""

    # Step 2 — form mapping
    if plog:
        plog.log(2, "Form Mapping", "started", f"Resolve template for {partner_key}")

    resolved = resolve_template(partner_key, list(parsed.lines[0].keys()), conn=conn)
    column_mapping: dict[str, str] = {}
    validation_source = "NONE"

    if resolved:
        column_mapping = dict(resolved.get("mapping", {}))
        if not column_mapping:
            column_mapping = {c: c for c in parsed.lines[0].keys()}
        validation_source = str(resolved.get("scope", "LOCAL"))
        if plog:
            plog.log(
                2,
                "Form Mapping",
                "completed",
                f"Template {validation_source}: {len(column_mapping)} columns → canonical",
                snowflake_target="APP.CALIBRATION_TEMPLATE",
            )
    else:
        column_mapping = {c: c for c in parsed.lines[0].keys()}
        if plog:
            plog.log(
                2,
                "Form Mapping",
                "partial",
                "No saved calibration — using identity column map; run Admin → Calibration",
                snowflake_target="APP.CALIBRATION_TEMPLATE",
            )

    # Steps 3–5 per line
    if plog:
        plog.log(
            4,
            "Value Mapping",
            "started",
            "Per line: LOCAL_MEMORY → GLOBAL_MEMORY → Cortex/taxonomy",
        )

    line_results = process_lines(
        conn,
        parsed=parsed,
        partner_key=partner_key,
        period=period,
        currency=currency,
        column_mapping=column_mapping,
        threshold=threshold,
        plog=plog,
    )

    auto = sum(1 for lr in line_results if lr.fully_validated)
    review = len(line_results) - auto
    local_total = sum(lr.amount_local for lr in line_results)
    eur_total = sum(lr.amount_eur for lr in line_results)
    any_pending = any(lr.pending_final_rate for lr in line_results)

    if auto == len(line_results) and len(line_results) > 0:
        status = "Validated"
    elif review > 0:
        status = "In review"
    else:
        status = "Pending processing"

    if plog:
        plog.log(
            4,
            "Value Mapping",
            "completed",
            f"Processed {len(line_results)} lines",
            snowflake_target="APP.LOCAL_MEMORY / APP.GLOBAL_MEMORY / Cortex",
        )
        plog.log(
            5,
            "Auto-validation",
            "completed" if auto == len(line_results) else "partial",
            f"auto_validated={auto}, in_review={review}, threshold={threshold}",
            snowflake_target="APP.VALIDATED_LINE / APP.MAPPING_PROPOSAL",
        )

    if plog:
        plog.log(
            6,
            "Currency Conversion",
            "completed",
            f"line-level EUR computed; deposit totals local={local_total:,.2f} eur={eur_total:,.2f} pending_rate={any_pending}",
            snowflake_target="STAGING.PARSED_LINE + REF.CURRENCY_RATE",
        )

    for lr in line_results:
        if lr.fully_validated:
            continue
        for dim, dr in lr.dimensions.items():
            if dr.confidence >= threshold and dr.proposed_target:
                continue
            _save_proposal_session(
                proposal_id=f"MAP-{uuid.uuid4().hex[:8].upper()}",
                upload_id=upload_id,
                partner_key=partner_key,
                dimension=dim,
                source_value=dr.source_value,
                proposed_target=dr.proposed_target or "Pending review",
                confidence_score=dr.confidence,
            )

    if conn is not None:
        if is_corrective and supersedes_upload_id:
            snowflake_store.supersede_upload(conn, supersedes_upload_id)

        snowflake_store.insert_raw_file(
            conn,
            upload_id=upload_id,
            partner_key=partner_key,
            declarant_type=declarant_type,
            period=period,
            currency=currency,
            comment=comment,
            filename=filename,
            file_size=len(file_bytes),
            line_count=len(line_results),
            status=status,
            auto_validated=auto,
            in_review=review,
            rejected=0,
            local_total=local_total,
            eur_total=eur_total,
            pending_final_rate=any_pending,
            is_corrective=is_corrective,
            supersedes_upload_id=supersedes_upload_id,
        )

        for lr in line_results:
            line_id = f"LN-{uuid.uuid4().hex[:12].upper()}"
            snowflake_store.insert_parsed_line(
                conn,
                line_id=line_id,
                upload_id=upload_id,
                partner_key=partner_key,
                line_number=lr.line_number,
                raw_payload=lr.raw,
                canonical_payload=lr.canonical,
                turnover_local=lr.amount_local,
                currency_code=lr.canonical.get("currency", currency),
                turnover_eur=lr.amount_eur,
                pending_final_rate=lr.pending_final_rate,
                parse_status="auto_corrected" if lr.corrections else "parsed",
            )
            for fix in lr.corrections:
                snowflake_store.insert_upload_error(
                    conn,
                    upload_id=upload_id,
                    partner_key=partner_key,
                    line_number=lr.line_number,
                    error_code="AUTO_CORRECT",
                    error_message=fix,
                )

            if lr.fully_validated:
                snowflake_store.insert_validated_line(
                    conn,
                    upload_id=upload_id,
                    partner_key=partner_key,
                    period_label=period,
                    product_category_id=lr.dimensions["product_category"].proposed_target,
                    counterparty_member_id=lr.dimensions["counterparty_member"].proposed_target,
                    counterparty_supplier_id=lr.dimensions["counterparty_supplier"].proposed_target,
                    turnover_local=lr.amount_local,
                    currency_code=lr.canonical.get("currency", currency),
                    turnover_eur=lr.amount_eur,
                    pending_final_rate=lr.pending_final_rate,
                )
            else:
                for dim, dr in lr.dimensions.items():
                    if dr.confidence >= threshold and dr.proposed_target:
                        continue
                    snowflake_store.insert_mapping_proposal(
                        conn,
                        proposal_id=f"MAP-{uuid.uuid4().hex[:8].upper()}",
                        upload_id=upload_id,
                        partner_key=partner_key,
                        dimension=dim,
                        source_value=dr.source_value,
                        proposed_target=dr.proposed_target or "Pending review",
                        confidence_score=dr.confidence,
                    )

        if auto > 0:
            snowflake_store.refresh_business_view(
                conn, upload_id=upload_id, partner_key=partner_key, period_label=period
            )
            if plog:
                plog.log(
                    5,
                    "Auto-validation",
                    "completed",
                    f"Refreshed OUTPUT.BUSINESS_VIEW for {auto} validated line(s)",
                    snowflake_target="OUTPUT.BUSINESS_VIEW",
                )

        msg = f"Processing complete for {period}: {status}."
        snowflake_store.insert_notification(
            conn,
            partner_key=partner_key,
            upload_id=upload_id,
            category="Declaration",
            message=msg,
            notification_type="deposit",
        )
        if plog:
            plog.log(
                7,
                "Notification",
                "completed",
                f"{msg} Stored in APP.NOTIFICATION (email stub: set NOTIFY_EMAIL_URL to enable)",
                snowflake_target="APP.NOTIFICATION",
            )

    return PipelineResult(
        upload_id=upload_id,
        partner_key=partner_key,
        status=status,
        line_results=line_results,
        auto_validated=auto,
        in_review=review,
        local_total=local_total,
        eur_total=eur_total,
        pending_final_rate=any_pending,
        validation_source=validation_source,
        column_mapping=column_mapping,
    )
