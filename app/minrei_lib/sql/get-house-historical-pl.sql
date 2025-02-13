declare @start_valuation_date varchar(20) = '{start_valuation_date}';
with latest_date as (
    select top 1 valuation_date from historical_pl where portfolio = 'hetcoport' and var_level in {var_levels} order by valuation_date desc
)
select valuation_date, var_level, level_name, price_date, pl, sc.supercommodity
from historical_pl hpl
left join supercommodity sc
    on hpl.level_name = sc.commoditygroup
where portfolio = 'hetcoport'
    and (
        (@start_valuation_date = '-1' and valuation_date = (select valuation_date from latest_date))
        or 
        valuation_date >= try_cast(@start_valuation_date as date)
    )
    and var_level in {var_levels}
order by valuation_date