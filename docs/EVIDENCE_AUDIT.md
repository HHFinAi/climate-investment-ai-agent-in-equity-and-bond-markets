# Traceable evidence and auditable climate investment research

The Climate Investment AI Agent records a reviewable chain from registered evidence to declared findings, role outputs and human research review. This guide explains what an institutional evaluator can inspect and what remains the deploying firm's responsibility.

## The evidence chain

**Registered source → dated/entity-scoped evidence record → finding and calculation basis → agent artifact → research packet → recorded human review.**

Every factual or calculation finding must refer to evidence IDs registered in the run; methodology references are separate. Declared assumptions and inferences remain distinguishable from empirical facts. The validator checks these structural relationships, not whether the prose correctly interprets a document. See the [data contract](../references/data-contract.md) and [validation implementation](../climate_agent/validation.py).

| Layer | Recorded fields or behavior | Review question |
|---|---|---|
| Source record | `id`, `kind`, `title`, `locator`, `summary`, `entity_scope`, `as_of`, `retrieved_on`, `review_status` | Is this the correct issuer, instrument, period and source? |
| Evidence review | `VERIFIED` records require `reviewed_by` and `reviewed_on` | Who attested to reviewing it, and what did that review establish? |
| Finding | `kind`, `time_basis`, `topic`, `evidence_ids`, `source_refs`; calculations also need `calculation_basis` | Is the conclusion a fact, judgment, assumption or calculation? |
| Research context | `frozen`, `frozen_digest`, `run_id`, role instructions and methodology map | Which inputs and instructions were in force? |
| Revision history | Superseded artifacts, submission events, artifact digests, descendant invalidation | What changed, and which dependent conclusions need to be rebuilt? |
| Human review | Named attestation, decision, rationale, timestamp and packet digest | Was this exact packet reviewed, and are material issues resolved? |

Units, reporting periods, scenario versions and calculation conventions must also be preserved by the host analyst in the supplied context. A nonempty field is not proof of correct analytical interpretation.

## Inspect a complete synthetic run

From the repository root, select a new output directory:

```bash
python -m climate_agent demo --workflow multi-asset --out runs/audit-demo
python -m climate_agent report --run runs/audit-demo > runs/audit-demo/review-packet.md
```

Open `runs/audit-demo/state.json`. Check `frozen.request.evidence`, trace a finding's `evidence_ids` to that register, inspect its declared kind/basis, then inspect `events` and `review`. The demonstration ends `DEMO_COMPLETE_NOT_APPROVED`; it supplies **no real issuer research or human approval**. Existing directories are not overwritten.

The [worked arithmetic example](../examples/WORKED_EXAMPLE.md) provides a separate fictional equity-and-bond illustration. Tests in [test_validation.py](../tests/test_validation.py) and [test_workflow.py](../tests/test_workflow.py) exercise the failure paths as well as successful handoffs.

## Corrections and refreshes

Changing an analytical result through `submit` archives the affected prior artifacts and invalidates downstream analysis and prior review. Revision numbers reject stale submissions. Adding or changing source evidence or the mandate requires a new frozen run; cite the earlier run in the new context. See [workflow.py](../climate_agent/workflow.py).

## Control boundaries

The records are local JSON, not immutable storage or an independently assured audit log. SHA-256 digests identify a frozen context and recorded artifacts; a person with write access can alter local files and recompute hashes. The software does not authenticate reviewers, enforce organizational access segregation, or automatically capture every external document's original bytes. Re-running an LLM is not guaranteed to reproduce its prior output.

`VERIFIED` is a submitting analyst/host review attestation, not independent source verification. Unknown or omitted risks, weak evidence, misclassified statements, source conflicts and misleading citations still require substantive review. The independent-challenge role is a workflow role; the engine cannot prove the reviewer is independent.

A deploying institution should evaluate licensed source capture, retention, access controls, backups, identity, model-output evaluation and review procedures before production use. No securities orders, votes or external communications are sent by this package.

[Institutional-quality controls](INSTITUTIONAL_QUALITY.md) · [FAQ](FAQ.md) · [Main project](../README.md)
