"""Append-only operational evidence with explicit trigger and event identity."""

import os
import subprocess
import time
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field


class RunIdentity(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    run_id: str
    trigger: Literal["manual", "schedule", "test_failure"]
    started_at: AwareDatetime
    git_sha: str
    workflow_run_url: str | None = None
    working_tree_dirty: bool = False


class Event(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    event_id: str
    event: Literal["run_started", "run", "approval", "delivery"]
    run: RunIdentity
    finished_at: AwareDatetime
    status: Literal["in_progress", "success", "failure", "partial"]
    failed_step: str | None = None
    error_type: str | None = None
    elapsed_seconds: float = Field(ge=0, allow_inf_nan=False)
    products: int = 0
    flags_by_severity: dict[str, int] = Field(default_factory=dict)
    ai_used: bool = False
    guard_rejections: int = 0
    provider_error_status: int | None = None
    ai_request_status: str | None = None
    ai_attempts: int = 0
    outputs: dict[str, str] = Field(default_factory=dict)
    approval: dict[str, str] = Field(default_factory=lambda: {"state": "pending"})
    notifications: dict[str, str] = Field(default_factory=dict)


@contextmanager
def exclusive_lock(path: Path) -> Iterator[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise ValueError(
            "Operation is locked. Check the active process before removing "
            "a stale lock."
        ) from exc
    try:
        os.close(descriptor)
        yield
    finally:
        path.unlink()


def read_events(path: Path) -> list[Event]:
    if not path.exists():
        return []
    unique: dict[str, Event] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        event = Event.model_validate_json(line)
        previous = unique.get(event.event_id)
        if previous is not None and previous != event:
            raise ValueError("Conflicting run-log event identity.")
        unique[event.event_id] = event
    return list(unique.values())


def append_event(path: Path, event: Event, *, same_approval: bool = False) -> None:
    with exclusive_lock(path.with_suffix(".lock")):
        existing = next(
            (e for e in read_events(path) if e.event_id == event.event_id), None
        )
        if existing is not None:
            equivalent = (
                same_approval
                and existing.event == event.event == "approval"
                and existing.outputs == event.outputs
                and existing.approval == event.approval
            )
            if existing != event and not equivalent:
                raise ValueError("Run-log event cannot be rewritten.")
            return
        with path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(event.model_dump_json() + "\n")
            stream.flush()
            os.fsync(stream.fileno())


def scheduled_rate(events: list[Event]) -> dict[str, int | float | None]:
    scheduled = {
        e.run.run_id: e
        for e in events
        if e.event in {"run_started", "run"} and e.run.trigger == "schedule"
    }
    successful = sum(e.status == "success" for e in scheduled.values())
    return {
        "successful": successful,
        "scheduled": len(scheduled),
        "incomplete": sum(e.status == "in_progress" for e in scheduled.values()),
        "percent": 100 * successful / len(scheduled) if scheduled else None,
    }


def new_run(*, test_failure: bool = False) -> RunIdentity:
    trigger: Literal["manual", "schedule", "test_failure"] = (
        "test_failure" if test_failure else "manual"
    )
    workflow_url = None
    if os.environ.get("GITHUB_ACTIONS") == "true":
        repository = os.environ.get("GITHUB_REPOSITORY", "")
        identifier = os.environ.get("GITHUB_RUN_ID", "")
        if (
            repository == "CardinalisUnum/amazon-ads-analysis-first"
            and identifier.isdigit()
        ):
            workflow_url = f"https://github.com/{repository}/actions/runs/{identifier}"
            if not test_failure and os.environ.get("GITHUB_EVENT_NAME") == "schedule":
                trigger = "schedule"
    try:
        sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
        dirty = bool(
            subprocess.check_output(["git", "status", "--porcelain"], text=True)
        )
    except (OSError, subprocess.CalledProcessError):
        sha = "unavailable"
        dirty = True
    return RunIdentity(
        run_id=datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ-") + uuid.uuid4().hex[:12],
        trigger=trigger,
        started_at=datetime.now(UTC),
        git_sha=sha,
        workflow_run_url=workflow_url,
        working_tree_dirty=dirty,
    )


def event_now(
    run: RunIdentity,
    kind: Literal["run_started", "run", "approval", "delivery"],
    status: Literal["in_progress", "success", "failure", "partial"],
    started: float,
    **details: object,
) -> Event:
    return Event.model_validate(
        {
            "event_id": run.run_id + "-" + kind + "-" + uuid.uuid4().hex,
            "event": kind,
            "run": run,
            "finished_at": datetime.now(UTC),
            "status": status,
            "elapsed_seconds": round(time.perf_counter() - started, 6),
            **details,
        }
    )
