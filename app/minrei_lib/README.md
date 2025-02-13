To implement a factor model, I will need:
- trader positions over time
- FULL price history of all the instruments the trader has EVER traded
- ? FULL price history of all instruments in the trading universe

To implement Pnl / return calculation for our trader, I will need:

To calculate STATIC historical beta, I will need:
- Need: Individual beta, VaR, marginal, R-squared
- To calculate OVERALL beta of the trader's portfolio to an index
    - calculate trader returns (requires trader positions and their associated prices over time)
- To calculate INDIVIDUAL beta of the individual instruments in the trader's potfolio
- Note: Beta_(position vs index) = covariance / variance(index)