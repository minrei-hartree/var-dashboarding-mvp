import datetime as datetime
from dateutil.relativedelta import relativedelta

import pandas as pd

from .base import query


class TraderQueries:
    def __init__(self, db):
        self._db = db
    
    @query("get-traders-pnl.sql")
    def get_pnl(self, trader_names: list[str], overnight_or_actual: str = 'actual'):
        """Get historical PnL for specified traders. Uses trader_pl_systemgenerate."""
        if isinstance(trader_names, str):
            trader_names = [trader_names]

        trader_names = ", ".join(f"'{name}'" for name in trader_names)
        trader_names = f"({trader_names})"
        return {
            'trader_names': f"({trader_names})",
            'overnight_or_actual': overnight_or_actual
        }
    
    def _process_get_pnl(self, df: pd.DataFrame) -> pd.DataFrame:
        df['valuation_date'] = pd.to_datetime(df['portfoliodate'])
        df = df.rename(columns={'portfoliodate': 'valuation_date'})
        return df

    @query("get-trader-positions-latest.sql")
    def get_positions_latest(self, trader_name: str):
        """Get positions for a specific trader.
        NOTE: weight applied onto deltaposition. prices are not cleaned.
        """
        return {
            'trader_name': trader_name,
        }
    
    def _process_get_positions_latest(self, df: pd.DataFrame) -> pd.DataFrame:
        return self.process_positions_helper(self, df)
    
    @query("get-trader-positions.sql")
    def get_positions(self, trader_name: str, valuation_date: str):
        """Get positions for a specific trader."""
        return {
            'trader_name': trader_name,
            'valuation_date': valuation_date,
        }
    
    def _process_get_positions_latest(self, df: pd.DataFrame) -> pd.DataFrame:
        return self.process_positions_helper(df)
    
    @query("get-trader-positions-with-prices.sql")
    def get_positions_with_prices(self, trader_name: str, valuation_date: str = 'max'):
        """Get positions for a specific trader with associated prices."""
        return {
            'trader_name': trader_name,
            'valuation_date': valuation_date
        }
    
    def _process_get_positions(self, df: pd.DataFrame) -> pd.DataFrame:
        return self.process_positions_helper(df)

    def process_positions_helper(self, df: pd.DataFrame) -> pd.DataFrame:
        df['valuation_date'] = pd.to_datetime(df['valuation_date'])
        df['px_location'] = df['px_location'].str.upper()
        df['px_location'] = df['px_location'].str.strip()
        df['deltaposition'] *= df['weight'] / 100
        df['gammaposition'] *= df['weight'] / 100
        df['thetaposition'] *= df['weight'] / 100
        df['vegaposition'] *= df['weight'] / 100
        # guess contract month if only forward month present
        mask = df['contract_month'].isna()
        def impute_contract_month(fm, vd):
            cm = vd + relativedelta(months=fm-1)
            cm = cm - relativedelta(days=cm.day-1)
            cm = pd.to_datetime(cm).strftime('%Y-%m-%d')
            return cm
        df.loc[mask, 'contract_month'] = \
        df.loc[mask, 'contract_month'] = df[mask].apply(lambda row : impute_contract_month(row['forward_month'], row['valuation_date']), axis=1)
        df['contract_month'] = pd.to_datetime(df['contract_month'])

        # group positions
        cols_to_index = ['valuation_date', 'px_location', 'forward_month']
        cols_to_sum = ['deltaposition', 'gammaposition', 'thetaposition', 'vegaposition']
        cols_to_first = list(set(df.columns) - set(cols_to_sum) - set(cols_to_index))
        df = df.groupby(cols_to_index).agg({
            **{col: 'sum' for col in cols_to_sum},
            **{col: 'first' for col in cols_to_first}
        }).reset_index()
        return df

    
    @query("get-trader-historical-pl.sql")
    def get_historical_pl(self, level_names: list[str]):
        if isinstance(level_names, str):
            level_names = [level_names]

        level_names = ", ".join(f"'{name}'" for name in level_names)
        level_names = f"({level_names})"
        return {
            'level_names': level_names
        }
    
    def _process_get_historical_pl(self, df: pd.DataFrame) -> pd.DataFrame:
        df['valuation_date'] = pd.to_datetime(df['valuation_date'])
        return df
    
    def list_groups(self):
        return [
            'AGRICULTURE',
            'BUNKER',
            'DIST PHY',
            'DISTILLATES',
            'FINANCE',
            'Former for 2025',
            'Former Trader',
            'FREIGHT & SHIPPING',
            'FUEL OIL',
            'GASOLINE',
            'GENEVA OIL PROP',
            'GLOBAL BIOFUELS',
            'Hartree Asset',
            'Hartree Entities',
            'Hartree Extrinsic Hedge',
            'HOUSE EMISSIONS',
            'House Hedge',
            'HPPGCO',
            'HPPGCO LNG',
            'LONDON DIST PHY',
            'LONDON OIL PROP',
            'MANAGEMENT',
            'MARKETING',
            'METALS',
            'OPTIONS',
            'SINGAPORE/APAC OIL',
            'SINGAPORE/APAC OTHER',
            'STEEL',
            'UK SECURITIES',
            'US NAT GAS',
            'US OIL PROP',
            'US POWER',
            'US SECURITIES'
        ]
    
    def list_traders(self):
        return [
            'A. Amann',
            'A. Bailey',
            'A. Candina',
            'A. Dalmia',
            'A. Grey/J. Robertson',
            'A. Hagerty',
            'A. Hoffmeyer',
            'A. Hoguet',
            'A. Lewis',
            'A. Mardirossian',
            'A. Oberhauser',
            'A. Zabolotskiy',
            'B. Johnston',
            'B. Keogh',
            'B. Mycock',
            'BlackSea',
            'C. Godefroy',
            'C. McAleese',
            'C. Sbraccia',
            'C. Schaefer/P. Collins',
            'CatchAllBucket',
            'Channelview',
            'D. Filatov',
            'D. Gonzalez',
            'D. Rosenberg',
            'D. Strasdin',
            'Derivatives (LNG)',
            'Derivatives (Peaker)',
            'Derivatives (Storage)',
            'E. Byberi',
            'E. Houache',
            'E. Ram',
            'E. Tay',
            'E. Valverde',
            'F. Marada/J. Reichl',
            'Former HPLP Traders',
            'Former HPPG Traders',
            'Former Trader',
            'G. Cicerani',
            'G. Shevill',
            'H. Thwaites (Comm)',
            'H. Thwaites (Prop)',
            'H. Thwaites (WH)',
            'H. Wooles',
            'House Avebury',
            'House Costs',
            'House Equities',
            'House pooling',
            'House underhedge',
            'House Vertree',
            'HPPG House',
            'HPPG MKT HOUSE',
            'J. Barker',
            'J. Brooks',
            'J. De Abreu',
            'J. Fish',
            'J. Gillespie',
            'J. Hornback',
            'J. Lemme',
            'J. Murphy',
            'J. Pedersen',
            'J. Santini',
            'J. Shah',
            'J. Sparling',
            'J. Stanley',
            'J. Syrett',
            'J. Treco',
            'J. Weidlich',
            'K. Billick',
            'K. Schmidt',
            'K. Tsai',
            'Kildair',
            'L. Berns',
            'L. Berns/S. Potolsky',
            'L. Foss-Skiftesvik',
            'L. Gjenari/V. Kekec',
            'L. Hopper',
            'M. Breuss',
            'M. Broillet',
            'M. Brouhard',
            'M. Ciano',
            'M. Heinemann',
            'M. Hermens',
            'M. Horreaux',
            'M. Kong',
            'M. Poray/D. Bhatia',
            'M. Rainger',
            'M. Rodrigues',
            'M. Rosales',
            'M. Slater',
            'M. Sun',
            'M. Wright',
            'Metallia (Comm)',
            'Metallia (Spec)',
            'N. Khan',
            'N. Nath (Comm)',
            'N. Nath (Prop)',
            'N. Peffley',
            'NEC',
            'NERP',
            'O. Bozhko',
            'P. Chen',
            'P. Garske',
            'P. Jacobs/D. Wolfert',
            'P. Larouche',
            'Peakers UK',
            'Power Supply',
            'R. Dhir',
            'R. Goldsworthy',
            'R. Hawkes',
            'R. Kochemirovskii',
            'R. Lee',
            'R. Martinez',
            'R. McLeod',
            'R. Odedra',
            'R. Renshaw',
            'R. Tan',
            'R. Waerner',
            'S. Barbouttis/R. McMillan',
            'S. Evans',
            'S. Garnas',
            'S. Goldblatt',
            'S. Gu',
            'S. Hendel',
            'S. Honeyball',
            'S. Lee',
            'S. Potolsky',
            'S. Verma',
            'S. Waters',
            'SGM Bunker',
            'Systematic Options',
            'T. Lefebvre',
            'T. Lien',
            'T. McMahon',
            'T. Nolte',
            'T. Stenvoll/A. Kozhipatt',
            'V. Goyal',
            'V. Nayar',
            'VER Upstream',
            'X. Gould Marks',
            'X. Liu',
            'Z. Mandel',
        ]