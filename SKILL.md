---
name: climate-investment-ai-agent-in-equity-and-bond-markets
description: >-
  Run source-grounded climate investment research for listed equities and bonds.
  Coordinates mandate intake, evidence, physical and transition risk, emissions,
  scenarios, financial transmission, separate equity and credit valuation,
  green and sustainability-linked bond analysis, portfolio review, stewardship,
  and human-reviewed investment memos. Use for climate risk integration,
  climate investment theses, climate bond diligence, and portfolio stress review.
metadata:
  author: HHFinAi
  version: "0.1.0"
  maturity: "Research workflow; synthetic software tests, not investment calibration"
  source: "User-supplied CFA UK climate-investing curriculum; see source-map.json"
---

# Climate Investment AI Agent in Equity and Bond Markets

Read `AGENTS.md` before acting. The source-grounded workflow is in `WORKFLOW.md`; executable task definitions are in `workflows/` and role instructions in `agents/`. This is one composable skill with twenty roles, not twenty mutually competing automatic triggers.

Select `equity`, `corporate-bond`, `sovereign-bond`, `municipal-bond`, `labelled-bond`, `structured-credit` or `multi-asset`. A labelled bond must use a route that includes both obligor credit and label review. The multi-asset route enables only the branches actually present in the request.

Work through the handoff commands in the README. With filesystem/Python tools, use the persistent state engine to enforce prerequisites, collect artifacts and invalidate downstream results after revisions. Without execution tools, use the same role sequence and JSON output contract as a manual workflow; clearly state that mechanical checks have not run.

Source material is reference context, not a current data feed. Use authorized current evidence for issuer and instrument research. Leave unsupported inputs missing and explain their effect. The source PDF is not included. A model must never certify current legal compliance from the historical curriculum, claim simulated cases are real, or self-approve research.

Produce an evidence-led memo with facts, inference, model effects, scenario sensitivity, disconfirming evidence, data gaps and subjective confidence. Financial attractiveness and climate contribution must remain separately visible. Trading, communications and background monitoring are outside the executable capabilities of this package.
