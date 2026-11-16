"""Measured run lifecycle and safe public event records."""

import os
import time
from collections import Counter
from pathlib import Path

from adsreport.approval import FrozenBundle, approve_report, freeze
from adsreport.config import load_config
from adsreport.delivery import deliver_report
from adsreport.notifications import notify
from adsreport.pipeline import run_numerical_draft
from adsreport.runlog import RunIdentity, append_event, event_now, new_run


def log_path() -> Path:
    return Path(os.environ.get("ADSREPORT_RUN_LOG", "runs/run-log.jsonl"))


def outbox_path() -> Path:
    return Path(os.environ.get("ADSREPORT_OUTBOX", "reports/outbox"))


def execute_run(
    folder: Path,
    destination: Path | None,
    config_dir: Path,
    *,
    no_ai: bool,
    inject_failure: bool = False,
) -> Path:
    identity = new_run(test_failure=inject_failure)
    start = time.perf_counter()
    append_event(log_path(), event_now(identity, "run_started", "in_progress", start))
    step = "configuration"

    def stage(value: str) -> None:
        nonlocal step
        step = value

    try:
        configuration = load_config(config_dir)
        if inject_failure:
            step = "injected_failure"
            raise ValueError("Injected test_failure for alert verification.")
        output = (
            destination
            if destination is not None
            else Path("reports") / identity.run_id / "draft"
        )
        path = run_numerical_draft(
            folder,
            output,
            config_dir,
            configuration,
            no_ai=no_ai,
            run=identity,
            on_stage=stage,
        )
        bundle = freeze(path)
    except Exception as exc:
        try:
            notifications = notify(
                "SAMPLE DATA - report failure",
                f"Run {identity.run_id}\nTrigger {identity.trigger}\n"
                f"Failed step {step}. Error type {type(exc).__name__}.\n"
                "No report is approved or delivered.",
                None,
                outbox_path() / identity.run_id / "failure.json",
            )
        except Exception:
            notifications = {"email": "alert_error", "discord": "alert_error"}
        append_event(
            log_path(),
            event_now(
                identity,
                "run",
                "failure",
                start,
                failed_step=step,
                error_type=type(exc).__name__,
                notifications=notifications,
            ),
        )
        raise
    document = bundle.document
    append_event(
        log_path(),
        event_now(
            identity,
            "run",
            "success",
            start,
            products=len(
                {p.asin for p in document.products if p.week == document.report_week}
            ),
            flags_by_severity=dict(
                Counter(f.severity for f in document.analysis.flags)
            ),
            ai_used=document.commentary.ai_used,
            guard_rejections=document.commentary.guard_rejections,
            provider_error_status=document.commentary.provider_error_status,
            ai_request_status=document.commentary.request_status,
            ai_attempts=document.commentary.attempts,
            outputs=bundle.manifest.sha256 | {"artifacts.json": bundle.manifest_sha256},
        ),
    )
    return path


def identity_for(bundle: FrozenBundle) -> RunIdentity:
    return bundle.document.run or new_run()


def execute_approval(
    folder: Path,
    destination: Path,
    expected: str,
    reviewer: str,
    *,
    github: bool = False,
) -> FrozenBundle:
    start = time.perf_counter()
    if github:
        from adsreport.github_review import github_reviewer

        reviewer = github_reviewer()
    result = approve_report(
        folder,
        destination,
        expected,
        reviewer,
        mechanism="github_environment" if github else "local_attestation",
    )
    approval = result.document.approval
    if approval is None:
        raise ValueError("Approval record missing.")
    event = event_now(
        identity_for(result),
        "approval",
        "success",
        start,
        outputs={
            "draft_manifest": expected,
            "approved_manifest": result.manifest_sha256,
        },
        approval={
            "state": "approved",
            "reviewer": approval.reviewer,
            "approved_at": approval.approved_at.isoformat(),
            "mechanism": approval.mechanism,
        },
    )
    # Retrying the same immutable approval does not append another approval event.
    event = event.model_copy(update={"event_id": "approval-" + result.manifest_sha256})
    append_event(log_path(), event, same_approval=True)
    return result


def execute_delivery(
    folder: Path, expected: str, *, retry_uncertain: bool = False
) -> dict[str, str]:
    start = time.perf_counter()
    bundle = freeze(folder, expected)
    try:
        states = deliver_report(
            folder, expected, outbox_path(), retry_uncertain=retry_uncertain
        )
    except Exception as exc:
        append_event(
            log_path(),
            event_now(
                identity_for(bundle),
                "delivery",
                "failure",
                start,
                failed_step="delivery",
                error_type=type(exc).__name__,
                approval={"state": "approved"}
                if bundle.document.approval
                else {"state": "pending"},
            ),
        )
        raise
    complete = all(state == "accepted" for state in states.values())
    append_event(
        log_path(),
        event_now(
            identity_for(bundle),
            "delivery",
            "success" if complete else "partial",
            start,
            outputs={"approved_manifest": expected},
            approval={"state": "approved"},
            notifications=states,
        ),
    )
    return states


def inspect_report(folder: Path) -> dict[str, object]:
    bundle = freeze(folder)
    return {
        "report_id": bundle.manifest.report_id,
        "manifest_sha256": bundle.manifest_sha256,
        "status": bundle.manifest.status,
        "data_label": "SAMPLE DATA",
        "run_id": bundle.document.run.run_id if bundle.document.run else None,
        "products": len(
            {
                p.asin
                for p in bundle.document.products
                if p.week == bundle.document.report_week
            }
        ),
        "flags": len(bundle.document.analysis.flags),
        "ai_outcome": bundle.document.commentary.request_status,
        "provider_error_status": bundle.document.commentary.provider_error_status,
    }
