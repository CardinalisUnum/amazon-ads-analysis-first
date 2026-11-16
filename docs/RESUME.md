# Resume this checkpoint

Current phase P0. Owner requested explicit approval at every phase gate and a commit and push at every checkpoint. No approval for P1 has been recorded.

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

- Finish P0 installation and record dependency compatibility, pandas behavior and PDF-native dependency outcomes.
- Run `scripts/check_gemini.py --confirm-unbilled` in the probe environment using the owner's Free Tier key. It writes only synthetic response evidence. If access fails, diagnose provider status safely and record the specific unmet dependency.
- Update STATUS with completed evidence and push the checkpoint. Ask for P1 approval only when presenting the P0 result and open conditions accurately.
- On approval, build P1 scaffold, reproducible lock, CLI/config and CI. Do not start P2 before its gate.

## Persistence

The origin is `https://github.com/CardinalisUnum/amazon-ads-analysis-first.git`, branch main. Normal Git network operations required escalation to access the existing Git credential helper in this Windows environment. Use commit messages with no secrets. Confirm the remote SHA after pushing.

Commit this resume file with an accurate update at every checkpoint. Another agent should verify current branch, working tree and remote SHA before continuing.
