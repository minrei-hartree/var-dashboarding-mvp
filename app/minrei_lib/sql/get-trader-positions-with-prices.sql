select rt.valuation_date, rt.px_location, rt.deltaposition, p.price, rt.forwardmo as forward_month, rt.contract_month,
	rt.gammaposition, rt.thetaposition, rt.vegaposition, -- options
	pd.currency, fx.rate, price_basis,
	pfc.exp_code, rt.uom, cb.contract_size, rt.producttype, tm.weight
from report_table rt
inner join price p
	on rt.valuation_date = p.px_date and rt.px_location = p.px_location and rt.forwardmo = p.forward_month
left join proxy_forward_curve pfc
	on rt.px_location = pfc.px_location
inner join tradermap tm
	on rt.strategynumber = tm.strategynumber and rt.portfolio = tm.portfolio
inner join price_desc pd
	on p.px_location = pd.px_location
left join contract_basis cb
	on rt.px_location = cb.px_location
left join fx_rate_hist fx
	on rt.valuation_date = fx.rate_date and pd.currency = fx.currency2 and fx.currency1 = 'USD' and pd.currency != 'USD' -- Only join FX rates for non-USD
where rt.portfolio = 'hetcoport'
	and tm.trader = '{trader_name}'
	and not rt.producttype like '%0%'
	and rt.deltaposition is not NULL        -- Excludes NULL
	and rt.deltaposition != 0               -- Excludes 0s
	and rt.deltaposition = rt.deltaposition -- Trick to exclude NaN
	and (rt.gammaposition != 0
		or rt.thetaposition != 0
		or rt.vegaposition != 0
		or abs(rt.deltaposition) >= 0.0001
	)                                       -- Excludes tiny positions
order by rt.valuation_date