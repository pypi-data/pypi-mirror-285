import pandas as pd
import numpy as np
from pqsdk.api import get_history


def get_portfolio_metrics():
    """
    在实盘中，根据投资的的交易数据，出入金数据和最新的Tick数据，计算投资组合的重要Metrics，比如：
        1. cost：持仓成本，截止当前的持仓成本余额
        2. market_value：持仓市值，截止当前的持仓市值，由最新的持仓标的价格计算所得。如果投资组合已经被全部平仓，则持仓市值为0，此时持仓成本为正数为亏损，持仓成本为负数为盈利。
        3. pnl：盈亏(profit and loss)，等于持仓市值 - 持仓成本 = market_value - cost。
        4. principal：本金，截止目前为止的投资组合出入金汇总。
        5. cash：现金，即截止今日剩余现金，等于本金 - 成本 = principal - cost
        6. asset：资产，等于现金 + 持仓市值 = cash + market_value
        7. position_size：仓位，等于持仓市值/资产 = market_value / asset
        8. nav：净值(Net Asset Value)，等于资产/本金 = asset / principal
        9. return：收益率， 等于净值 - 1 = nav - 1
    :return:
    """
    # portfolio_ids = [str(id) for id in portfolio_ids]
    # sql_str = f"SELECT portfolio_id, sec_code, trade_date, is_buy, volume, amount as cost from trd_trade tt " \
    #           f"WHERE deleted =0 and tt.portfolio_id in ({','.join(portfolio_ids)}) " \
    #           f"order by portfolio_id, sec_code, trade_date"
    # df = pd.read_sql(sql_str, engine)
    df = pd.read_csv("storage/orders/orders_20240526_170558.csv")
    df['cost'] = df['volume'] * df['price']
    df = df[["sec_code", "trade_date", "is_buy", "volume", "cost"]]

    # volume, amount: 买单为正数，卖单为负数
    df['volume'] = np.where(df['is_buy'], df['volume'], df['volume'] * -1)
    df['cost'] = np.where(df['is_buy'], df['cost'], df['cost'] * -1)

    # 计算每个股票的目前持仓sum(volume)、成本sum(cost)
    stock_df = df.groupby(['sec_code'])[['volume', 'cost']].sum()
    stock_df = stock_df.reset_index()

    # 获取目前持仓的最新股票价格

    unit = '1m'
    sec_code_lst = stock_df['sec_code'].unique().tolist()
    # price_df = get_last_ticks(user=user, sec_code_lst=sec_code_lst, fields=['sec_code', 'last_price'])
    if unit == '1d':
        current_dt = "2024-05-24"
        price_df = get_history(start_date=current_dt,
                               end_date=current_dt,
                               unit=unit,
                               field='close',
                               security_list=sec_code_lst,
                               dividend_type='back',
                               expect_df=True)
    else:
        current_dt = "2024-05-24 15:00:00"
        price_df = get_history(start_datetime=current_dt,
                               end_datetime=current_dt,
                               unit=unit,
                               field='close',
                               security_list=sec_code_lst,
                               dividend_type='back',
                               expect_df=True)
    price_df = price_df.T.reset_index()
    price_df.columns = ["sec_code", "last_price"]
    stock_df = pd.merge(stock_df, price_df, on='sec_code')

    # 计算最新的持仓市值，盈亏
    stock_df['market_value'] = stock_df['volume'] * stock_df['last_price']
    stock_df['pnl'] = stock_df['market_value'] - stock_df['cost']

    # 统计投资组合基本的Metrics
    metrics_dict = stock_df[['cost', 'market_value', 'pnl']].sum().to_dict()

    # 本金: 出入金汇总
    # cash_sql = f"SELECT portfolio_id, sum(quota_value) as principal FROM trd_inout_quota_account tiqa " \
    #            f"WHERE deleted =0 and portfolio_id in ({','.join(portfolio_ids)}) group by portfolio_id"
    # cash_df = pd.read_sql(cash_sql, engine).set_index('portfolio_id')
    cash_df = pd.read_csv("storage/inout_cash/inout_cash_20240526_170558.csv")
    metrics_dict['principal'] = cash_df['cash'].sum()
    # metrics_df = pd.merge(metrics_df, cash_df, left_index=True, right_index=True, how='inner')

    # 截止今日剩余现金: 本金汇总 - 成本汇总
    metrics_dict['cash'] = metrics_dict['principal'] - metrics_dict['cost']
    # 资产：
    metrics_dict['asset'] = metrics_dict['cash'] + metrics_dict['market_value']
    # 仓位
    metrics_dict['position_size'] = metrics_dict['market_value'] / metrics_dict['asset']
    # 净值
    metrics_dict['nav'] = metrics_dict['asset'] / metrics_dict['principal']
    # 收益率： 净值 - 1
    metrics_dict['return_rate'] = metrics_dict['nav'] - 1

    return metrics_dict


if __name__ == '__main__':
    ret = get_portfolio_metrics()
    print(ret)
