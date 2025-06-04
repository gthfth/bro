import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import portfolios
import pandas as pd
import numpy as np

def make_fake_asset(symbol, prices):
    return pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=len(prices)),
        "open": prices,
        "high": prices,
        "low": prices,
        "close": prices,
        "volume": [1000]*len(prices)
    })

def test_portfolio_add_and_simulate():
    asset1 = make_fake_asset("AAA", [10, 11, 12, 13, 12, 11, 12, 14, 15, 16])
    asset2 = make_fake_asset("BBB", [20, 19, 18, 20, 21, 22, 22, 21, 21, 20])
    p = portfolios.Portfolio(initial_cash=10000)
    p.add_asset(asset1, "AAA")
    p.add_asset(asset2, "BBB")
    p.simulate_ma_strategy(fast=2, slow=3, fee=0.001, leverage=1.0)
    assert "AAA" in p.get_positions()
    assert "BBB" in p.get_positions()
    trades = p.get_trades()
    assert not trades.empty
    assert set(trades.columns) >= {"date", "symbol", "size", "price", "fee"}

def test_nav_calc_runs():
    asset1 = make_fake_asset("AAA", [100, 101, 99, 102, 104, 103, 105])
    p = portfolios.Portfolio(initial_cash=5000)
    p.add_asset(asset1, "AAA")
    p.simulate_ma_strategy(fast=2, slow=3, fee=0.0001, leverage=1)
    nav = p.calc_nav()
    assert isinstance(nav, pd.Series)
    assert len(nav) == len(asset1)
    assert np.all(nav > 0)  