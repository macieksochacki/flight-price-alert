def should_alert(price, previous_prices):
    return len(previous_prices) == 0 or price < min(previous_prices)
