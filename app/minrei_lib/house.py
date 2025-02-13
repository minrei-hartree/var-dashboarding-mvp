import pandas as pd

from .base import query


class HouseQueries:
    def __init__(self, db):
        self._db = db
    
    @query("get-house-positions-latest.sql")
    def get_positions_latest(self) -> pd.DataFrame:
        return {}

    def _process_get_positions_latest(self, df: pd.DataFrame) -> pd.DataFrame:
        df['valuation_date'] = pd.to_datetime(df['valuation_date'])
        df['px_location'] = df['px_location'].str.upper()
        df['px_location'] = df['px_location'].str.strip()
        # group positions
        cols_to_index = ['valuation_date', 'px_location', 'forward_month']
        cols_to_sum = ['deltaposition', 'gammaposition', 'thetaposition', 'vegaposition']
        cols_to_first = list(set(df.columns) - set(cols_to_sum) - set(cols_to_index))
        df = df.groupby(cols_to_index).agg({
            **{col: 'sum' for col in cols_to_sum},
            **{col: 'first' for col in cols_to_first}
        }).reset_index()
        return df
    
    @query("get-house-historical-pl.sql")
    def get_historical_pl(self, var_levels: list[str], start_valuation_date: str = '-1'):
        if isinstance(var_levels, str):
            var_levels = [var_levels]

        var_levels = ", ".join(f"'{name}'" for name in var_levels)
        var_levels = f"({var_levels})"
        return {
            'var_levels': var_levels,
            'start_valuation_date': start_valuation_date
        }