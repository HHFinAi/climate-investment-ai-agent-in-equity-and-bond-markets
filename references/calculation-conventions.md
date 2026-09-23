# Calculation conventions and source boundaries

## Source-inspired implementations
**Emissions:** source chapter 5.1, PDF 329. Add gross Scope 1 and one explicitly selected Scope 2 basis; include Scope 3 only when requested and available. The helper never nets avoided emissions or offsets. The caller must ensure gases, units, boundaries and periods are comparable.

**Intensity and WACI:** chapter 5.1.4, PDF 329–330, equation visually verified. Revenue intensity is `tCO2e / revenue_million`. WACI is `sum(weight * issuer_intensity)`. The helper uses an explicitly defined long-only corporate sleeve with weights summing to one, consistent reporting year, currency and scope. Missing coverage returns `full_waci = null`; the known weighted contribution and the separately normalised covered-only WACI remain available. Strict homogeneous-period and missing-data handling are engineering safeguards, not claims that the source prescribes this exact implementation.

**Attribution:** PDF 329 and chapter 7.2.4, PDF 584. The helper illustrates `investment_value / selected_denominator * emissions`. The denominator must be named explicitly (equity market capitalisation, corporate enterprise value, or corporate total debt); these are source-era choices, not a claim of current PCAF conformity. Corporate and sovereign attribution are not interchangeable. Currency/date/capital-claim consistency remains the analyst's responsibility.

**Carbon cost:** chapter 7.1.5, PDF 547–550. `max(covered_emissions - free_allowances, 0) * carbon_price`, less the explicit cost passed to customers, produces a net cost. Subtract the net carbon cost already embedded in the baseline to obtain the incremental EBITDA effect. Coverage and free allowances are supplied assumptions or sourced legal facts—not inferred from scope labels. Prices, costs and revenue must be in the same currency. The example's carbon bridge is in USD; it is divided by one million before comparison with financial statements in USD millions.

**Simplified FCF:** source PDF 545: `EBITDA - cash_taxes - capex - increase_in_working_capital`. Cash taxes are provided, not inferred from EBITDA. A negative working-capital increase is a release. More elaborate tax/lease/SBC/debt treatment requires an explicitly identified additional model.

**DCF:** chapter 7.1.5, PDF 545. End-of-year supplied cash flows discounted at a supplied rate; optional Gordon-growth terminal value. Terminal growth must be below the discount rate and terminal sustainable cash flow positive. No market/industry default discount rate is embedded. The same risk ID cannot enter both cash flow and a discount-rate adjustment. An enterprise-to-equity bridge uses explicit cash, debt, other claims and diluted shares; this simple bridge is not a forecast financing model. A negative residual raises a distress-model requirement rather than publishing a negative share-price target.

## Explicit implementation extensions
The following numerical conventions are new implementation choices. The source supports the analytical questions but does not supply these software routines.

**Plain-vanilla bond PV:** supplied contractual amounts at explicit year fractions, discounted at a flat annually compounded risk-free rate plus credit spread. Cash-flow times are strictly increasing. No accrued interest, coupon calendar, day-count conversion, default cash-flow transition, OAS, optionality, amortisation or securitisation waterfall is implemented. The output is a simplified present value, not a verified clean bond quote. Use a specialist model for complex instruments.

**Bond stress:** independently reprice rate-only, spread-only and combined basis-point shocks. Shocks divide by 10,000. The nonlinear interaction is reported so the two single-axis price changes are not assumed additive. No attribution of the shock magnitude to climate is made without an external model or explicit analyst assumption.

**Expected credit loss:** the single-horizon, undiscounted illustration is `EAD * PD * LGD`, with both probabilities bounded to [0,1]. Horizon, PD calibration and recovery assumptions must be supplied. It is not IFRS 9 expected loss or a complete valuation. Do not subtract this illustration again from a bond price already discounted for credit risk.

**Scenario weights:** unweighted scenarios are the default and yield a range, not an expected value. Explicit weights must be complete and sum to one. They are identified as analyst-supplied, not probabilities produced by climate models or confidence scores.

## Not implemented
No climate-loss functions, downscaling, hazard-frequency calibration, IAM simulations, temperature-alignment engine, regulatory taxonomy classifier, credit rating model, risk optimizer or automated position sizing are embedded. Narrative agent roles require the appropriate inputs and tools, or must state the limitation.
