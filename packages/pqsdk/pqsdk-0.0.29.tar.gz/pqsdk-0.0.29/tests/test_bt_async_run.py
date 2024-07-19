from pqsdk.backtest import execute, tearsheet, save_metrics, save_orders, save_inout_cash
from pqsdk import log

log.set_level(level=log.DEBUG)

# 回测参数
params = {
    "cash": 1000000,
    "start_date": "2024-07-12",
    "end_date": "2024-07-12",
    "benchmark": "000300.SH",
    "stock_pool": "000985.SH".split(","),
    "unit": '1m',
    "adjust_period": 5,
    "hold_maxsize": 5,
    "dividend_type": "none",
}

#
strategy_file = "async_run_strategy.py"
# 执行回测
results = execute(parameters=params, strategy_file=strategy_file)

if not results['orders'].empty:
    print(results['orders'])
    # tearsheet(results)
    # save_metrics(results)
    # save_orders(results)
    # save_inout_cash(results)

