# Agent workflow — climate investment in equity and bond markets

## 1. Mandate before metrics
The curriculum concludes with client needs and reporting; operational execution starts there. Specify whether the investor seeks financially material climate-risk integration, portfolio alignment, financing solutions or explicit impact. These are not equivalent objectives. Record the issuer, instrument, legal structure, currency, benchmark and investment horizon. Source: chapter 10.1.1 (PDF 845–849), chapter 9.1.1 (PDF 732).

## 2. Establish a common evidence base
The evidence agent creates a provenance and entity map. Science/materiality, disclosure, and emissions work can then proceed in parallel. Separate source-era methodological context from dated real issuer observations. Capture missingness rather than treating absent emissions, facility data or debt terms as neutral. Source: chapter 5.1.1–5.1.2 (PDF 317–320), chapter 7.2.4 (PDF 584).

## 3. Analyse physical and transition channels
Physical risk requires hazard, exposure and vulnerability, including insurance, adaptation and residual loss. Transition work examines policy/legal, technology, market and reputation effects and opportunities in resource efficiency, energy, products/services, markets and resilience. Corporate decarbonisation and selling climate solutions are separate dimensions. Source: chapters 1–2, chapter 4.1 (PDF 220–226), chapter 7.1.2 (PDF 503–505).

## 4. Define scenarios, not forecasts
Choose coherent, versioned scenarios appropriate to the holding period and the issuer's asset life. Report model resolution, parameter uncertainty and missing financial transmission functions. Do not convert a temperature label or qualitative narrative into a probability. Modelled financial paths are assumptions unless supported by the supplied scenario data. Source: chapter 5.2 (reviewed PDF 351–358).

## 5. Build a financial transmission bridge
Follow Figure 7.12: scenario pathways → economic shocks → exposure/action/competition → financial impacts. Bridge to revenues, cash operating costs, capex, working capital, assets, liabilities and financing. Every risk/opportunity has a persistent ID and explicit treatment location. Avoid charging the same effect in both cash flow and the discount rate. Source: chapter 4.1.1 (PDF 225–226), chapter 7.1.5 (PDF 544–551), Figure 7.12 (PDF 546).

## 6. Branch by the security's economics
**Equity:** competitive economics, climate-adjusted cash flows, comparable/absolute valuation, terminal assumptions, capital allocation and diluted per-share values. Include a no-climate-adjustment baseline and explain the deltas.

**Corporate credit:** issuer/guarantor, seniority, collateral, covenant and financing structure; operating/financial resilience; default/recovery; risk-free versus credit/liquidity spread. A climate assessment is not an external credit rating.

**Sovereign/municipal:** public-budget versus whole-economy emissions, production/consumption basis, fiscal/external resilience, local/foreign currency, and the geography of productive assets or pledged tax/revenue streams. Keep analysis descriptive and financial, not an evaluative political ranking.

**Labelled debt:** retain the appropriate credit branch and add use-of-proceeds or KPI/contract analysis, allocation/impact reporting and verification. Avoided emissions, additionality, legal recourse and overall issuer risk are different questions.

**Structured credit:** require collateral and waterfall diligence. No claim that the bundled plain-vanilla bond helper prices a complex tranche.

Source: chapter 7.1–7.2; chapter 8 is supporting context on private/underlying asset differences, not an additional private-market execution mandate.

## 7. Reconcile the portfolio and engagement plan
Bring top-down scenario exposure together with bottom-up issuer work. Reconcile holdings, currencies and denominators. Keep corporate and sovereign metrics separate. Show missing-data coverage, unintended sector/geography tilts, mandate constraints and attribution. A sale of a high-emitting security can change the portfolio metric without changing the issuer's emissions. Define measurable engagement objectives and monitoring triggers. Source: chapters 6, 9 and 10 (see source map).

## 8. Challenge, document and review
An independent challenge role checks provenance, unit consistency, unsupported inference, scenario consistency, valuation double counting, label/credit conflation and mandate adherence. Material/critical exceptions block approval. The memo preserves dissent, assumptions, financial sensitivities and separate climate contribution. A human reviews the full packet. No tool sends orders, communications or votes.

The role partition, DAG, JSON envelope, severity levels, review gates and revision mechanics are **IMPLEMENTATION_EXTENSION** choices for this project, not instructions quoted from CFA UK.

## Role catalogue

