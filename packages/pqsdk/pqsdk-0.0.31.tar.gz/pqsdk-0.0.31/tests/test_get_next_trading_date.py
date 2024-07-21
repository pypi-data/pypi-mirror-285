from pqsdk.api import is_open_trade_date, get_next_trading_date

current_date = '2024-05-24'
res = get_next_trading_date(current_date)
print(res)
