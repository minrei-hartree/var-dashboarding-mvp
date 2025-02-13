from collections.abc import Sequence
import os

import pandas as pd

from .database import Database

# Facade for backward compatbility
class HetcoPortDatabase:
    def __init__(self, debug: bool = False):
        self.db = Database(debug=debug)
        
    def get_traders_pnl(self, trader_names: list[str], overnight_or_actual: str = 'actual') -> pd.DataFrame:
        return self.db.traders.get_pnl(trader_names, overnight_or_actual)

    
    def get_trader_positions(self, trader_name: str, valuation_date: str = 'max') -> pd.DataFrame:
        return self.db.traders.get_positions_with_prices(trader_name, valuation_date)

    def get_commodity_index(self) -> pd.DataFrame:
        return self.db.commodities.get_commodity_index()
    
    def get_price_data(self, px_locations: Sequence, lookback_days: int = -1) -> pd.DataFrame:
        return self.db.prices.get_historical(px_locations, lookback_days)