| # | Agent | Decision responsibility | Methodology anchors |
|---|---|---|---|
| 01 | `mandate` | Turn the investor request into a specific research mandate without inventing climate objectives. | CFA-10-MANDATE, CFA-09-PORTFOLIO |
| 02 | `evidence` | Build the common evidence base and prevent entity, date, unit and scope mismatches. | CFA-05-DATA, CFA-07-CREDIT |
| 03 | `science-materiality` | Identify which climate mechanisms could matter for this investment and at what horizon. | CFA-01-FRAME, CFA-02-RISK |
| 04 | `disclosure-policy` | Translate relevant disclosure and policy context into dated analytical inputs, not political judgments. | CFA-03-DISCLOSURE, CFA-10-REPORT |
| 05 | `emissions` | Produce comparable climate metrics without confusing footprint, risk and real-world impact. | CFA-05-CARBON, CFA-05-DATA, CFA-07-SOVEREIGN |
| 06 | `physical-risk` | Translate location-specific hazards and adaptive capacity into investment-relevant exposures. | CFA-02-RISK, CFA-04-OPPORTUNITY, CFA-05-DATA |
| 07 | `transition` | Assess how business models and competitive economics change under specified transitions. | CFA-04-OPPORTUNITY, CFA-04-TRANSMISSION, CFA-07-EQUITY |
| 08 | `scenarios` | Select coherent what-if pathways appropriate to the mandate rather than predict one climate future. | CFA-05-SCENARIO, CFA-07-FLOW |
| 09 | `financial-transmission` | Connect the shared climate analysis to financial models through explicit and non-duplicated channels. | CFA-04-TRANSMISSION, CFA-07-FLOW, CFA-07-VALUATION |
| 10 | `equity` | Produce an equity-specific climate-integrated valuation, not an ESG score relabelled as a price target. | CFA-07-EQUITY, CFA-07-VALUATION |
| 11 | `corporate-credit` | Evaluate repayment capacity, legal recourse and price risk separately from climate labels. | CFA-07-CREDIT, CFA-07-VALUATION |
| 12 | `sovereign` | Assess sovereign financial exposures without turning country analysis into political rankings. | CFA-07-SOVEREIGN, CFA-07-CREDIT |
| 13 | `municipal` | Connect geographically concentrated climate exposures to the bond’s actual repayment source. | CFA-07-SOVEREIGN, CFA-07-CREDIT |
| 14 | `labelled-debt` | Assess label integrity and climate contribution alongside, not instead of, obligor credit quality. | CFA-07-LABEL, CFA-07-CREDIT |
| 15 | `structured-credit` | Trace physical and transition risk through collateral and contractual structure. | CFA-07-CREDIT, CFA-08-CONTEXT, CFA-02-RISK |
| 16 | `portfolio` | Aggregate decision-relevant exposures while preserving financial and climate objectives separately. | CFA-09-PORTFOLIO, CFA-05-CARBON, CFA-07-SOVEREIGN |
| 17 | `stewardship` | Convert material research gaps into measurable issuer-engagement objectives. | CFA-06-ENGAGE, CFA-10-REPORT |
| 18 | `monitoring` | Define how the decision should be revisited as evidence and exposures evolve. | CFA-06-ENGAGE, CFA-10-REPORT, CFA-09-PORTFOLIO |
| 19 | `red-team` | Challenge the thesis and enforce evidence, scope and arithmetic controls before investment review. | CFA-05-DATA, CFA-05-SCENARIO, CFA-07-VALUATION, CFA-10-REPORT |
| 20 | `investment-memo` | Synthesize the reviewed work into a decision document accountable to the mandate. | CFA-10-MANDATE, CFA-10-REPORT, CFA-09-PORTFOLIO |

## Handoff and failure states

`PENDING → COMPLETE` advances downstream dependencies. `NEEDS_DATA` and `BLOCKED` retain the exact missing/contradictory item and stop downstream work. A revised artifact archives the previous output and invalidates descendants. A new input/evidence universe requires a new frozen run. The engine does not average agent confidence or pretend a quorum proves an investment thesis.

`READY_FOR_HUMAN_REVIEW` is an unapproved research packet. `BLOCKED_FOR_REVIEW` means material exceptions remain. `HUMAN_REVIEW_RECORDED` includes the actual approve/reject decision and digest. `DEMO_COMPLETE_NOT_APPROVED` and `SOURCE_STUDY_COMPLETE_NOT_APPROVED` cannot be promoted to research approval.

## Source-informed versus current-data operation
Source-study mode explains the curriculum without presenting it as current market evidence. Research mode requires a host with permitted current inputs and relevant review. A live source update should be logged as a separate source, with the changed interpretation explained. Neither mode claims full reconstruction of all textbook content or any source-brand endorsement.
