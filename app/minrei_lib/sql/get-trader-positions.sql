select rt.valuation_date, rt.px_location, rt.deltaposition, rt.forwardmo as forward_month, rt.contract_month,
	rt.gammaposition, rt.thetaposition, rt.vegaposition, -- options
	pd.currency, case when fx.rate is not null then fx.rate else 1 end as rate, price_basis,
	rt.uom, cb.contract_size, 
	pfc.exp_code, rt.producttype, cg.commoditygroup, sc.supercommodity, rt.strategynumber,
	tm.trader, tm.weight
from report_table rt with (nolock)
left join proxy_forward_curve pfc
	on rt.px_location = pfc.px_location
left join price_desc pd
	on rt.px_location = pd.px_location
left join contract_basis cb
	on rt.px_location = cb.px_location
left join fx_rate_hist fx
	on rt.valuation_date = fx.rate_date and pd.currency = fx.currency2 and fx.currency1 = 'USD' and pd.currency != 'USD' -- Only join FX rates for non-USD
left join commoditygroup cg
	on cg.px_location = rt.px_location
left join supercommodity sc
	on cg.commoditygroup = sc.commoditygroup
inner join tradermap tm
	on rt.strategynumber = tm.strategynumber and rt.portfolio = tm.portfolio and tm.traderorgroup = 'trader'
where rt.valuation_date = '{valuation_date}'
	and rt.portfolio = 'hetcoport'
	and tm.trader = '{trader_name}'
	and rt.producttype not like '%0%'
	and rt.deltaposition is not NULL        -- Excludes NULL
	and rt.deltaposition != 0               -- Excludes 0s
	and rt.deltaposition = rt.deltaposition -- Trick to exclude NaN
	and (rt.gammaposition != 0
		or rt.thetaposition != 0
		or rt.vegaposition != 0
		or abs(rt.deltaposition) >= 0.0001
	)                                       -- Excludes tiny positions 
order by rt.valuation_date, rt.px_location, rt.forwardmo, rt.contract_month, rt.deltaposition