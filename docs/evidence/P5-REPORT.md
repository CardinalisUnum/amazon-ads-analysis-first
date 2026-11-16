# P5 gate report

P5 is complete. The owner authorized this phase on 2026-11-16. P6 requires a new approval. Hosted CI task P1-5 remains open because the provider account is locked.

## Acceptance evidence

| Task | Evidence |
|---|---|
| P5-1 schema and prompt | Typed Draft/Claim/Note models and packaged prompt. Builder reviewed supplied facts, permitted review choices, unknown causes/targets/dates, wording and field limits. See COMMENTARY.md. |
| P5-2 real batch | Normal CLI parsed a real gemini-3.5-flash-lite response for all ten products. Ten notes passed, zero templates and zero guard rejections. See p5-gemini.json. |
| P5-3 number guard | Product/week/metric/unit/direction bindings, Decimal half-up rounding, EUR, percentages, percentage points and injected hallucination tests pass. Number-guard coverage is 100%, including branches. |
| P5-4 offline fallback | --no-ai yields ten deterministic template notes without reading credentials or making requests. The numerical CSV matches its existing golden file. |
| P5-5 failures and quota | Mocked quota exhaustion and recovery, long provider delays, authentication/network/schema errors and per-product failures pass. An actual SDK HTTP transport confirms only one request per adapter call, with retries disabled. |
| P5-6 source labels | Every report.json note shows SAMPLE DATA, source label and reason. Guard failures record stable issues and numeric tokens, while other valid products retain their accepted notes. P6 will show these labels in the four visual formats. |

## Verification

```text
uv sync --locked                         exit 0, 46 packages resolved
uv run ruff check .                      All checks passed!
uv run ruff format --check .              47 files already formatted
uv run mypy --strict src/                 no issues in 20 source files
uv run pytest --cov=src/adsreport          180 passed, 98% total coverage
KPI / rules / number guard coverage       100% each, including branches
Existing Hypothesis identities           200 passing examples each
generate-sample and configuration checks  exit 0
normal offline CLI                       exit 0, ten labelled templates
wheel build                              exit 0, packaged prompt present
```

Full captured output is p5-local.txt. A separate Windows checkout with CRLF conversion verifies all 180 tests and byte-identical offline JSON/CSV. The wheel contains 26 package/metadata files with its prompt and no local cache or credentials. See p5-checkout.txt.

The successful manual live verification took 6.066 seconds end to end on this local environment. Two earlier requests received HTTP 400 for serving-schema complexity, with the first normal CLI producing ten labelled fallback notes. The serving schema was simplified before the successful request. The manual request history is one parsed response in three requests during implementation. This is no scheduled reliability claim and no measurement of human time saved.

Live and offline runs preserve identical product metrics, rules, source hashes and configuration hashes. The CSV remains byte-identical to the P3 golden file. No financial arithmetic moved into AI code.

## Self-review and resolved findings

The serving schema initially exceeded provider constraints. It now retains object types, required fields and controlled choices while leaving date/length constraints to local validation. Each product is validated independently, preserving good notes when another entry fails.

The SDK transport test exposed distinct Interactions and legacy error hierarchies. The adapter now supports their public status/body attributes without private imports. It keeps provider text and credentials out of stored outcomes. SDK retries and automatic continuation are disabled, and one application quota retry honors the longer provider delay in waits of at most sixty seconds. Other service failures use templates immediately.

The official google-genai SDK is the only added direct runtime dependency. uv.lock captures its dependencies. The guard uses explicit canonical metric labels and a small set of permitted review actions. This avoids free-prose numeric and metric-name ambiguity. AI chooses facts and review focus, and Python renders the sentences. Causes, targets and review dates are deliberately unknown, with low confidence. The guard does not certify causal interpretation or the usefulness of the selected facts.

The builder traced request success, network/quota/schema failures, product-local rejection, offline behavior and staged publication. Automated tests, diff review, package inspection and a publication-candidate secret scan passed. This self-review does not replace P9's independent release audit.

## Gate and remaining work

All six P5 tasks are complete. Overall completion is 32 of 56 tasks and 63.7% weighted. STATUS.md contains the full phase/task table. RESUME.md contains the contracts, reproduction commands and P6 implementation order for another agent.

The P5 [hosted run](https://github.com/CardinalisUnum/amazon-ads-analysis-first/actions/runs/43869282957) executed zero runner steps and returned the same account billing-lock annotation. See p5-hosted-ci.json. This phase claims local verification only. Billing-unlinked Gemini status is owner-attested, without independent billing-admin access. Official pricing and schema links are in COMMENTARY.md and decisions.md. The key shared in chat must be rotated privately before unattended operation.

Four visual outputs and native PDF support remain P6. Human approval/delivery, email/Discord evidence and genuine scheduled history remain P7. Measured manual versus assisted review effort remains P8. No prospect delivery or production schedule has been performed.

Pause for the owner's P6 approval after committing and pushing this checkpoint.
