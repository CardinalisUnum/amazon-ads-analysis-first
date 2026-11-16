"""Immutable approved archive and retry-aware notification receipt state."""

import hashlib
import io
import json
import zipfile
from pathlib import Path

from adsreport.approval import freeze
from adsreport.notifications import notify
from adsreport.runlog import exclusive_lock


def deliver_report(
    folder: Path,
    expected: str,
    outbox: Path,
    *,
    retry_uncertain: bool = False,
    test_mode: bool = False,
) -> dict[str, str]:
    bundle = freeze(folder, expected)
    approval = bundle.document.approval
    if bundle.manifest.status != "APPROVED" or approval is None:
        raise ValueError("Only an approved frozen report can be delivered.")
    if approval.mechanism == "test" and not test_mode:
        raise ValueError(
            "Test approvals cannot be delivered through the production command."
        )
    target = outbox / expected
    with exclusive_lock(target.with_suffix(".lock")):
        target.mkdir(parents=True, exist_ok=True)
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, content in sorted(bundle.files.items()):
                entry = zipfile.ZipInfo(name, date_time=(2000, 1, 1, 0, 0, 0))
                entry.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(entry, content)
        data = stream.getvalue()
        checksum = hashlib.sha256(data).hexdigest()
        zip_path = target / "SAMPLE-approved.zip"
        if zip_path.exists() and zip_path.read_bytes() != data:
            raise ValueError(
                "Existing delivery archive differs from the approved version."
            )
        if not zip_path.exists():
            zip_path.write_bytes(data)
        metadata = {
            "approved_manifest_sha256": expected,
            "archive_sha256": checksum,
            "report_id": bundle.manifest.report_id,
        }
        metadata_path = target / "delivery.json"
        if (
            metadata_path.exists()
            and json.loads(metadata_path.read_text(encoding="utf-8")) != metadata
        ):
            raise ValueError("Delivery receipt identity differs.")
        metadata_path.write_text(
            json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
        )
        subject = "SAMPLE DATA - approved Amazon Ads report"
        text = (
            f"{bundle.manifest.report_id}\nApproved by {approval.reviewer} "
            f"at {approval.approved_at.isoformat()}.\n"
            "Independent retailer simulation. No brand affiliation. "
            "The attached archive is the frozen approved version."
        )
        return notify(
            subject,
            text,
            data,
            target / "notifications.json",
            retry_uncertain=retry_uncertain,
        )
