declare @lookback int = {lookback_days};
declare @start varchar(20) = '{start_date}';
with latest_date as (
	select top 1 px_date from price where px_location in {px_locations} order by px_date desc
)
select
	p.px_date, p.px_location, p.price, p.forward_month, p.contract_month,
	cb.price_basis, pd.currency, case when fx.rate is not null then fx.rate else 1 end as rate,
	cg.commoditygroup
	-- pfc.exp_code,
	-- case when et.mtmquote is not null then 1 else 0 end as is_futures_expiring
from price p
left join commoditygroup cg
	on cg.px_location = p.px_location
-- left join proxy_forward_curve pfc
-- 	on pfc.px_location = p.px_location
-- left join expirationtable et
-- 	on et.basefuturecon = pfc.exp_code and et.futureexp = p.px_date and et.period = p.contract_month
left join contract_basis cb
	on cb.px_location = p.px_location
left join price_desc pd
	on p.px_location = pd.px_location
left join fx_rate_hist fx
	on p.px_date = fx.rate_date and pd.currency = fx.currency2 and fx.currency1 = 'USD' and pd.currency != 'USD' -- Only join FX rates for non-USD
where p.px_location in {px_locations}
	and p.px_date >= dateadd(day, -@lookback, (select px_date from latest_date))
order by p.px_date, p.forward_month

