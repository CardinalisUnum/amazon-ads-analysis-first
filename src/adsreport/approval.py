"""Review the exact frozen bytes, preserve the draft, then re-stamp its facts."""

import csv
import hashlib
import io
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from adsreport.artifacts import publish_bundle
from adsreport.pipeline import render_bundle
from adsreport.report import Approval, ReportDocument, restore_view

DIGEST = Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]
BASE_FILES = frozenset(
    {
        "report.json",
        "SAMPLE_kpis.csv",
        *["SAMPLE_report." + s for s in ("html", "pdf", "xlsx", "pptx")],
        *[
            f"SAMPLE_{name}.{suffix}"
            for name in ("tacos", "contribution", "acos")
            for suffix in ("svg", "png")
        ],
    }
)


class Manifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    report_id: str
    status: Literal["DRAFT", "APPROVED"]
    data_label: Literal["SAMPLE DATA"]
    sha256: dict[str, DIGEST]


@dataclass(frozen=True)
class FrozenBundle:
    manifest: Manifest
    manifest_sha256: str
    files: dict[str, bytes]
    document: ReportDocument


def freeze(folder: Path, expected: str | None = None) -> FrozenBundle:
    if folder.is_symlink() or not folder.is_dir():
        raise ValueError("Report must be a regular bundle directory.")
    names = {p.name for p in folder.iterdir()}
    if "artifacts.json" not in names:
        raise ValueError("Report has no artifact manifest.")
    if not names <= BASE_FILES | {"artifacts.json", "approval.json"}:
        raise ValueError("Bundle contains unexpected file names.")
    files = {}
    for name in names:
        path = folder / name
        if path.is_symlink() or not path.is_file():
            raise ValueError("Bundle contains an unexpected file or link.")
        files[name] = path.read_bytes()
    digest = hashlib.sha256(files["artifacts.json"]).hexdigest()
    if expected is not None and digest != expected:
        raise ValueError("Manifest changed since review. Inspect and review again.")
    try:
        manifest = Manifest.model_validate_json(files["artifacts.json"])
    except ValidationError as exc:
        raise ValueError("Invalid artifact manifest.") from exc
    required = BASE_FILES | (
        {"approval.json"} if manifest.status == "APPROVED" else set()
    )
    if set(manifest.sha256) != required or names != required | {"artifacts.json"}:
        raise ValueError("Bundle file set differs from its contract.")
    for name, checksum in manifest.sha256.items():
        if hashlib.sha256(files[name]).hexdigest() != checksum:
            raise ValueError(f"Frozen artifact checksum mismatch: {name}")
    try:
        document = ReportDocument.model_validate_json(files["report.json"])
        if (
            document.status != manifest.status
            or document.presentation.report_id != manifest.report_id
        ):
            raise ValueError("Report identity/status differs from manifest.")
        if document.analysis.report_week != document.report_week:
            raise ValueError("Report weeks differ.")
        if len({(p.asin, p.week) for p in document.products}) != len(document.products):
            raise ValueError("Duplicate product-week facts.")
        restore_view(document)
        if manifest.status == "APPROVED":
            approval = Approval.model_validate_json(files["approval.json"])
            if approval != document.approval:
                raise ValueError("Approval records differ.")
    except (ValidationError, KeyError, StopIteration) as exc:
        raise ValueError("Frozen report structure is invalid.") from exc
    return FrozenBundle(manifest, digest, files, document)


def approve_report(
    folder: Path,
    destination: Path,
    expected: str,
    reviewer: str,
    *,
    mechanism: Literal[
        "local_attestation", "github_environment", "test"
    ] = "local_attestation",
) -> FrozenBundle:
    source = freeze(folder, expected)
    if source.manifest.status != "DRAFT":
        raise ValueError("Only a DRAFT bundle can be approved.")
    if destination.resolve() == folder.resolve():
        raise ValueError("Approved output must preserve the original draft directory.")
    if destination.exists():
        existing = freeze(destination)
        prior = existing.document.approval
        if (
            prior
            and prior.draft_manifest_sha256 == expected
            and prior.reviewer == reviewer
            and prior.mechanism == mechanism
        ):
            return existing
        raise ValueError("Approved output already exists for another review.")
    approval = Approval(
        reviewer=reviewer,
        approved_at=datetime.now(UTC),
        draft_manifest_sha256=expected,
        mechanism=mechanism,
    )
    document = source.document.model_copy(
        update={"status": "APPROVED", "approval": approval}
    )
    view = restore_view(document)
    original = io.StringIO(source.files["SAMPLE_kpis.csv"].decode("utf-8"), newline="")
    reader = csv.DictReader(original)
    if not reader.fieldnames:
        raise ValueError("Frozen KPI CSV has no headers.")
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=reader.fieldnames, lineterminator="\n")
    writer.writeheader()
    for row in reader:
        if row.get("status") != "DRAFT" or row.get("data_label") != "SAMPLE DATA":
            raise ValueError("Frozen CSV status/data label differs.")
        writer.writerow(row | {"status": "APPROVED"})
    charts = {
        name: content
        for name, content in source.files.items()
        if name.endswith((".svg", ".png"))
    }
    files = render_bundle(
        view,
        document.model_dump(mode="json"),
        output.getvalue().encode(),
        charts=charts,
        extra={"approval.json": (approval.model_dump_json(indent=2) + "\n").encode()},
    )
    publish_bundle(destination, files)
    return freeze(destination)
