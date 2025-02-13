from collections.abc import Sequence
from typing import Dict, Optional
import urllib
import os

import pandas as pd
import sqlalchemy as sa

from .commodities import CommodityQueries
from .prices import PriceQueries
from .traders import TraderQueries
from .house import HouseQueries

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
SQL_DIRECTORY = os.path.join(MODULE_DIR, "sql")

class Database:
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.engine = self._init_risk_engine()

        # Initialize query interfaces
        self.traders = TraderQueries(self)
        self.house = HouseQueries(self)
        self.prices = PriceQueries(self)
        self.commodities = CommodityQueries(self)
    
    def _init_risk_engine(self, server='nysqlrisk01', db='dbrisk', driver='{ODBC Driver 17 for SQL Server}'):
        # Trusted connection to instance
        params = urllib.parse.quote_plus(f"DRIVER={driver};"
                                        f"SERVER={server};"
                                        f"DATABASE={db};"
                                        "Trusted_Connection=Yes")

        # Connect using the specified parameters
        engine = sa.create_engine("mssql+pyodbc:///?odbc_connect={}".format(params))
        self.log(f'Successfully connected to db server: {server}')
        return engine
    
    def _inject_and_execute_sql(
            self,
            query_file: str,
            params: Optional[Dict[str, any]] = None,
        ) -> pd.DataFrame:
        """Injects parameters into a SQL query file and executes it.

        Args:
            query_file (str): Name of SQL file to execute.
            params (Optional[Dict[str, any]], optional): Dictionary of parameters to inject into query.

        Returns:
            pd.DataFrame: Contains query results.
        """
        query_path = os.path.join(SQL_DIRECTORY, query_file)
        if not query_path:
            raise FileNotFoundError(f"SQL file not found: {query_file}")
        
        try:
            with open(query_path, 'r') as f:
                sql_template = f.read()
                params = params or {}
                sql_query = sql_template.format(**{
                    k: v
                    for k, v in params.items()
                })
                self.log(sql_query)
                return pd.read_sql_query(sql_query, self.engine)

        except KeyError as e:
            raise ValueError(f"Missing required parameter: {str(e)}")
        except ValueError as e:
            raise ValueError(f"Parameter validation failed: {str(e)}")
        except Exception as e:
            raise type(e)(f"Query execution failed: {str(e)}")
    
    def log(self, message: str) -> None:
        if self.debug:
            print(f"[DEBUG] {message}")
