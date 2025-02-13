with latest_date as (
    select top 1 valuation_date from report_table where portfolio = 'hetcoport' and producttype like '0Trader' order by valuation_date desc
)
select trader from report_table where valuation_date = (select valuation_date from latest_date) and portfolio = 'hetcoport' and producttype like '0Trader' and trader is not null order by trader