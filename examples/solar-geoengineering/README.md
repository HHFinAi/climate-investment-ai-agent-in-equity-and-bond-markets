# Solar geoengineering: SAI / MCB cost sensitivity, not a climate forecast

**21 November 2026 | Original HHFinAi numerical implementation | Illustrative only | NEEDS_DATA**

This compact methodology case analyses the arithmetic of **stratospheric
aerosol injection (SAI)** and **marine cloud brightening (MCB)** without
claiming that either technology has demonstrated predictable large-scale
temperature control, environmental safety, international authorization or a
commercial market.

## Calculations and units

- **SAI:** target degrees × assumed radiative forcing magnitude per degree
  gives W/m²; divide by assumed forcing efficiency in W/m² per Tg sulfur per
  year to obtain Tg sulfur/year; convert Tg sulfur to Tg SO₂; multiply by
  a hypothetical all-in USD/tonne delivery cost. A teragram is one million
  metric tonnes.
- **MCB:** target degrees × assumed dry-salt Tg/year per degree; multiply
  by GWh per Tg to obtain annual electricity; convert GWh to MWh; multiply
  by an all-in marine generation USD/MWh LCOE; add only separately modelled
  **non-energy** direct annual costs.
- The marine LCOE already includes power-plant capital and operating expenses.
  Adding the power-generation equipment capital a second time would
  **double-count it**. Governance, R&D, long-run ecological effects, liability,
  and monitored weather impacts are not included in either cost number.

**All numeric coefficients in [inputs.json](inputs.json) are independently
selected hypothetical sensitivity inputs**, NOT proprietary Goldman Sachs
model values or validated scientific response functions. One-degree-unit
mass/cost calculations are not evidence that the outcome will occur.

## Run

~~~bash
python examples/solar-geoengineering/model.py --check
python examples/solar-geoengineering/model.py
python examples/solar-geoengineering/model.py --write
python -m unittest discover -s tests -p 'test_solar_geoengineering.py' -v
~~~

The output includes two 3×3 sensitivity matrices, cost component bridges
and explicit suppression of security-level revenue and carbon-removal pricing.
The optional results.json is generated locally only on \`--write\`.
There is no autonomous climate simulation or field-deployment mechanism.

## What this is NOT

- **Not decarbonization or carbon dioxide removal.** SAI/MCB may change
  radiative forcing, but the model explicitly reports zero atmospheric
  CO₂ physically removed and does not create an artificial USD/tCO₂
  removal-price benchmark. Operational emissions remain **unknown**, not zero.
- **Not a deployment or governance recommendation.** No authority to spray
  aerosols, verified global-scale feasibility, calibrated location-specific
  climate impacts or market opportunity is established.
- **Not an equity TAM or additive supplier revenue pool.** Aircraft,
  power equipment, vessels, chemicals and services can overlap in modelled
  spending. No issuer sales, adoption probability or equity value is forecast.

## Research source and verification

The 18 November 2026 Goldman Sachs *Carbonomics — Geo-engineering:
Thinking the unthinkable* report prompted this study. Its analyses of sulfur
efficacy, delivery constraints, marine aerosol uncertainty, governance and
termination risks identify helpful diligence questions. **The proprietary
report, its proprietary charts/tables and its estimates have not been
reproduced in this repository.** The source remains external, with all
specific inputs here clearly fictional; cite public original scientific
literature directly in any later substantive research release.

Next verification gates: peer-reviewed forcing/dose relationships and
uncertainty envelopes; engineering costs and replacement; multi-region
precipitation, ozone, ocean and termination impacts; applicable national
and international law; liability and funding; independent human assessment.
Pending these gates, the investment status is **NEEDS_DATA**. A low
engineering-cost estimate is neither an aggregate social cost nor evidence
that SRM should replace emissions reductions.
