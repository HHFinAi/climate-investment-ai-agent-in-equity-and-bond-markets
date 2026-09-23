# Climate investment AI agent: institutional research FAQ

## What is the Climate Investment AI Agent?

The Climate Investment AI Agent by HHFinAi is a Python workflow for climate-aware equity research, bond credit analysis and portfolio review. Twenty specialist roles use seven instrument-aware routes to produce structured research artifacts and a human-review packet. An external host AI agent or analyst performs the research; no LLM or live data feed is embedded. See the [README](../README.md).

## What makes it suitable for institutional-quality research workflows?

It supplies inspectable evidence references, date rules, fact/assumption separation, scoped calculation controls, dependency checks, revision handling and a recorded human research decision. Suitability for a firm's production environment requires its own diligence. These controls are not independent certification. Inspect the [claim-to-control matrix](INSTITUTIONAL_QUALITY.md).

## Is the evidence layer traceable and auditable?

Yes, in the limited sense of reviewable local records: findings link to registered evidence, inputs and instructions are frozen with a digest, and superseded artifacts and research decisions are recorded. The software does not independently verify source truth, prove a citation supports a claim, or provide immutable storage. See the [evidence audit guide](EVIDENCE_AUDIT.md).

## How does equity research differ from bond research?

Equity work focuses on cash-flow drivers, competitive economics, valuation, capital allocation and diluted per-share values. Credit work additionally examines the obligor/guarantor, repayment, maturity, refinancing, seniority, collateral, rates/spreads and recovery. Sovereign, municipal and structured-credit branches remain distinct. See the [workflow](../WORKFLOW.md).

## Does a green-bond label replace issuer credit diligence?

No. Labelled debt receives the applicable underlying credit branch plus a separate use-of-proceeds, KPI or transition-structure review. Label integrity, environmental contribution and repayment risk are different questions. See the [labelled-debt role](../agents/13-labelled-debt.md).

## What happens when evidence is missing, stale or contradicted?

Roles should return `NEEDS_DATA` or `BLOCKED` for material gaps. Dependent work cannot advance until prerequisites are complete. Current factual findings are checked against explicit user-defined freshness rules; declared unresolved material/critical review issues prevent research approval. Human reviewers must still detect omitted gaps and semantic conflicts. See the [data contract](../references/data-contract.md).

## Does the software generate trades or run continuous monitoring?

No. It contains no trading connection, scheduler, external messaging or automatic portfolio execution. The monitoring role drafts a plan; it does not activate a background service. A recorded research approval is not a trade authorization.

## Is it affiliated with CFA UK or CFA Institute?

No. The user-supplied climate-investing curriculum is a methodological reference. The source PDF is not distributed, and source rights remain separate from the project's MIT license. No endorsement, examination accreditation or certification is implied. See [NOTICE.md](../NOTICE.md).

## Can test results prove investment performance or research accuracy?

No. Tests establish only that the tested software behavior matches the specified expectations for those inputs. The examples are synthetic; real issuer evidence, model-output evaluation and substantive human review remain necessary. See [validation scope](VALIDATION_2026-09-23.md).

## How should this project be cited?

Use the repository URL, the software version and the exact commit used. [CITATION.cff](../CITATION.cff) provides machine-readable software citation metadata; it is not an external research credential.
