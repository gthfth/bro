import numpy as np
import pandas as pd

class Portfolio:
    def __init__(self, initial_cash=1_000_000):
        self.assets = {}           # dict: symbol -> price DataFrame
        self.positions = pd.DataFrame()   # Daily positions (symbol x date)
        self.trades = []           # Stores trade records
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.nav_series = pd.Series(dtype=float)  # Series of NAV over time

    def add_asset(self, df, symbol):
        """Adds an asset's price DataFrame. Expects columns: date, open, high, low, close, volume."""
        if 'date' in df.columns:
            df = df.copy()
            df.set_index('date', inplace=True)
        self.assets[symbol] = df

    def simulate_ma_strategy(self, fast=10, slow=30, fee=0.0005, leverage=1.0):
        """
        Implements a cross-asset MA crossover strategy:
        - Long when fast MA > slow MA, short when fast MA < slow MA.
        - Fee charged per trade (fraction of notional).
        - Leverage applied to signals.
        Supports multiple assets; trades daily.
        """

        all_dates = sorted(set(date for df in self.assets.values() for date in df.index))
        positions = pd.DataFrame(index=all_dates, columns=self.assets.keys(), dtype=float).fillna(0)
        signals = {}

        for symbol, df in self.assets.items():
            close = df['close']
            fast_ma = close.rolling(fast).mean()
            slow_ma = close.rolling(slow).mean()
            # Signal: 1 = long, -1 = short
            signal = np.where(fast_ma > slow_ma, 1, -1)
            signals[symbol] = pd.Series(signal, index=close.index)
            positions[symbol] = leverage * signals[symbol]
        
        # Forward-fill for any missing signals (edge dates)
        positions.ffill(inplace=True)

        # Trades: when position changes, record a trade and apply fee
        self.trades = []
        prev_pos = positions.shift(1).fillna(0)
        for date in positions.index:    
            for symbol in self.assets:
                size_change = positions.at[date, symbol] - prev_pos.at[date, symbol]
                if size_change != 0:
                    price = self.assets[symbol].at[date, 'close'] if date in self.assets[symbol].index else np.nan
                    trade_fee = abs(size_change) * price * fee
                    self.trades.append({
                        'date': date, 'symbol': symbol, 'size': size_change, 'price': price, 'fee': trade_fee
                    })

        self.positions = positions

    def calc_nav(self):
        """Calculates NAV time series using daily close prices and positions."""
        nav = pd.Series(index=self.positions.index, dtype=float)
        nav.iloc[0] = self.initial_cash
        prev_nav = self.initial_cash
        
        for i, date in enumerate(self.positions.index[1:], start=1):
            daily_pnl = 0
            for symbol in self.assets:
                pos_yday = self.positions.iloc[i-1][symbol]
                price_yday = self.assets[symbol]['close'].get(date, np.nan)
                price_today = self.assets[symbol]['close'].get(date, np.nan)
                if not np.isnan(price_today) and not np.isnan(price_yday):
                    daily_ret = (price_today - price_yday) / price_yday
                    daily_pnl += pos_yday * daily_ret * prev_nav / len(self.assets)
            nav.iloc[i] = prev_nav + daily_pnl
            prev_nav = nav.iloc[i]
        
        self.nav_series = nav
        return nav

    def get_positions(self):
        """Returns positions DataFrame."""
        return self.positions.copy()

    def get_trades(self):
        """Returns DataFrame of trade records."""
        return pd.DataFrame(self.trades)    