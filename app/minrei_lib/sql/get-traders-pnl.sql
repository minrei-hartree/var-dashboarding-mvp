select
    portfoliodate, tradername, dtd_pl, mtd_pl, ytd_pl, updatedate
from Trader_PL_SystemGenerate
where portfolio = 'hetcoport'
    and overnightoractual = '{overnight_or_actual}'
    and tradername in {trader_names}
order by portfoliodate, tradername