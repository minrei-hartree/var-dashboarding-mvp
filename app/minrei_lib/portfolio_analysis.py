import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import linregress
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .database import Database
from .plot import Plot

CUSTOM_SEPARATOR = '._.'

class PortfolioAnalysis:
    def __init__(self):
        pass

    @staticmethod
    def _calculate_portfolio_log_returns(portfolio_v : pd.Series) -> pd.Series:
        """Calculates log returns off portfolio notionals.

        Args:
            portfolio_v (pd.Series): portfolio notionals over time (t x 1)

        Returns:
            _type_: log returns (t-1 x 1)
        """
        # determine if long, short, or both
        if min(portfolio_v) > 0: # long
            return np.log(1 + portfolio_v.pct_change()).dropna()

        if max(portfolio_v) < 0: # short
            return np.log(1 - np.abs(portfolio_v).pct_change()).dropna()
        
        # long/short, delta-neutral? rare but possible edge case
        return np.log(1 + (-2 * min(portfolio_v) + portfolio_v).pct_change()).dropna()

    @staticmethod
    def calculate_beta(returns_x: pd.Series, returns_y: pd.Series, lookback_days: int = 0):
        aligned_returns = pd.concat([returns_x, returns_y], axis=1).dropna()[-lookback_days:]
        covariance = aligned_returns.iloc[:, 0].cov(aligned_returns.iloc[:, 1])
        variance = aligned_returns.iloc[:, 0].var()
        beta = covariance / variance

        correlation = aligned_returns.iloc[:, 0].corr(aligned_returns.iloc[:, 1])
        r_squared = correlation ** 2
        _, _, _, p_value, _ = linregress(aligned_returns.iloc[:, 0], aligned_returns.iloc[:, 1])

        return beta, r_squared, p_value

    @staticmethod
    def simulate_ex_ante_portfolio_notionals(trader_name: str, valuation_date: str = "-1", lookback_days: int = 400) -> pd.Series:
        """Simulates an ex-ante portfolio's notionals based on historical data (default lookback of a year).
        NOTE: Does not take contract rolls into account. Use `ex_ante_returns` instead.

        Args:
            positions (pd.Series): deltaposition indexed by date
            valuation_date (str): start date to look back from. defaults to latest (-1).

        Returns:
            pd.Series: (t, ) of simulated historical portfolio notionals
        """
        db = Database()
        seasonal_indices = db.commodities.get_seasonal_index()
        if valuation_date != '-1':
            positions = db.traders.get_positions(trader_name, valuation_date)
        else:
            positions = db.traders.get_positions_latest(trader_name)
        px_locations = positions['px_location'].unique()
        prices = db.prices.get_historical(px_locations, lookback_days=lookback_days, start_date=valuation_date)

        return PortfolioAnalysis.ex_ante_portfolio_notional(positions, prices, seasonal_indices)
    
    @staticmethod
    def ex_ante_portfolio_notional(positions: pd.DataFrame, prices: pd.DataFrame, seasonal_indices: list[str]) -> pd.Series:
        """Calculates the ex-ante historical notionals given *static positions*, and their historical prices.
        Seasonality is taken into account (seasonal contracts use contract_month, else forward_month).
        NOTE: Does not take contract rolls into account. Use `_ex_ante_pnl` instead.

        Args:
            positions (pd.DataFrame): _description_
            prices (pd.DataFrame): _description_
            seasonal_indices (list[str]): _description_

        Returns:
            pd.Series: (t, ) of simulated historical portfolio notionals
        """
        if (len(positions['valuation_date'].unique()) > 1):
            return ValueError('position df should only have a single valuation_date')

        seasonal_mask = positions['px_location'].isin(seasonal_indices)
        seasonal_portfolio_returns, prices_idx = PortfolioAnalysis._ex_ante_subnotionals(positions, prices, seasonal_mask, True)
        non_seasonal_portfolio_returns, _ = PortfolioAnalysis._ex_ante_subnotionals(positions, prices, ~seasonal_mask, False)
        portfolio_returns = seasonal_portfolio_returns + non_seasonal_portfolio_returns
        return pd.Series(portfolio_returns, index=prices_idx)

    @staticmethod
    def _ex_ante_subnotionals(positions: pd.DataFrame, prices: pd.DataFrame, mask, is_season: bool):
        returns_by = f"{'contract' if is_season else 'forward'}_month"
        sub_positions = positions.loc[mask, :].copy()
        sub_positions['idx'] = sub_positions['px_location'] + CUSTOM_SEPARATOR + sub_positions[returns_by].astype(str)
        sub_positions = sub_positions.set_index('idx')

        prices['idx'] = prices['px_location'] + CUSTOM_SEPARATOR + prices[returns_by].astype(str)
        prices_matrix = prices.pivot(index='px_date', columns='idx', values='price') # t x n
        prices_matrix = prices_matrix.ffill().bfill()

        prices_matrix_np = prices_matrix[sub_positions.index].to_numpy() # t x n
        sub_positions_v_np = sub_positions['deltaposition'].to_numpy() # n x 1
        portfolio_v = prices_matrix_np @ sub_positions_v_np # t x 1
        return portfolio_v, prices_matrix.index
    
    @staticmethod
    def ex_ante_portfolio_positions(positions: pd.DataFrame, prices: pd.DataFrame, seasonal_indices: list[str], use_prices: bool=False) -> pd.Series:
        """Simualtes ex-ante historical pnl by position. Uses either prices or simple returns which takes futures rolls into account.
        NOTE: Assumes weight has already been applied onto positions.

        Returns:
            pd.Series: (n x t-1) pnl returns.
        """
        mask = positions['px_location'].isin(seasonal_indices)

        seasonal_pnl = PortfolioAnalysis._ex_ante_subpnl(positions, prices, mask, True, use_prices)
        nonseasonal_pnl = PortfolioAnalysis._ex_ante_subpnl(positions, prices, ~mask, False, use_prices)
        total_pnl = pd.concat([seasonal_pnl, nonseasonal_pnl], axis=0)
        return total_pnl
    
    @staticmethod
    def _ex_ante_subpnl(positions: pd.DataFrame, prices: pd.DataFrame, mask, is_seasonal: bool, use_prices: bool=False):
        """Simualtes ex-ante historical pnl. Uses either prices or simple returns which takes futures rolls into account.
        NOTE: Assumes weight has already been applied onto positions.

        Returns:
            pd.Series: (n x t-1) pnl returns.
        """
        val = 'price' if use_prices else 'price_delta'
        subpositions = positions.loc[mask, :].copy()
        return_by = 'contract_month' if is_seasonal else 'forward_month'
        dates = prices['px_date'].unique()

        subpositions_index = subpositions['px_location'] + CUSTOM_SEPARATOR + subpositions['contract_month'].astype(str)

        subpositions['idx'] = subpositions['px_location'] + CUSTOM_SEPARATOR + subpositions[return_by].astype(str)
        subpositions = subpositions.set_index('idx')

        prices['idx'] = prices['px_location'] + CUSTOM_SEPARATOR + prices[return_by].astype(str)
        returns_matrix = prices.pivot(index='px_date', columns='idx', values=val) # t-1 x n
        if use_prices:
            returns_matrix = returns_matrix.ffill().bfill().reindex(subpositions.index, axis=1).to_numpy() # t1 x n
        else: # assume don't move
            returns_matrix = returns_matrix.fillna(0).reindex(subpositions.index, axis=1).to_numpy() # t-1 x n

        scaling = subpositions['deltaposition'].to_numpy().reshape(1, -1) # 1 x t-1
        historical_pnl = pd.DataFrame((scaling * returns_matrix).T, index=subpositions_index, columns=dates) # n x t-1
        return historical_pnl


    @staticmethod
    def var(return_history: pd.Series, tail: int = 251, confidence_level: float = 0.95) -> float:
        """Calculates VaR off simple returns, not relative. Return history assumed sorted by date.
        """
        return_history = return_history[-tail:]
        return_history = return_history.sort_values()
        return_history = np.array(return_history)
        
        if confidence_level == 0.95 and tail == 251:
            return 0.9 * return_history[12] + 0.1 * return_history[13]
        else:
            return np.percentile(return_history, (1-confidence_level) * 100)
        
    
    @staticmethod
    def calculate_returns(
        df: pd.DataFrame,
        price_col: str = 'price',
    ) -> pd.DataFrame:
        """Calculates absolute, percentage, and log returns over time. Drops NA.
        NOTE: casts all price to non-negative. For electricity / basis prices, model them differently.

        Args:
            df (pd.DataFrame).
            price_col (str, optional) Defaults to 'price'.

        Returns:
            pd.DataFrame: New price_delta column.
        """
        df = PortfolioAnalysis._calculate_price_delta(df, price_col)
        df = PortfolioAnalysis._calculate_log_returns(df, price_col)
        df = df.dropna(subset=['simple_return', 'log_return'])
        return df

    @staticmethod
    def _calculate_price_delta(
        df: pd.DataFrame,
        price_col: str = 'price',
    ) -> pd.DataFrame:
        """Calculates absolute price differences over time. Does not drop NA.

        Args:
            df (pd.DataFrame).
            price_col (str, optional) Defaults to 'price'.

        Returns:
            pd.DataFrame: New price_delta column.
        """
        df['price_delta'] = df.groupby(['px_location', 'contract_month'])[price_col].diff()
        return df

    @staticmethod
    def _calculate_simple_return(
        df: pd.DataFrame,
        price_col: str = 'price',
    ) -> pd.DataFrame:
        """Calculates simple returns (percentage) over time. Does not drop NA.

        Args:
            df (pd.DataFrame).
            price_col (str, optional) Defaults to 'price'.

        Returns:
            pd.DataFrame: New simple_return column.
        """
        df['tmp'] = df[price_col].abs()
        prices = df.groupby(['px_location', 'contract_month'])['tmp']
        # df['simple_return'] = prices.diff() / prices.shift().abs()
        df['simple_return'] = prices.pct_change()
        df = df.drop(columns='tmp')
        return df

    @staticmethod
    def _calculate_log_returns(
        df: pd.DataFrame,
        price_col: str = 'price',
    ) -> pd.DataFrame:
        """Calculates log returns over time. Does not drop NA.

        Args:
            df (pd.DataFrame).
            price_col (str, optional) Defaults to 'price'.

        Returns:
            pd.DataFrame: New simple_return column.
        """
        df = PortfolioAnalysis._calculate_simple_return(df, price_col)
        df['log_return'] = np.where(
            (df['simple_return'] <= -1) | (df['simple_return'].isna()),
            np.nan,
            np.log1p(1e-9 + df['simple_return'])
        )

        return df

    @staticmethod
    def clean_prices(
        df: pd.DataFrame,
        price_col: str = 'price',
        date_col: str = 'px_date'
    ) -> pd.DataFrame:
        """Drops rows where any instrument on a given date is missing prices.

        Args:
            df (pd.DataFrame): pandas df to clean.
            price_col (str, optional): Name of price column. Defaults to 'price'.
            date_col (str, optional): Name of date column. Defaults to 'valuation_date'.
        """

        dates_with_nan_counts = df.groupby(date_col)[price_col].apply(lambda r : r.isna().sum())
        print("Number of missing prices per date:")
        print(dates_with_nan_counts[dates_with_nan_counts != 0])

        good_dates = dates_with_nan_counts[dates_with_nan_counts == 0].index
        cleaned_df = df[df[date_col].isin(good_dates)]
        print(f"Number of rows deleted: {df.shape[0] - cleaned_df.shape[0]}")
        
        return cleaned_df
    
    @staticmethod
    def plot_timeseries(s1, n1='facade', title='Timeseries'):
        return Plot.plot_timeseries(s1, n1, title)

    @staticmethod
    def plot_timeseries_multiple(s1, s2, n1='trace 1', n2='trace 2', title='Timeseries'):
        return Plot.plot_timeseries_multiple(s1, s2, n1, n2, title)
    
    @staticmethod
    def make_multi_plot(plot_funcs, layout_title: str, rows = None, cols : int = 2, file_name: str = 'default', subplot_titles = []):
        return Plot.make_multi_plot(plot_funcs, layout_title, rows, cols, file_name, subplot_titles)
        