import pandas as pd

from .base import query


class CommodityQueries:
    def __init__(self, db):
        self._db = db
    
    @query("get-commodity-index.sql")
    def get_commodity_index(self):
        """Get commodity index data"""
        return {}  # No parameters needed for this query

    @query("get-seasonal-index.sql")
    def get_seasonal_index(self):
        """Get seasonal commodities"""
        return {}  # No parameters needed for this query
    
    def _process_get_seasonal_index(self, df: pd.DataFrame) -> list[str]:
        df['px_location'] = df['px_location'].str.upper()
        return df['px_location'].tolist()