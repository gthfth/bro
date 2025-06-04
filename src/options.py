import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

def price_option(spot, strike, expiry, vol, r, type='call'):
    """
    Black-Scholes price for European call/put.
    spot:    Current price
    strike:  Option strike
    expiry:  Time to expiry (in years, e.g. 0.5)
    vol:     Implied volatility (annualized, e.g. 0.25)
    r:       Risk-free rate (annualized, e.g. 0.02)
    type:    'call' or 'put'
    """
    if expiry <= 0 or vol <= 0 or spot <= 0 or strike <= 0:
        raise ValueError("Inputs must be positive")
    d1 = (np.log(spot/strike) + (r + 0.5*vol*vol)*expiry) / (vol * np.sqrt(expiry))
    d2 = d1 - vol * np.sqrt(expiry)
    if type == 'call':
        price = spot * stats.norm.cdf(d1) - strike * np.exp(-r*expiry) * stats.norm.cdf(d2)
    elif type == 'put':
        price = strike * np.exp(-r*expiry) * stats.norm.cdf(-d2) - spot * stats.norm.cdf(-d1)
    else:
        raise ValueError("type must be 'call' or 'put'")
    return price

def calc_greeks(spot, strike, expiry, vol, r, type='call'):
    """Returns a dict of Black-Scholes Greeks: delta, gamma, vega, theta, rho"""
    d1 = (np.log(spot/strike) + (r + 0.5*vol*vol)*expiry) / (vol * np.sqrt(expiry))
    d2 = d1 - vol * np.sqrt(expiry)
    pdf_d1 = stats.norm.pdf(d1)
    cdf_d1 = stats.norm.cdf(d1)
    cdf_d2 = stats.norm.cdf(d2)

    greeks = {}
    if type == 'call':
        greeks['delta'] = cdf_d1
        greeks['theta'] = (-spot * pdf_d1 * vol / (2*np.sqrt(expiry)) -
                           r * strike * np.exp(-r*expiry) * cdf_d2)
        greeks['rho'] = strike * expiry * np.exp(-r*expiry) * cdf_d2
    else:
        greeks['delta'] = cdf_d1 - 1
        greeks['theta'] = (-spot * pdf_d1 * vol / (2*np.sqrt(expiry)) +
                           r * strike * np.exp(-r*expiry) * stats.norm.cdf(-d2))
        greeks['rho'] = -strike * expiry * np.exp(-r*expiry) * stats.norm.cdf(-d2)
    greeks['gamma'] = pdf_d1 / (spot * vol * np.sqrt(expiry))
    greeks['vega'] = spot * pdf_d1 * np.sqrt(expiry) / 100  # per 1 vol point (1%)
    return greeks

def plot_vol_smile(symbol, strikes, expiries, impvols, expiry_idx=0):
    """
    Plots volatility smile for a given symbol for one expiry.
    - strikes: array-like of strikes
    - expiries: array-like of all expiries (in years)
    - impvols: 2D array-like (expiries x strikes)
    - expiry_idx: which expiry row to plot (default 0)
    """
    vol_curve = np.array(impvols)[expiry_idx]
    plt.figure(figsize=(8,5))
    plt.plot(strikes, vol_curve, marker='o')
    plt.title(f"{symbol} Implied Volatility Smile (T={expiries[expiry_idx]:.2f}y)")
    plt.xlabel("Strike")
    plt.ylabel("Implied Volatility")
    plt.grid()
    plt.show()

# --- Example usage as main script ---
if __name__ == "__main__":
    # Example: Price a call
    spot, strike, expiry, vol, r = 200, 210, 0.5, 0.25, 0.03
    print("AAPL call option price:", price_option(spot, strike, expiry, vol, r, 'call'))
    print("Greeks:", calc_greeks(spot, strike, expiry, vol, r, 'call'))

    # Example: Plot vol smile for AAPL
    strikes = np.arange(180, 241, 10)
    expiries = [0.5] # 6 months
    # Faked implied vols -- usually fetched from data
    impvols = [[0.28, 0.27, 0.26, 0.25, 0.245, 0.25, 0.26]]
    plot_vol_smile("AAPL", strikes, expiries, impvols)