from pqsdk.backtest import execute, tearsheet, save_metrics, save_orders, save_inout_cash
from pqsdk import log

log.set_level(level=log.ERROR)

# 回测参数
params = {
    "cash": 1000000,
    "start_date": "2024-01-01",
    "end_date": "2024-05-25",
    "benchmark": "000300.SH",
    "stock_pool": "000300.SH".split(","),
    "unit": '1d',
    "adjust_period": 5,
    "hold_maxsize": 10,
}

#
strategy_file = "buy_and_hold.py"
# strategy_file = "stop_loss_strategy.py"
# strategy_file = "test_momentum_strategy.py"
# 执行回测
results = execute(parameters=params, strategy_file=strategy_file)

# print(results)
tearsheet(results)
save_metrics(results)
save_orders(results)
save_inout_cash(results)

