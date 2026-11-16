"""Merge immutable events through GitHub Contents API with optimistic retries.

Only the validated public run log is committed. Private report/receipt folders
are never enumerated. The token remains in memory and exception bodies stay private.
"""

import base64
import json
import os
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

from adsreport.runlog import Event, read_events

REPOSITORY = "CardinalisUnum/amazon-ads-analysis-first"


def merge_events(remote: bytes, local: list[Event]) -> bytes:
    merged: dict[str, Event] = {}
    for line in remote.splitlines():
        event = Event.model_validate_json(line)
        if event.event_id in merged and merged[event.event_id] != event:
            raise ValueError("Remote log contains conflicting events.")
        merged[event.event_id] = event
    additions = []
    for event in local:
        if event.event_id in merged and merged[event.event_id] != event:
            raise ValueError("Remote event conflicts with local immutable event.")
        if event.event_id not in merged:
            additions.append(event.model_dump_json() + "\n")
            merged[event.event_id] = event
    separator = b"\n" if remote and not remote.endswith(b"\n") else b""
    return remote + separator + "".join(additions).encode()


def main() -> None:
    if (
        os.environ.get("GITHUB_ACTIONS") != "true"
        or os.environ.get("GITHUB_REPOSITORY") != REPOSITORY
        or os.environ.get("GITHUB_REF") != "refs/heads/main"
    ):
        raise ValueError("Run-log publication requires the main repository workflow.")
    events = read_events(Path("runs/run-log.jsonl"))
    if not events:
        return
    token = os.environ["GITHUB_TOKEN"]
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": "Bearer " + token,
        "User-Agent": "adsreport",
    }
    url = f"https://api.github.com/repos/{REPOSITORY}/contents/runs/run-log.jsonl"
    # Preserve the repository owner's configured authorship, without coauthor tags.
    author = {
        "name": subprocess.check_output(
            ["git", "log", "-1", "--format=%an"], text=True
        ).strip(),
        "email": subprocess.check_output(
            ["git", "log", "-1", "--format=%ae"], text=True
        ).strip(),
    }
    for _ in range(4):
        sha = None
        remote = b""
        try:
            with urllib.request.urlopen(
                urllib.request.Request(url + "?ref=main", headers=headers), timeout=20
            ) as response:
                result = json.load(response)
            sha = result["sha"]
            raw = base64.b64decode(result["content"])
            remote = raw
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                raise ValueError(f"Run-log read failed: HTTP {exc.code}") from None
        content = merge_events(remote, events)
        if content == remote:
            return
        payload = {
            "message": "chore: record report execution evidence",
            "branch": "main",
            "content": base64.b64encode(content).decode(),
            "author": author,
            "committer": author,
        }
        if sha:
            payload["sha"] = sha
        request = urllib.request.Request(
            url, data=json.dumps(payload).encode(), headers=headers, method="PUT"
        )
        try:
            with urllib.request.urlopen(request, timeout=20):
                return
        except urllib.error.HTTPError as exc:
            if exc.code != 409:
                raise ValueError(f"Run-log write failed: HTTP {exc.code}") from None
    raise ValueError("Run-log publication conflicted repeatedly; retry the job.")


if __name__ == "__main__":
    main()
