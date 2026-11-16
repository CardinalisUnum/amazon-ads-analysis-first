# P8 documentation and readiness checkpoint

The buildable documentation is complete: README, OPERATIONS, PROCESS, LIMITS, REVIEW-EFFORT, OWNER-ACTIONS, the three-minute demo script and the independent audit request. Architecture/output/commentary/assumption documents now describe the implemented operations instead of future placeholders.

README and PROCESS require owner sign-off, and manual-versus-assisted review time has not been measured. P8-3 (assumptions/limits) and P8-5 (demo script) meet their file-based acceptance. P8-1, P8-2 and P8-4 remain pending. No numerical saving or real merchant improvement was invented.

The Windows launcher passed a real local offline run. Local report readiness is true, optional AI configuration exists but the exposed key needs private rotation, and both notification destinations are absent. Current historical free-model evidence and provider fallback are preserved. Actual hosted execution is still blocked by the account lock. OWNER-ACTIONS consolidates the owner's work without blocking local generation.

Strict acceptance is 41/56 tasks, 82.3% weighted. P9 remains a separate independent reviewer task, with a copyable request and reproduction checklist in AUDIT-HANDOFF. No release tag or independent verification is claimed by this builder checkpoint.

A fresh extracted source distribution passed locked installation, offline doctor, four-format report generation and frozen inspect; output is in p8-package.txt. The wheel contains the new operational modules and packaged HTML. An initial archive check found redundant .env.example copies from ignored local test checkouts (no credentials); explicit source-root selection excludes all .tools paths, private .env and reports. Rebuilt archive contents passed the exclusion check. The pinned Google SDK emitted nonfatal SyntaxWarnings on first import in that fresh environment; commands still exited zero. Upstream dependency maintenance can be assessed by the independent reviewer without changing the verified pin during this handoff.

Final builder gates: Ruff lint and formatting pass, strict mypy passes for 38 source files, both workflows pass actionlint, 222 tests pass with 95% coverage, local Markdown links resolve, and genuine operational history remains byte-identical across the suite. Secret scanning includes the publication set and nested OOXML files. These checks do not certify hosted Ubuntu execution or independent P9 acceptance.
