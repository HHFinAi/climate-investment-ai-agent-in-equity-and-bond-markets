# Worked example — fictional industrial issuer and corporate bond

**SYNTHETIC DEMONSTRATION ONLY.** No real company, market price, climate forecast or legal carbon-price regime is represented. All amounts below are USD millions except carbon price per tonne, equity per-share values, and bond prices per 100 face value. Inputs are in `synthetic-financials.json`; reproducible outputs are in `expected-calculations.json`.

## Climate-to-cash-flow bridge
The illustrative business has 1,000,000 tonnes of covered emissions and 200,000 assumed free allowances. At an assumed USD75/tonne, gross cost is USD60 million. At 60% assumed pass-through, USD36 million is recovered in sales and USD24 million remains. With zero carbon cost embedded in the baseline, the incremental EBITDA effect is **-USD24 million**. Neither legal coverage nor the carbon price is inferred from the source textbook.

Baseline simplified FCF: `240 EBITDA - 35 cash taxes - 60 capex - 5 working-capital increase = 140`.

Illustrative year-one EBITDA: `240 - 24 carbon - 8 physical-cost sensitivity + 10 solutions margin = 218`. Scenario FCF: `218 - 33 cash taxes - 75 capex - 6 working-capital increase = 104`. The taxes, investment costs and following years' cash flows are independently supplied synthetic assumptions, not mechanically forecast from the carbon calculation.

## Equity branch
Five explicit year-end cash flows, a 9% discount rate, and 2% terminal growth. Cash 100, debt 400 and 50 million diluted shares. Discount rates are held constant because the same climate effects already enter cash flow. These are demonstration assumptions, not recommended model inputs.

| Scenario | Enterprise value | Equity value | Per share |
|---|---:|---:|---:|
| baseline | 2,320.34 | 2,020.34 | 40.41 |
| managed transition | 1,744.75 | 1,444.75 | 28.89 |
| delayed transition | 1,508.24 | 1,208.24 | 24.16 |
| physical stress | 1,790.14 | 1,490.14 | 29.80 |

No scenario probabilities are assigned. No current market price is provided, so no upside or trade recommendation is calculated. The scenario set is not an exhaustive distribution.

## Corporate bond branch
Supplied annual coupons are 5 per 100 face and the fifth-year payment is 105. Flat risk-free rate 3%, spread 1.5%. The helper uses a simplified annual discount rate, not an OAS/curve/callable model.

| Sensitivity | PV per 100 |
|---|---:|
| Baseline | 102.194988 |
| Risk-free rate +100bp only | 97.864858 |
| Spread +75bp only | 98.925070 |
| Combined shock | 94.770163 |

Combined percentage price change: **-7.2654%**. Rate/spread interaction is reported rather than assuming linear additivity. The separate example `100 exposure * 3% PD * 50% LGD = 1.5` is an undiscounted single-horizon expected-loss illustration and is **not** subtracted again from the spread-discounted bond price.

## Portfolio metric example
A separate corporate sleeve holds 60% of an issuer with intensity 500 and 40% of an issuer with intensity 200, producing **WACI = 380 tCO2e/USD million revenue**. With the second issuer's emissions missing, full WACI is null, coverage is 60%, known weighted contribution is 300, and covered-only WACI is separately labelled 500. No sovereign emissions are inserted into that corporate metric.

## Method and software boundary
The source underpins financial transmission, FCF/DCF and WACI (source-map anchors CFA-04-TRANSMISSION, CFA-05-CARBON, CFA-07-VALUATION and CFA-07-FLOW). Contractual bond-PV conventions, ECL illustration, missing-data handling and all numerical fixtures are original implementation choices. Read `references/calculation-conventions.md` for limitations. An actual credit analysis additionally requires legal obligor/guarantee, capital structure, refinancing and evidence; these arithmetic examples do not supply that diligence.
