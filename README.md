# Climate Investment AI Agent in Equity and Bond Markets

**A source-grounded, human-reviewed research workflow for HHFinAi.**

Version **0.1.0** · **20 analyst roles** · **7 routed workflows** · Python standard library · No autonomous trading

This project turns the user-supplied **897-page CFA UK climate-investing curriculum** into operational analyst handoffs. The source remains the methodological foundation. Original workflow engineering, calculation implementations, validation rules and synthetic examples are separately identified as additions—not presented as CFA-authored software or a substitute for the curriculum.

**GitHub Desktop edition:** complete local repository package prepared for `HHFinAi/climate-investment-ai-agent-in-equity-and-bond-markets`, private. Start with [START_HERE_GITHUB_DESKTOP.md](START_HERE_GITHUB_DESKTOP.md) to copy, commit and publish using the desktop app. No terminal or GitHub CLI is needed for that publishing route. Remote publication is performed by the repository owner; it was not performed in the authoring environment.

## What runs, and what does not

The executable engine validates a research request, selects the correct instrument branches, emits agent work packets, validates structured results, blocks out-of-order handoffs, tracks revisions, invalidates dependent work, and produces a review packet. An external host AI agent or human performs the research using the included role instructions and actual available data tools.

There is **no embedded LLM, broker connection, live climate/market feed, scheduler or automatic trade execution**. `demo` runs deterministic synthetic fixtures to exercise the workflow; it is not a live investment-analysis run. Software tests are not evidence of alpha, scientific calibration, source entailment or regulatory compliance.

## The workflow

The source's Figure 7.12 (PDF page 546, chapter 7 printed page 50) connects scenario pathways, economic shocks, issuer/asset value streams and financial impacts. This package operationalises that sequence with explicit intake and review controls.

```mermaid
flowchart TD
    M[Mandate and instrument scope] --> E[Evidence and entity boundaries]
    E --> S[Science and materiality]
    E --> D[Policy and disclosure context]
    E --> C[Emissions and targets]
    S --> P[Physical risk and adaptation]
    S --> T[Transition and opportunities]
    D --> T
    C --> T
    S --> Q[Scenarios and model risk]
    D --> Q
    P --> F[Financial transmission and double-counting check]
    T --> F
    Q --> F
    F --> EQ[Equity valuation]
    F --> CB[Corporate credit]
    F --> SB[Sovereign and municipal debt]
    F --> SC[Structured credit]
    F --> LB[Labelled-debt integrity]
    EQ --> PF[Portfolio and constraint review]
    CB --> PF
    SB --> PF
    SC --> PF
    LB --> PF
    PF --> ST[Stewardship and monitoring plans]
    ST --> RT[Independent challenge]
    RT --> IC[Investment memo]
    IC --> H[Human research decision]
```

Equity and bond outputs remain separate: equity work focuses on cash flows, capital allocation, valuation and dilution; credit work additionally focuses on obligor/guarantor, repayment, security, maturity, refinancing, rates/spreads and recovery. Labelled bonds receive **both credit analysis and label/impact analysis**. Corporate carbon intensity is not mixed with sovereign GDP-based intensity.

## Run the local tests and synthetic demo

