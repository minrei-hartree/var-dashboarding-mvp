from typing import Union
import numpy as np
import pandas as pd

from .portfolio_analysis import CUSTOM_SEPARATOR, PortfolioAnalysis
from .database import Database
from .plot import Plot


class Core:

    @staticmethod
    def generate_pnl_vectors(trader: str, lookback_days: int = 400):
        db = Database()
        positions = db.traders.get_positions_latest(trader)
        prices = db.prices.get_historical(positions['px_location'].unique(), lookback_days)
        prices = PortfolioAnalysis.calculate_returns(prices)
        pnl_vectors = PortfolioAnalysis.ex_ante_portfolio_positions(positions, prices, db.commodities.get_seasonal_index(), use_prices=False)

        # unparse
        pnl_vectors.index = pnl_vectors.index.str.rsplit(CUSTOM_SEPARATOR, n=1, expand=True)
        pnl_vectors.index.names = ['px_location', 'contract_month']
        pnl_vectors.index = pnl_vectors.index.set_levels([
            pnl_vectors.index.levels[0],
            pd.to_datetime(pnl_vectors.index.levels[1])
        ])
        pnl_vectors = pnl_vectors.apply(list, axis=1).rename('pnl_vector')

        df = pd.merge(positions.set_index(['px_location', 'contract_month']), pnl_vectors, left_index=True, right_index=True)
        df = df.reset_index()
        df['idx'] = df['px_location'] + CUSTOM_SEPARATOR + df['contract_month'].astype(str)
        return df

    @staticmethod
    def backtest_portfolio_gmv(trader: Union[str, pd.DataFrame], index: str = 'SPY500-N', lookback_days: int = 400):
        db = Database()
        index_log_returns = PortfolioAnalysis.calculate_returns(db.prices.get_historical(index, lookback_days))
        index_log_returns = index_log_returns.set_index('px_date')['log_return']

        trader_positions = db.traders.get_positions_latest(trader) if isinstance(trader, str) else trader
        trader_prices = PortfolioAnalysis.calculate_returns(db.prices.get_historical(trader_positions['px_location'].unique(), lookback_days=400))
        exante_portfolio = PortfolioAnalysis.ex_ante_portfolio_positions(trader_positions, trader_prices, db.commodities.get_seasonal_index(), use_prices=True)


        var_1y = PortfolioAnalysis.var(exante_portfolio.sum(axis=0).diff().dropna())
        var_3m = PortfolioAnalysis.var(exante_portfolio.sum(axis=0).diff().dropna(), 60)
        starting_gmv = exante_portfolio.iloc[:, 0].abs().sum()
        ending_gmv = exante_portfolio.iloc[:, -1].abs().sum()
        ending_nmv = exante_portfolio.iloc[:, -1].sum()
        print("1y VaR", var_1y)
        print("3m VaR", var_3m)
        print("ending GMV", ending_gmv)
        print("ending NMV", ending_nmv)
        leverage_ratio = abs(ending_gmv / ending_nmv)
        print("ratio", leverage_ratio)
        print("starting GMV", starting_gmv)
        beta, r2, p_value = PortfolioAnalysis.calculate_beta(
            index_log_returns,
            PortfolioAnalysis._calculate_portfolio_log_returns(exante_portfolio.sum(axis=0) + starting_gmv)
        )

        print('(beta, r2, p_value)', beta, r2, p_value)
        print('leverage-adjusted beta', beta * leverage_ratio)

        reconstructed_returns = np.exp(
                                    PortfolioAnalysis._calculate_portfolio_log_returns(exante_portfolio.sum(axis=0) + starting_gmv)
                                ).cumprod()
        
        print('1y returns (GMV)', reconstructed_returns[-1])
        print('1y returns (levered; "true")', 1 + (reconstructed_returns[-1] - 1) * leverage_ratio)
        

        return Plot.plot_timeseries(reconstructed_returns, title=f'{trader if isinstance(trader, str) else "House"} 1y backtest (GMV)')