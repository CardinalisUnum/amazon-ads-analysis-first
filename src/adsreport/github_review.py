"""Verify an actual environment review instead of trusting a workflow actor name."""

import json
import os
import urllib.request

REPOSITORY = "CardinalisUnum/amazon-ads-analysis-first"
REVIEWER = "CardinalisUnum"


def github_reviewer() -> str:
    identifier = os.environ.get("GITHUB_RUN_ID", "")
    if (
        os.environ.get("GITHUB_ACTIONS") != "true"
        or os.environ.get("GITHUB_REPOSITORY") != REPOSITORY
        or not identifier.isdigit()
        or os.environ.get("GITHUB_RUN_ATTEMPT", "1") != "1"
    ):
        raise ValueError(
            "GitHub approval requires the repository's real Actions context."
        )
    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "adsreport"}
    if token:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request(
        f"https://api.github.com/repos/{REPOSITORY}/actions/runs/{identifier}/approvals",
        headers=headers,
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            reviews = json.load(response)
    except Exception as exc:
        raise ValueError("Could not verify GitHub environment review.") from exc
    if not isinstance(reviews, list):
        raise ValueError("Invalid GitHub review history.")
    for review in reversed(reviews):
        if isinstance(review, dict) and any(
            e.get("name") == "client-delivery" for e in review.get("environments", [])
        ):
            if (
                review.get("state") == "approved"
                and review.get("user", {}).get("login") == REVIEWER
            ):
                return REVIEWER
            break
    raise ValueError("The required owner's client-delivery approval is not recorded.")