From this folder, with Python **3.10 or later**:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/check_repository.py
python3 -m climate_agent demo --workflow multi-asset --out runs/demo-01
python3 -m climate_agent status --run runs/demo-01
python3 -m climate_agent report --run runs/demo-01 > runs/demo-01/review-packet.md
```

Choose a new output directory for each run; existing directories are never overwritten. No packages, API keys or network access are required for the tests and synthetic demo. On systems whose Python executable is named `python`, substitute that command.

## Run an actual research workflow

Start from `examples/research-request-template.json`, replace the clearly marked placeholders, adopt or change the example freshness policy, and register permitted issuer, market, scenario and instrument evidence. Do not leave placeholder identity or mandate terms unresolved.

```bash
python3 -m climate_agent plan --workflow equity --input your-request.json --out runs/issuer-01
python3 -m climate_agent next --run runs/issuer-01
# The host AI/human reads the packet, performs research, and saves an artifact.
python3 -m climate_agent submit --run runs/issuer-01 --agent mandate --artifact mandate-result.json --revision 0
python3 -m climate_agent next --run runs/issuer-01
```

Repeat for the ready agents; use the latest revision from `next` or `status`. Consult `examples/mandate-artifact.json` for the JSON format, but copy `run_id` and `input_digest` from your actual work packet rather than the example. A role with a material gap returns `NEEDS_DATA`, not invented values. The detailed host procedure and evidence rules are in `AGENTS.md` and `references/data-contract.md`.

Once all work is complete and independent material exceptions are resolved, a **human** may record a research decision:

```bash
python3 -m climate_agent review --run runs/issuer-01 --reviewer "Your name" --decision APPROVE_RESEARCH --rationale "Describe the checks actually performed" --attest-human-review --revision 15
```

The revision above is illustrative; replace it with the run's current value. The tool records an attestation, not authenticated identity or trade authority. Demo/source-study runs cannot be approved as investment research.

## Choose the right route

| Workflow | Instrument scope | Additional branch |
|---|---|---|
| `equity` | Listed equities, including listed real-asset businesses | Equity strategy and valuation |
| `corporate-bond` | Unlabelled corporate debt | Corporate credit and price stress |
| `sovereign-bond` | Unlabelled sovereign debt | Fiscal/external, currency and rate/credit analysis |
| `municipal-bond` | Unlabelled municipal/sub-sovereign debt | Geographic tax/revenue and recourse analysis |
| `labelled-bond` | Labelled corporate, sovereign or municipal bonds | Underlying credit branch **plus** label review |
| `structured-credit` | Unlabelled structured credit | Collateral/waterfall diligence; specialist pricing required |
| `multi-asset` | Any supported mixture, including labelled structured debt | Only applicable branches are enabled |

## Repository guide

`WORKFLOW.md` describes the operational sequence. `agents/` holds source-linked role contracts; `workflows/` contains directed dependencies; `climate_agent/` contains the runnable engine and calculation helpers; `schemas/` describes handoff envelopes; `references/` explains source provenance and model limits; `templates/` contains analyst output structures; `examples/` contains fictional inputs and a worked arithmetic illustration; `tests/` and `.github/workflows/` contain quality checks.

Use `SKILL.md` plus the complete adjacent folder contents in a filesystem-enabled agent host. Do not copy only the entry-point file and lose its dependencies. Automatic installation/activation depends on the host and has not been certified for any specific product. In text-only environments the prompts can be applied manually, but no Python state or test gate is then enforced.

## Publish with GitHub Desktop

Follow [START_HERE_GITHUB_DESKTOP.md](START_HERE_GITHUB_DESKTOP.md): create the local repository, copy the extracted project's **contents into its root**, review and commit, then publish to the personal **HHFinAi** account with **Keep this code private** selected.

Preserve the local `.git/` directory. Include the supplied `.github/`, `.gitignore` and `.gitattributes` files; they may be hidden by your file manager. Do not upload the ZIP or the source CFA PDF. The guide also covers importing into an already-created remote without replacing its history.

The script `scripts/publish_github.py` is a separate, optional **initial-creation CLI route**. It is not used in the Desktop workflow and refuses an existing remote. See [PUBLISHING.md](PUBLISHING.md) for that alternative and recovery limits.

## Source and limitations

See `references/SOURCE_MAP.md` for the ten-chapter map, reviewed operational anchors and one-indexed PDF page convention. The source includes historical policies, standards and market examples; these are not current verification. Quantitative helpers use supplied assumptions and do not turn emissions into default probabilities or precise physical losses.

See `VALIDATION.md` for checks actually run and checks not performed. The source PDF and page images are excluded. There is no CFA UK/CFA Institute affiliation or endorsement. No open-source licence has been selected; see `NOTICE.md`.
