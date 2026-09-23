"""Small, explicit calculations; see references/calculation-conventions.md.

No helper estimates climate pathways, causal coefficients, PDs or market prices.
Source-inspired formulas and implementation extensions are distinguished there.
All rate inputs are decimals, all basis point inputs explicitly use *_bps.
"""
from __future__ import annotations
import math
from typing import Any, Sequence

class DataError(ValueError):
    """A missing, inconsistent or unsupported analytical input."""

def number(value: Any, name: str, *, minimum: float | None = None,
           maximum: float | None = None, positive: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise DataError(f'{name} must be a finite number, not missing, boolean or text')
    result = float(value)
    if positive and result <= 0:
        raise DataError(f'{name} must be positive')
    if minimum is not None and result < minimum:
        raise DataError(f'{name} must be >= {minimum}')
    if maximum is not None and result > maximum:
        raise DataError(f'{name} must be <= {maximum}')
    return result

def total_emissions(scope1: float, scope2: float, *, scope3: float | None = None,
                    include_scope3: bool = False) -> dict[str, Any]:
    if not isinstance(include_scope3, bool):
        raise DataError('include_scope3 must be boolean')
    a, b = number(scope1, 'scope1', minimum=0), number(scope2, 'scope2', minimum=0)
    c = number(scope3, 'scope3', minimum=0) if include_scope3 else 0.0
    return {'tco2e': a + b + c, 'scope_basis': '1+2+3' if include_scope3 else '1+2',
            'scope3_included': include_scope3, 'offsets_or_avoided_emissions_netted': False}

def carbon_intensity(emissions_tco2e: float, revenue_million: float) -> float:
    return number(emissions_tco2e, 'emissions_tco2e', minimum=0) / number(revenue_million, 'revenue_million', positive=True)

def waci(holdings: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Corporate long-only sleeve WACI. Input weights must sum to one.

    Missing observations retain their weight. Full WACI is null, not zero-filled.
    The covered-only normalisation is a separately labelled output.
    """
    if not holdings:
        raise DataError('holdings cannot be empty')
    seen: set[str] = set()
    total_weight = 0.0
    coverage = 0.0
    contribution = 0.0
    missing: list[str] = []
    basis: set[tuple[Any, ...]] = set()
    for h in holdings:
        hid = h.get('instrument_id')
        if not isinstance(hid, str) or not hid or hid in seen:
            raise DataError('unique instrument_id required')
        seen.add(hid)
        if h.get('asset_class') not in ('equity', 'corporate_bond'):
            raise DataError('corporate WACI does not accept sovereign, municipal or structured credit')
        w = number(h.get('weight'), 'weight', minimum=0, maximum=1)
        total_weight += w
        for key in ('scope_basis','revenue_currency','reporting_year'):
            if not isinstance(h.get(key), str) or not h[key].strip():
                raise DataError(f'{key} must be explicitly stated')
        basis.add((h['scope_basis'], h['revenue_currency'], h['reporting_year']))
        e, r = h.get('emissions_tco2e'), h.get('revenue_million')
        # Validate the known half of a partially missing observation as well.
        if e is not None: number(e, 'emissions_tco2e', minimum=0)
        if r is not None: number(r, 'revenue_million', positive=True)
        if e is None or r is None:
            if w > 0: missing.append(hid)
            continue
        contribution += w * carbon_intensity(e, r)
        coverage += w
    if not math.isclose(total_weight, 1.0, rel_tol=0, abs_tol=1e-9):
        raise DataError('weights must sum to 1; define the sleeve explicitly, do not silently rescale')
    if len(basis) != 1:
        raise DataError('align scope, currency and reporting year before aggregation')
    scope, currency, year = next(iter(basis))
    return {'full_waci': contribution if not missing else None,
            'known_weighted_contribution': contribution,
            'covered_only_waci': contribution / coverage if coverage > 0 else None,
            'coverage_weight': coverage, 'missing_instruments': missing,
            'scope_basis': scope, 'reporting_year': year,
            'units': f'tCO2e/{currency} million revenue',
            'interpretation': 'Exposure metric, not financial loss or proof of real-world impact.'}

def attributed_emissions(investment_value: float, denominator_value: float,
                         emissions_tco2e: float, *, denominator_basis: str) -> float:
    """Illustrate the source's ownership attribution choices; NOT PCAF certification."""
    if denominator_basis not in ('equity_market_cap', 'corporate_enterprise_value', 'corporate_total_debt'):
        raise DataError('explicit source-era corporate/equity attribution basis required')
    inv = number(investment_value, 'investment_value', minimum=0)
    den = number(denominator_value, 'denominator_value', positive=True)
    if inv > den:
        raise DataError('attribution exceeds selected denominator; reconcile units and capital claim')
    return inv / den * number(emissions_tco2e, 'emissions_tco2e', minimum=0)

def carbon_cost_bridge(covered_emissions_tco2e: float, free_allowances_tco2e: float,
                       carbon_price_per_tonne: float, pass_through: float,
                       *, baseline_net_carbon_cost: float) -> dict[str, float]:
    """Analyst-specified coverage, not an assertion of legal emissions-tax scope."""
    e = number(covered_emissions_tco2e, 'covered_emissions', minimum=0)
    a = number(free_allowances_tco2e, 'free_allowances', minimum=0)
    price = number(carbon_price_per_tonne, 'carbon_price', minimum=0)
    pt = number(pass_through, 'pass_through', minimum=0, maximum=1)
    baseline = number(baseline_net_carbon_cost, 'baseline_net_carbon_cost', minimum=0)
    charged = max(0.0, e-a)
    gross = charged * price
    passed = gross * pt
    net = gross - passed
    return {'chargeable_tco2e': charged, 'gross_carbon_cost': gross,
            'revenue_pass_through': passed, 'net_carbon_cost': net,
            'incremental_ebitda_impact': -(net-baseline)}

def simplified_fcf(ebitda: float, cash_taxes: float, capex: float,
                   increase_working_capital: float) -> float:
    """Source p545 bridge; cash taxes are supplied, not inferred from EBITDA."""
    return (number(ebitda, 'ebitda') - number(cash_taxes, 'cash_taxes')
            - number(capex, 'capex', minimum=0) - number(increase_working_capital, 'increase_working_capital'))

def validate_treatments(records: Sequence[dict[str, Any]]) -> None:
    treatments: dict[str, set[str]] = {}
    allowed = {'cash_flow', 'discount_rate', 'terminal', 'collateral', 'disclosure_only'}
    for rec in records:
        rid = rec.get('risk_id')
        where = rec.get('treatment')
        if not isinstance(rid, str) or not rid.strip() or where not in allowed:
            raise DataError('each risk requires an ID and explicit supported treatment')
        if where in treatments.setdefault(rid, set()):
            raise DataError(f'duplicate treatment for {rid}; reconcile the underlying economic effect')
        treatments[rid].add(where)
    for rid, choices in treatments.items():
        if {'cash_flow', 'discount_rate'} <= choices:
            raise DataError(f'{rid}: same economic effect charged in cash flow and discount rate')

def dcf(cash_flows: Sequence[float], discount_rate: float,
        *, terminal_growth: float | None = None) -> dict[str, float | None]:
    if not cash_flows:
        raise DataError('cash flows required')
    r = number(discount_rate, 'discount_rate')
    if r <= -1: raise DataError('discount_rate must exceed -1')
    cfs = [number(x, 'cash_flow') for x in cash_flows]
    pv = sum(cf / (1+r)**t for t, cf in enumerate(cfs, 1))
    terminal_pv = None
    if terminal_growth is not None:
        g = number(terminal_growth, 'terminal_growth')
        if g <= -1 or r <= g:
            raise DataError('terminal growth must exceed -1 and be below the discount rate')
        if cfs[-1] <= 0:
            raise DataError('positive sustainable terminal cash flow required; otherwise provide an explicit wind-down')
        terminal_pv = cfs[-1] * (1+g) / (r-g) / (1+r)**len(cfs)
    result = {'explicit_pv': pv, 'terminal_pv': terminal_pv, 'enterprise_value': pv+(terminal_pv or 0)}
    for key, value in result.items():
        if value is not None: number(value, key)
    return result

def equity_bridge(enterprise_value: float, cash: float, debt: float,
                  diluted_shares: float, *, other_claims: float = 0) -> dict[str, float]:
    ev = number(enterprise_value, 'enterprise_value')
    equity = ev + number(cash, 'cash', minimum=0) - number(debt, 'debt', minimum=0) - number(other_claims, 'other_claims', minimum=0)
    if equity < 0: raise DataError('claims exceed modelled value; use a distress/recovery model, not a negative share price')
    shares = number(diluted_shares, 'diluted_shares', positive=True)
    return {'equity_value': equity, 'value_per_share': equity/shares}

def scenario_weighted_value(values: Sequence[float], probabilities: Sequence[float] | None = None) -> dict[str, Any]:
    vals = [number(x, 'scenario_value') for x in values]
    if not vals: raise DataError('scenario values required')
    if probabilities is None:
        return {'weighted_value': None, 'minimum': min(vals), 'maximum': max(vals), 'basis': 'Unweighted what-if scenarios; no probabilities inferred.'}
    if len(vals) != len(probabilities): raise DataError('one probability per scenario required')
    ps = [number(x, 'probability', minimum=0, maximum=1) for x in probabilities]
    if not math.isclose(sum(ps), 1, rel_tol=0, abs_tol=1e-9): raise DataError('probabilities must sum to 1; no automatic normalisation')
    return {'weighted_value': sum(v*p for v,p in zip(vals,ps)), 'minimum': min(vals), 'maximum': max(vals),
            'basis': 'Explicit analyst-supplied scenario weights; not model-calibrated probabilities.'}

def bond_present_value(cash_flows: Sequence[dict[str, float]], risk_free_rate: float,
                       credit_spread: float, *, instrument_type: str = 'plain_vanilla') -> float:
    """IMPLEMENTATION_EXTENSION: flat annual rate, supplied times, no accrued interest.

    Not a yield-curve/OAS, default-transition, callable or securitisation model.
    """
    if instrument_type != 'plain_vanilla': raise DataError('specialist model required for this instrument type')
    if not cash_flows: raise DataError('contractual cash flows required')
    r = number(risk_free_rate, 'risk_free_rate') + number(credit_spread, 'credit_spread')
    if r <= -1: raise DataError('combined annual rate must exceed -1')
    times, pv = [], 0.0
    for row in cash_flows:
        t = number(row.get('time_years'), 'time_years', positive=True)
        cf = number(row.get('amount'), 'amount', minimum=0)
        times.append(t)
        pv += cf / (1+r)**t
    if times != sorted(times) or len(set(times)) != len(times):
        raise DataError('cash-flow times must be unique and strictly increasing')
    return number(pv, 'bond_present_value')

def bond_stress(cash_flows: Sequence[dict[str, float]], risk_free_rate: float,
                credit_spread: float, *, rate_shock_bps: float, spread_shock_bps: float) -> dict[str, float]:
    rate = number(rate_shock_bps, 'rate_shock_bps')/10000
    spread = number(spread_shock_bps, 'spread_shock_bps')/10000
    base = bond_present_value(cash_flows, risk_free_rate, credit_spread)
    if base <= 0: raise DataError('positive base bond value required')
    rate_only = bond_present_value(cash_flows, risk_free_rate+rate, credit_spread)
    spread_only = bond_present_value(cash_flows, risk_free_rate, credit_spread+spread)
    combined = bond_present_value(cash_flows, risk_free_rate+rate, credit_spread+spread)
    return {'base_value': base, 'rate_only_value': rate_only, 'spread_only_value': spread_only,
            'combined_value': combined, 'combined_change_pct': 100*(combined/base-1),
            'interaction': combined-base-(rate_only-base)-(spread_only-base)}

def expected_credit_loss(exposure: float, probability_default: float, loss_given_default: float) -> float:
    """IMPLEMENTATION_EXTENSION: undiscounted single-horizon illustration only."""
    return (number(exposure, 'exposure', minimum=0)
            * number(probability_default, 'probability_default', minimum=0, maximum=1)
            * number(loss_given_default, 'loss_given_default', minimum=0, maximum=1))
