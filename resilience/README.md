# Climate Resilience Investment Intelligence — original extension

**Prepared 18 November 2026. Research-only; no live security prices, climate hazard feed or trade execution.**

## What is new
A versioned **seven-category** adaptation taxonomy, three distinct economic roles (**solution supplier**, **resilience operator**, **insurer**), cash-flow sensitivity calculations, funding/issuer/market-price evidence gates, explicit prevention of cross-channel risk double counting, three investable-theme *research questions*, and a frozen El Niño observation register.

The user-provided Morgan Stanley report, *The Case for Climate Resilience in a Multipolar World* (13 November 2026), motivated the research questions. This original repository extension **does not reproduce its proprietary 222-stock universe, ratings, charts or PDF**. The category labels are thematic, not investment recommendations.

Independent public context: [McKinsey Global Institute](https://www.mckinsey.com/mgi/our-research/advancing-adaptation-breaking-barriers-to-a-trillion-dollar-opportunity), 3 Nov 2026. Estimated adaptation **needs** are NOT forecast supplier sales; bankability, financing and ability to act limit conversion. [NOAA CPC](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso_advisory/ensodisc.shtml), 12 Nov 2026: ENSO strength probability is NOT a local precipitation or company-earnings probability.

## Run
From the repository root, Python 3.10+ standard library:

```bash
python -m resilience.engine --input resilience/benchmarks.v1.json
python -m unittest discover -s tests -p 'test_resilience.py' -v
```

Every example reports `NEEDS_DATA` and `NOT_SECURITY_VALUATION`. Outputs are in millions of their specified currency, with no terminal value. The supplier model computes realized incremental revenue, contribution EBITDA, tax proxy, recurring capex and working capital; operator avoids expected annual losses based on analyst-supplied **event frequency**; insurer computes a basic underwriting cash-flow proxy including a capital charge. None is an audited DCF or full insurance solvency model.

The following are deliberately NOT implemented: issuer earnings estimates, independent geocoded physical-risk data, hazard probability calibration, real-time quotes, authorized project funding, source entailment, automated trading, and alpha backtests.

See [three original casebooks](CASEBOOK.md), [seven-theme taxonomy](taxonomy.v1.json), and [frozen 2026–27 El Niño hypotheses](enso-freeze-2026-11-18.json). The project economics should be connected to the existing evidence and human approval engine only after primary issuer facts and valuation expectations are supplied.
