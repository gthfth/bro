import sqlite3
import pandas as pd
from matplotlib import pyplot as plt
from datetime import datetime

DB_PATH = 'macro_data.sqlite'

def ensure_db():
    """Create the SQLite database and macro_data table, if not exists"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS macro_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            source TEXT,
            series TEXT,
            value REAL,
            region TEXT,
            other_info TEXT
        );
    """)
    conn.commit()
    conn.close()

def store_data(source, series, value, region, other_info=''):
    """Save macro/alt data in the database"""
    ensure_db()
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO macro_data (timestamp, source, series, value, region, other_info) 
        VALUES (?, ?, ?, ?, ?, ?)
    """, (ts, source, series, value, region, other_info))
    conn.commit()
    conn.close()

def fetch_gdp(country='US'):
    """Dummy GDP data by country"""
    fake_gdp = {
        'US': 25000 + 100 * pd.Timestamp(datetime.now()).year % 10,
        'JP': 5000 + 10 * pd.Timestamp(datetime.now()).year % 10,
        'CN': 18000 + 150 * pd.Timestamp(datetime.now()).year % 10
    }
    value = fake_gdp.get(country, 10000)
    store_data('Dummy', 'GDP', value, country)
    return value

def fetch_cpi(zone='EU'):
    """Dummy CPI data by economic zone"""
    fake_cpi = {
        'EU': 110 + 1 * pd.Timestamp(datetime.now()).month,
        'US': 120 + 1.2 * pd.Timestamp(datetime.now()).month,
        'JP': 105 + 0.8 * pd.Timestamp(datetime.now()).month
    }
    value = fake_cpi.get(zone, 100)
    store_data('Dummy', 'CPI', value, zone)
    return value

def fetch_alt_data(item, region):
    """Dummy alternate data (e.g., iPhone price)"""
    if item == 'iphone-14-price' and region == 'Tokyo':
        value = 850 + 10 * (pd.Timestamp(datetime.now()).month)
    elif item == 'iphone-14-price' and region == 'NYC':
        value = 900 + 10 * (pd.Timestamp(datetime.now()).month)
    else:
        value = 600
    store_data('Dummy', item, value, region)
    return value

def fetch_fx_pairs():
    """Dummy FX rates"""
    fx = {
        'USDJPY': 157 + pd.Timestamp(datetime.now()).month,
        'USDEUR': 0.91 + 0.01 * (pd.Timestamp(datetime.now()).month % 3),
        'USDCNY': 7.1 + 0.05 * (pd.Timestamp(datetime.now()).month % 3),
    }
    store_data('Dummy', 'fx_pairs', 0, 'global', other_info=str(fx))
    return fx

def update_macro_db():
    """Update the database with (dummy) latest macro/alt data"""
    fetch_gdp('US')
    fetch_cpi('EU')
    fetch_alt_data('iphone-14-price', 'Tokyo')
    fetch_fx_pairs()

def get_series(series, region):
    """Helper to pull a labeled time series from db as a dataframe (latest 10 records)"""
    ensure_db()
    conn = sqlite3.connect(DB_PATH)
    q = """
        SELECT timestamp, value FROM macro_data 
        WHERE series = ? AND region = ? ORDER BY timestamp DESC LIMIT 10
    """
    df = pd.read_sql_query(q, conn, params=(series, region))
    conn.close()
    df = df.sort_values('timestamp') # chronological order
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def demo_plot():
    """Demo: plot most recent US GDP, EU CPI, iPhone 14 price in Tokyo"""
    # Add 10 dummy dates to illustrate a time series
    for i in range(10):
        pd.Timestamp(datetime.now())  # dummy; not used, just for demonstration
        fetch_gdp('US')
        fetch_cpi('EU')
        fetch_alt_data('iphone-14-price', 'Tokyo')

    gdp = get_series('GDP', 'US')
    cpi = get_series('CPI', 'EU')
    iphone = get_series('iphone-14-price', 'Tokyo')

    fig, ax = plt.subplots(3, 1, figsize=(8, 10))
    if not gdp.empty:
        ax[0].plot(gdp['timestamp'], gdp['value'], marker='o')
        ax[0].set_title('US GDP')
    if not cpi.empty:
        ax[1].plot(cpi['timestamp'], cpi['value'], marker='o')
        ax[1].set_title('EU CPI')
    if not iphone.empty:
        ax[2].plot(iphone['timestamp'], iphone['value'], marker='o')
        ax[2].set_title('Tokyo: iPhone 14 (USD)')
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    update_macro_db()
    demo_plot()