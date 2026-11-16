"""P0 account check. Run only with an owner-confirmed unbilled project."""

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

from google import genai
from google.genai import errors
from pydantic import BaseModel, ConfigDict


class CheckResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    product: str
    note: str


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirm-unbilled", action="store_true")
    args = parser.parse_args()
    if not args.confirm_unbilled:
        print("Confirm the project is Free Tier with billing unlinked first.")
        return 2
    # Read only the two expected settings. Never evaluate the file or echo values.
    settings = dict(os.environ)
    env_file = Path(".env")
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8-sig").splitlines():
            name, separator, value = line.partition("=")
            if separator and name.strip() in {"GEMINI_API_KEY", "GEMINI_MODEL"}:
                settings.setdefault(name.strip(), value.strip().strip("\"'"))
    key = settings.get("GEMINI_API_KEY", "")
    if not key:
        print("GEMINI_API_KEY is missing. Configure the ignored .env file.")
        return 2
    model = settings.get("GEMINI_MODEL", "gemini-3.5-flash-lite")
    try:
        with genai.Client(api_key=key) as client:
            reply = client.interactions.create(
                model=model,
                input=(
                    "SAMPLE DATA. Product SAMPLE-01 has contribution after ads "
                    "of EUR 180. Return its identifier and a short note using only "
                    "this fact. Do not calculate anything."
                ),
                response_format={
                    "type": "text",
                    "mime_type": "application/json",
                    "schema": CheckResult.model_json_schema(),
                },
            )
        result = CheckResult.model_validate_json(reply.output_text)
        if result.product != "SAMPLE-01":
            raise ValueError("Unexpected product")
    except (errors.APIError, ValueError, OSError) as exc:
        # Provider exception text may contain request details. Store only its class.
        print(json.dumps({"status": "failed", "error_type": type(exc).__name__}))
        return 1
    evidence = {
        "status": "parsed_response",
        "model": model,
        "checked_at": datetime.now(UTC).isoformat(),
        "project_unbilled_confirmed_by_operator": True,
        "sample_data": True,
        "response": result.model_dump(),
    }
    path = Path("docs/evidence/p0-gemini.json")
    path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evidence, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
