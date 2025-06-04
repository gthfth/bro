# /src/alerts.py

import datetime

class Alert:
    CATEGORIES = ('risk', 'price', 'signal', 'custom')
    def __init__(self, category, message, triggered_by, symbol=None, user=None, timestamp=None, active=True):
        assert category in Alert.CATEGORIES, f"Invalid category: {category}"
        self.category = category
        self.message = message
        self.triggered_by = triggered_by
        self.symbol = symbol
        self.user = user
        self.timestamp = timestamp or datetime.datetime.now()
        self.active = active

    def __repr__(self):
        return (f"<Alert {self.category.upper()}:{self.symbol or '?'} {self.message} "
                f"@{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}, User:{self.user}, Active:{self.active}>")

class AlertSystem:
    def __init__(self, user_config=None):
        self.alerts = []  # In production: use DB or persistent store
        self.user_config = user_config or {}  # e.g. {'AAPL': {'drawdown': 5, 'price': 180}, ...}
    def trigger_alert(self, category, message, triggered_by, symbol=None, user=None):
        alert = Alert(category, message, triggered_by, symbol=symbol, user=user)
        self.alerts.append(alert)
        self.log_alert(alert)
        return alert
    def log_alert(self, alert):
        print(f"[{alert.timestamp}] ALERT ({alert.category.upper()}, {alert.symbol}): {alert.message}")
    def get_active_alerts(self, user=None, symbol=None):
        return [a for a in self.alerts if a.active 
                and (user is None or a.user == user)
                and (symbol is None or a.symbol == symbol)]
    def clear_alerts(self):
        for alert in self.alerts:
            alert.active = False

# ------------- Example trigger logic -------------

def check_price_drawdown(prices, threshold_pct=5, symbol=None, alert_system=None, user=None):
    """
    Trigger alert if drawdown from max to latest > threshold_pct. 
    prices: list of floats, latest last.
    """
    if not prices: return None
    peak = max(prices)
    latest = prices[-1]
    dd_pct = ((peak - latest) / peak) * 100 if peak > 0 else 0
    if dd_pct > threshold_pct:
        msg = f"Drawdown exceeded {threshold_pct}%: Current DD {dd_pct:.2f}% for {symbol}"
        return alert_system.trigger_alert("risk", msg, triggered_by="check_price_drawdown", symbol=symbol, user=user)
    return None

def check_price_threshold(price, threshold, direction, symbol=None, alert_system=None, user=None):
    """
    Trigger if price crosses threshold. 
    direction: 'above' or 'below'
    """
    if (direction == 'above' and price > threshold) or (direction == 'below' and price < threshold):
        msg = f"Price {direction} {threshold} for {symbol}: Current {price}"
        return alert_system.trigger_alert("price", msg, triggered_by="check_price_threshold", symbol=symbol, user=user)
    return None

# ------------- Demo usage -------------

if __name__ == "__main__":
    alerts = AlertSystem(user_config={'AAPL': {'drawdown': 5, 'price_above': 200, 'price_below': 150}})
    # Simulated price series for AAPL
    price_series = [175, 180, 182, 185, 178, 165]  # drawdown from 185 to 165 ~10.8%
    # Drawdown alert
    check_price_drawdown(price_series, threshold_pct=alerts.user_config['AAPL']['drawdown'],
                         symbol='AAPL', alert_system=alerts, user='alice')
    # Price threshold alerts
    check_price_threshold(165, 200, 'above', symbol='AAPL', alert_system=alerts, user='alice')
    check_price_threshold(165, 150, 'below', symbol='AAPL', alert_system=alerts, user='alice')
    # Price drops below 150
    check_price_threshold(140, 150, 'below', symbol='AAPL', alert_system=alerts, user='alice')

    # View active alerts
    print("Active Alerts:", alerts.get_active_alerts())