select valuation_date, level_name, price_date, pl
from historical_pl where level_name in {level_names} and portfolio = 'hetcoport'
order by valuation_date