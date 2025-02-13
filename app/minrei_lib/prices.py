import pandas as pd

from .base import query


class PriceQueries:
    def __init__(self, db):
        self._db = db
    
    def get_historical(self, px_locations: list[str], lookback_days: int = -1, start_date: str = '-1') -> pd.DataFrame:
        """Get historical prices in USD.
        NOTE: APPLIED: FX, PRICE BASIS

        Args:
            px_locations (list[str]): Tickers.
            lookback_days (int, optional): Defaults to -1 (full price history).

        Returns:
            _type_: Price histories of ticker(s).
        """
        if isinstance(px_locations, str):
            px_locations = [px_locations]

        px_locations = ", ".join(f"'{loc}'" for loc in px_locations)
        px_locations = f"({px_locations})"

        # full
        if lookback_days == -1:
            return self.get_full(px_locations, lookback_days, start_date)

        # latest - lookback
        if start_date == '-1':
            return self.get_latest(px_locations, lookback_days, start_date)

        # start - lookback
        return self.get_start_lookback(px_locations, lookback_days, start_date)
    
    @query("get-prices-full.sql")
    def get_full(self, px_locations: list[str], lookback_days: int = -1, start_date: str = '-1') -> pd.DataFrame:
        return {
            'px_locations': px_locations,
            'lookback_days': lookback_days,
            'start_date': start_date,
        }
    
    def _process_get_full(self, df: pd.DataFrame) -> pd.DataFrame:
        return self._process_prices_helper(df)

    @query("get-prices-latest-lookback.sql")
    def get_latest(self, px_locations: list[str], lookback_days: int = -1, start_date: str = '-1') -> pd.DataFrame:
        return {
            'px_locations': px_locations,
            'lookback_days': lookback_days,
            'start_date': start_date,
        }
    
    def _process_get_latest(self, df: pd.DataFrame) -> pd.DataFrame:
        return self._process_prices_helper(df)

    @query("get-prices-start-lookback.sql")
    def get_start_lookback(self, px_locations: list[str], lookback_days: int = -1, start_date: str = '-1') -> pd.DataFrame:
        return {
            'px_locations': px_locations,
            'lookback_days': lookback_days,
            'start_date': start_date,
        }
    
    def _process_get_start_lookback(self, df: pd.DataFrame) -> pd.DataFrame:
        return self._process_prices_helper(df)

    
    def _process_prices_helper(self, df: pd.DataFrame) -> pd.DataFrame:
        df['px_date'] = pd.to_datetime(df['px_date'])
        df['contract_month'] = pd.to_datetime(df['contract_month'])

        df['px_location'] = df['px_location'].str.upper()
        df['px_location'] = df['px_location'].str.strip()
        df['price'] = df['price'] / df['price_basis'].fillna(1)
        df['price'] = df['price'] / df['rate']

        # clean extra prices for same contract_month
        df = df.drop_duplicates(subset=['px_location', 'px_date', 'contract_month'], keep='first')

        return df