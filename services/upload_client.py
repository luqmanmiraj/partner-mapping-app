"""Upload client — delegates to processing pipeline or API."""

from __future__ import annotations

import os
from dataclasses import dataclass

from services.processing_pipeline import process_upload


@dataclass
class UploadResult:
    success: bool
    upload_id: str = ""
    message: str = ""
    error: str = ""


def upload_declaration(
    *,
    file_bytes: bytes,
    filename: str,
    period: str,
    currency: str,
    comment: str,
    partner_key: str,
    is_corrective: bool = False,
    supersedes_upload_id: str = "",
) -> UploadResult:
    api_url = os.environ.get("UPLOAD_API_URL", "")
    if api_url:
        return UploadResult(success=False, error="UPLOAD_API_URL set — wire Lambda ingestion (not yet connected).")

    ok, upload_id, msg = process_upload(
        file_bytes=file_bytes,
        filename=filename,
        period=period,
        currency=currency,
        comment=comment,
        partner_key=partner_key,
        is_corrective=is_corrective,
        supersedes_upload_id=supersedes_upload_id,
    )
    if ok:
        return UploadResult(success=True, upload_id=upload_id, message=msg)
    return UploadResult(success=False, error=msg)
