# Institutional-quality climate investment research: controls you can inspect

**Built for institutional-quality equity and bond research through traceable evidence, explicit assumptions, controlled handoffs and human review.** This describes the project's implemented research-process controls, not an independent audit, certification, or demonstrated institutional adoption.

## What institutional quality means here

An investment committee should be able to investigate the source behind a claim, distinguish evidence from judgment, inspect the assumptions driving valuation, identify superseded results and review the recorded research decision. This workflow organizes those records rather than presenting only a generated narrative.

The [data contract](../references/data-contract.md), [state engine](../climate_agent/workflow.py) and [operating instructions](../AGENTS.md) distinguish machine-enforced checks from responsibilities that remain with an analyst. Instruction compliance, structural validation and substantive verification are not equivalent.

## Claim-to-control matrix

| ID | Claim | Implementation and named tests | Boundary |
|---|---|---|---|
| IQ-01 | Evidence references are traceable. | [`validate_artifact`](../climate_agent/validation.py); `test_unknown_evidence`, `test_current_fact_unreviewed_rejected` in [tests](../tests/test_validation.py). | A valid reference and review flag do not prove source truth or citation support. |
| IQ-02 | Facts, assumptions and calculations are distinguishable. | [`validate_artifact`](../climate_agent/validation.py); `test_no_fact_from_textbook_alone`, `test_no_fact_from_assumption` in [tests](../tests/test_validation.py). | Checks use declared categories; semantic misclassification remains possible. |
| IQ-03 | Current facts use explicit evidence-date and primary-policy rules. | [`validate_artifact`](../climate_agent/validation.py); `test_stale_market_fact`, `test_current_fact_requires_freshness_policy`, `test_policy_requires_primary_record` in [tests](../tests/test_validation.py). | Freshness thresholds are user policy; recency does not prove legal applicability. |
| IQ-04 | A run preserves its input and instruction context. | [`load_state`](../climate_agent/workflow.py); `test_frozen_input_change_detected`, `test_wrong_input_digest_rejected` in [tests](../tests/test_workflow.py). | Frozen metadata is not automatic archival of source files or reproducible LLM output. |
| IQ-05 | Revisions invalidate downstream conclusions and prior review. | [`submit`](../climate_agent/workflow.py); `test_resubmit_invalidates_descendants`, `test_revision_invalidates_human_review` in [tests](../tests/test_workflow.py). | Controls apply through the engine; direct local editing is outside controlled submission. |
| IQ-06 | Declared material gaps and review issues can block approval. | [`human_review`](../climate_agent/workflow.py); `test_needs_data_stops_descendants`, `test_material_issue_blocks_approval` in [tests](../tests/test_workflow.py). | Undeclared gaps still require a competent analyst to identify them. |
| IQ-07 | Equity, credit and labelled-debt research are routed separately. | [`select_nodes`](../climate_agent/workflow.py); `test_labelled_sovereign_uses_sovereign_not_corporate_credit`, `test_label_requires_additional_route` in [tests](../tests/test_workflow.py). | Routing does not replace credit, legal or specialist structured-pricing diligence. |
| IQ-08 | Quantitative guardrails reject specified modelling errors. | [`validate_treatments`](../climate_agent/calculations.py); `test_duplicate_climate_treatment`, `test_scenario_weights_no_renormalisation`, `test_rate_spread_separated` in [tests](../tests/test_calculations.py). | These are scoped arithmetic/identity checks, not a complete model-risk or semantic audit. |
| IQ-09 | Human research decisions are recorded without trade authority. | [`human_review`](../climate_agent/workflow.py); `test_human_attestation_required`, `test_demo_cannot_be_approved`, `test_explicit_no_execution` in [tests](../tests/test_workflow.py). | Attestation is not authenticated identity, independent assurance or trade authorization. |

The [machine-readable claims register](claims.json) names code and test references. The documentation checker verifies that these references exist; it does not establish that any test is sufficient to prove a broad quality claim.

## Validation and deployment

See [current validation scope](VALIDATION_2026-09-23.md), the [original software validation](../VALIDATION.md), and the live CI badge in the [README](../README.md). Synthetic regression tests are not evidence of return prediction, calibrated climate probabilities, credit-model accuracy, legal compliance, source entailment or commercial adoption.

The package does not claim independently audited evidence, immutable records, authenticated reviewer identities, regulatory approval, production certification, CFA UK/CFA Institute endorsement, client AUM or investment outperformance. Before production, evaluate data licensing, completeness, source interpretation, security, retention, identity controls and actual model-generated research quality.

Start with the [evidence audit walkthrough](EVIDENCE_AUDIT.md) and reproduce the tests before assessing the analytical assumptions.
