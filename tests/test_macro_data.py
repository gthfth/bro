import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import macro_data

def test_gdp_fetch():
    df = macro_data.fetch_gdp('US')
    assert 'date' in df and 'value' in df and len(df) > 0

def test_cpi_fetch():
    df = macro_data.fetch_cpi('EU')
    assert 'date' in df and 'value' in df and len(df) > 0

def test_alt_data():
    df = macro_data.fetch_alt_data('iphone-14', 'tokyo')
    assert 'date' in df and 'value' in df and len(df) > 0

def test_fx_pairs():
    df = macro_data.fetch_fx_pairs()
    assert 'pair' in df and 'rate' in df and len(df) > 0
    