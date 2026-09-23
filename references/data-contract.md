# Data and handoff contract

## Run inputs
The run request identifies mode, analysis date, mandate, entities, instruments, evidence and an explicit freshness policy. Each instrument maps to an entity and has its own asset class, currency and label. The base currency is a reporting choice; the engine does not automatically convert currencies. Fill every REPLACE marker in the template; a role must flag material missing mandate terms before proceeding.

`demo` permits fictional fixtures and cannot receive research approval. `source_study` explains historical methods and cannot receive research approval. `research` is intended for actual analyst work and requires verified, appropriately dated evidence for factual findings. A source record's VERIFIED flag means the submitting user/host attests review; the software does not independently verify the source's truth or an analyst's identity.

## Evidence fields
Each record requires `id`, `kind`, `title`, `locator`, `summary`, `entity_scope`, `as_of`, `retrieved_on` and `review_status`. Verified records additionally require `reviewed_by` and `reviewed_on`. Preserve the reporting period, unit and calculation/estimation basis in the summary or structured context. `as_of` is the date relevant to the observation, not merely today's download date; annual emissions retain their reporting vintage.

Kinds are `issuer_disclosure`, `market_data`, `scenario_data`, `policy_primary`, `assumption`, `synthetic` and `methodology`. A textbook method or a forecast assumption cannot be the evidence for an issuer fact. Synthetic evidence is confined to demo mode. Policy applicability findings require primary-policy evidence when stated as current facts. The host must additionally check provision, jurisdiction, scope, legal status and effective date; the engine cannot interpret legal effect from a date alone.

All date fields are YYYY-MM-DD. Future observations/retrieval relative to the run date are rejected to prevent look-ahead contamination. Freshness thresholds are an explicit **implementation policy**, not CFA requirements. The sample values are illustrative; change them to match the mandate. A current factual finding without a freshness rule is rejected. Historical facts may use older, reviewed evidence but must be labelled historical.

## Agent output
Copy `run_id` and `input_digest` from the current work packet into every result; outputs from other runs or frozen inputs are rejected. Each result uses `schemas/agent-output.schema.json` and contains status, summary, source_refs, evidence_ids, findings, data, assumptions, gaps, uncertainties and a confidence object. Each role specifies its required data keys in `agents/registry.json`. Values can be structured tables/objects or explanatory text. Do not fill required keys with reassuring boilerplate; absent material inputs require NEEDS_DATA.

Finding kinds separate `source_method`, `fact`, `inference`, `assumption` and `calculation`. Each finding specifies `time_basis` (`historical`, `as_of`, `scenario`, `timeless`) and topic. Empirical facts must be timed historical or as_of; scenario and timeless statements must not be presented as empirical facts. Factual/calculation entries need registered evidence; calculations also describe `calculation_basis`. Method references establish conceptual provenance, not the underlying numbers. Inferences must expose assumptions and uncertainties even though the engine cannot test semantic reasoning.

The confidence value lies between zero and one, has an explicit basis, and must set `calibrated: false`. It is not a scenario probability or a statistically measured forecast score.

## Special result structures
`financial-transmission.data.risk_treatment_register` is a list of `{risk_id, treatment}` where treatment is cash_flow, discount_rate, terminal, collateral or disclosure_only. Identical entries and cash-flow/discount-rate use for the same risk ID are rejected. Economically different effects need different IDs and explanations; ID changes must not disguise double counting.

`scenarios.data.scenario_register` contains unique IDs, names and optional `probability`. Leave all probabilities null unless explicitly justified. If probabilities are supplied, each scenario needs one and they must sum to one without renormalisation.

`red-team.data.issues` contains `{severity, description, resolved}`; resolved issues also need a resolution. Severity is CRITICAL, MATERIAL or MINOR. Any unresolved critical/material issue requires a BLOCKED recommendation and prevents research approval.

## Changes and persistence
Research inputs and role instructions are frozen with a SHA-256 digest at plan creation. New evidence or a new mandate requires a new run, with the old run referenced in context. Corrections to analysis with unchanged evidence use resubmission: prior artifacts are archived and all downstream analysis plus prior review invalidated. Revision numbers prevent concurrent stale writes. This is local traceability, not tamper-proof regulated recordkeeping or an authenticated approval system.

Research approval additionally requires at least one reviewed issuer-disclosure record. This is a minimum gate, not proof that all issuer/instrument inputs or analytical conclusions have been verified.
