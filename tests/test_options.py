import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import options

def test_price_option_call():
    price = options.price_option(100, 100, 1, 0.2, 0.01, 'call')
    # Accept result to the nearest penny:
    assert abs(price - 8.43332) < 0.01

def test_price_option_put():
    price = options.price_option(100, 100, 1, 0.2, 0.01, 'put')
    assert abs(price - 7.43830) < 0.01

def test_greeks_shape():
    greeks = options.calc_greeks(100, 100, 1, 0.2, 0.01, 'call')
    assert {'delta','gamma','vega','theta','rho'} <= set(greeks)

def test_plot_smile_runs():
    options.plot_vol_smile("AAPL", [90,100,110], [0.25], [[0.28,0.23,0.25]])    
    