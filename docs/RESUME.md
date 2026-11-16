# Resume this checkpoint

Current phase P1, in progress. Owner requested explicit approval at every phase gate and a commit and push at every checkpoint. Owner approved P1 on 2026-11-16. P2 approval is pending.

## Read first

1. AGENTS.md and CLAUDE.md for shared working rules.
2. docs/decisions.md for owner-approved changes to the original brief.
3. docs/STATUS.md for all 56 acceptance tasks and weighted progress.
4. docs/SPEC.md for the technical build scope.
5. docs/evidence/ for actual execution evidence.

## Environment

The pre-existing system Python is 3.11. P0 downloaded Python 3.13.18 into `.tools/python/cpython-3.13.18-windows-x86_64-none/`. The local isolated probe environment is `.tools/p0-check/`. Bootstrap uv is `.tools/bootstrap/bin/uv.exe`.

Windows sandbox denied uv temporary/cache writes. Python's standard `venv` created the probe environment successfully. These are local ignored tools. P1 should use uv for the project lock and install, resolving the temporary-directory issue before claiming the packaging gate.

The ignored `.env` holds the owner-supplied Gemini credential. It must be rotated before unattended service setup because it was shared in chat. Never read it into logs or commit it. A replacement should be saved directly by the owner. Use the standard Gemini endpoint only for the requested synthetic test.

## Next actions

P0 is complete. The owner approved P1 on 2026-11-16. Complete P1 then stop for the P2 gate.

- Read docs/evidence/p0-stack.json and p0-gemini.json for actual results.
- Pango/native libraries are unavailable in this Windows environment. Implement and verify an Ubuntu runner dependency installation before claiming PDF support in P6.
- uv version executes but uv venv temporary/cache writes were denied. The isolated P0 probe used standard venv/pip. P1 must demonstrate uv sync --locked with a chosen supported execution environment.
- After approval, create the P1 package, lock, CLI/config, MIT license and CI. Preserve owner control at the next gate.
- The key was shared in chat. Rotate it before unattended setup, saving its replacement directly in ignored .env. No credential has been committed.

## Persistence

The origin is `https://github.com/CardinalisUnum/amazon-ads-analysis-first.git`, branch main. Normal Git network operations required escalation to access the existing Git credential helper in this Windows environment. Use commit messages with no secrets. Confirm the remote SHA after pushing.

Commit this resume file with an accurate update at every checkpoint. Another agent should verify current branch, working tree and remote SHA before continuing.
