from pqsdk import g, log
from pqsdk.api import *
# --------------------------------------------------
# 步骤2、开发策略代码 - 开始
# --------------------------------------------------
import datetime
import logging
import traceback
import pandas as pd
import numpy as np
import talib as ta
import numpy
from sklearn.linear_model import LinearRegression

# 设置log level
log.set_level(level=logging.DEBUG)


def initialize(context):
    """
    构造持仓字典和退出价格
    format:
    g.positions_dict = {"000001.SZ": {"init_date": "2024-03-03",  # 建仓时间
                                      "transact_date": "2024-03-03",  # 最后交易时间
                                      "highest_date": "2024-03-03",  # 最高价时间
                                      "highest_price": 12,  # 最高价格
                                      "openPositionAtr": 1,  # atr用于跟踪止盈止损，记录开仓时候的atr，记录下来让其固定不变
                                      "longOpenPositionLowPrice": 8,  # 多头开仓的价格的最低价，记录下来让其固定不变
                                      "exitPriceType": "开",  # 开 、 松、 紧 ，超紧，现在使用的止损线类型
                                      "startExitPrice": 8,  # 开始止损-退出价格
                                      "looseExitPrice": 10,  # 宽松止损-退出价格
                                      "realExitPrice": 18,  # 实际止损-退出价格
                                      "exitPriceChangeReason": "价格跌破平均建仓成本价",  # 止损线改变的原因
                                      }
                        }
    """
    g.positions_dict = dict()
    g.trade_idx = 0  # 调仓编号


def process_initialize(context):
    """
    每次启动策略都会执行的初始化函数，一般用来初始化一些不能持久化保存的内容. , 比如以__开头的全局变量属性，或者计划任务，在 initialize 后执行.
    """

    # 获取策略执行的字典
    strategy_params = context.parameters
    log.debug(f"策略执行的参数字典: type={type(strategy_params)} {strategy_params}")
    for k, v in context.parameters.items():
        if type(v) == str:
            v_print = f'"{v}"'
        else:
            v_print = v
        log.debug(f"    {k}={v_print}")

    # Prompt 参数
    # log.info(f"输入Prompt: {context.parameters.get('prompt', '')}")

    # 每次策略启动需要重置的参数
    g.increase1d = 0.087  # 前一日涨幅，超过这个涨幅的股票，在股票初筛函数Trade_Open()中过滤掉
    # 定义止损所需要的参数
    g.isEarlyExitOn = False  # 是否启用止盈止损,设为False即可关闭止盈止损
    g.atr_period = 14
    g.isStartStopOn = False  # 是否启动初始的止损线
    g.startStopAtrMulti = 0.5  # 开始止损线-开始的跟踪止盈止损atr的倍数
    g.isLooseStopOn = False  # 是否启用宽松止损线
    g.looseStopAtrMulti = 1  # 宽松止损线-跟踪止盈止损的atr的倍数
    g.slop_period = 90

    g.force_close = True  # 止盈止损时是否强制平仓，忽略拦截配置

    # 牛熊信号配置
    g.isbull = True  # 是否牛市
    g.bull_bear_index = ['000001.SH', 10]  # 上证指数，牛熊判断，均线择时
    g.bull_bear_enable = False  # 启用牛熊信号
    g.bull_bear_threshold = 0.003  # 牛熊切换阈值
    g.bullMaxRatio = 0.9  # 牛市最大仓位
    g.bearMaxRatio = 0.0  # 熊市最大仓位

    """
    从持仓中初始化，仅对实盘已经含有持仓有效，在回测中持仓为空
    """
    sync_portfolio_positions(context)

    # 调仓日进行股票初筛
    # run_time = (datetime.datetime.now() + datetime.timedelta(minutes=1)).strftime('%H:%M')
    # context.run_weekly(func=Trade_Open, weekday=datetime.datetime.now().weekday() + 1, time_str=run_time)
    # context.run_daily(func=Trade_Open, time_str="14:25")
    context.run_weekly(func=Trade_Open, weekday=3, time_str="14:25")
    # 调仓日买入股票
    # run_time = (datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime('%H:%M')
    # context.run_weekly(func=Trade_In, weekday=datetime.datetime.now().weekday() + 1, time_str=run_time)
    # context.run_daily(func=Trade_In, time_str="14:30")
    context.run_weekly(func=Trade_In, weekday=3, time_str="14:26")


def sync_portfolio_positions(context):
    """
    从持仓中初始化，仅对实盘已经含有持仓有效
    """
    # 获取当前的时间点
    dt = context.current_dt.strftime('%Y-%m-%d')
    log.debug(f"持仓字典1: ={g.positions_dict.keys()}")
    # 过滤掉已经被平仓的股票
    g.positions_dict = {k: v for k, v in g.positions_dict.items() if k in context.portfolio.positions.keys()}
    log.debug(f"持仓字典3: ={g.positions_dict.keys()}")
    log.debug(f"持仓字典2: ={context.portfolio.positions.keys()}")
    # g.positions_dict 与系统持仓同步, 获取手工建仓的股票
    for stock, position in context.portfolio.positions.items():
        # volume = position.volume  # 持仓数量
        # can_use_volume = position.can_use_volume  # 可用数量
        init_date = position.init_date  # 开仓日期
        transact_date = position.transact_date  # 最后交易日期
        open_price = position.open_price  # 平均建仓成本

        if stock not in g.positions_dict:
            g.positions_dict[stock] = {"init_date": init_date,  # 减仓时间
                                       "transact_date": transact_date,  # 最后交易时间
                                       "openPositionAtr": 0,  # atr用于跟踪止盈止损，记录开仓时候的atr，记录下来让其固定不变
                                       "longOpenPositionLowPrice": open_price,  # 多头开仓的价格的最低价，记录下来让其固定不变
                                       "exitPriceType": "开",  # 开 、 松、 紧 ，超紧. 现在使用的止损线类型
                                       "startExitPrice": open_price * 0.95,  # 开始止损-退出价格, 默认为建仓成本的95%
                                       "looseExitPrice": open_price * 0.95,  # 宽松止损-退出价格
                                       "tightExitPrice": open_price * 0.95,  # 紧密止损-退出价格
                                       "veryTightExitPrice": open_price * 0.95,  # 超紧止损-退出价格
                                       "realExitPrice": open_price * 0.95,  # 实际止损-退出价格
                                       "exitPriceChangeReason": "价格跌破平均建仓成本价"  # # 止损线改变的原因
                                       }


def get_close_price(context, security, n=1, unit='1d'):
    """
    获取前n个单位时间当时的收盘价
    当unit=1d, 前第n天的收盘价
    当unit=1m, 前第n分钟的收盘价
    :param context:
    :param security: 股票代码
    :param n: 最新的n个单位
    :param unit: 支持1d, 1m
    :return: float, 收盘价
    """
    return context.attribute_history(security=security,
                                     count=n,
                                     unit=unit,
                                     fields=['close'],
                                     dividend_type=context.dividend_type
                                     )['close'][0]


def get_bull_bear_signal(context):
    """
    获取当前市场的牛熊信号
    :param context:
    :return:
    """
    dt = context.current_dt.strftime('%Y-%m-%d')

    df1 = get_factor(sec_code_list=['000300.SH'], unit='1d', start_date=get_previous_trading_date(dt, 10),
                     end_date=get_previous_trading_date(dt), factor_list=['ma_120'],
                     dividend_type='back')
    df1['ma_120_slope'] = ta.LINEARREG_SLOPE(df1['ma_120'], timeperiod=10)
    ma_120_slope = df1['ma_120_slope'].tolist()[-1]

    df = context.get_factor(sec_code_list=['000300.SH'], unit='1d', trade_date=get_previous_trading_date(dt),
                            factor_list=['close', 'ma_120', 'ma_60', 'ma_20'],
                            dividend_type='back')
    df['ma_120_slope'] = ma_120_slope
    df["state"] = df.apply(lambda row: "red" if (row["close"] > row['ma_120'] and row['ma_20'] > row['ma_120'] and row['ma_60'] > row['ma_120'] and row['ma_120_slope'] > 0)
    else ("green" if (row['close'] < row['ma_120'] and
                      row["ma_20"] < row['ma_120'] and
                      row["ma_60"] < row['ma_120'] and
                      row['ma_120_slope'] < 0) else "orange"), axis=1)

    if df['state'].tolist()[0] == 'red':
        g.slop_period = 80
    elif df['state'].tolist()[0] == 'green':
        g.slop_period = 120

    log.info(f"{context.current_dt} 获取牛熊信号: {df['state'].tolist()[0]}")


def get_bar_dict(context, sec_code: str, N1: int = 20, N2: int = 5) -> dict:
    """
    获取截止context.current_dt的bar统计, 当天价格去上一分钟

    :param context:
    :param sec_code:
    :param N1: 最近N1个交易日, 用于获取最高价，即唐奇安通道上轨
    :param N2: 最近N2个交易日，用于获取最低价，即唐奇安通道下轨
    :return: {'trade_date': '2023-08-09', # 当前交易日
              'open': 12.06,              # 开盘价
              'high': 12.2,               # 最高价
              'low': 12.05,               # 最低价
              'close': 12.17,             # 收盘价
              'return': 0.0058,           # 收益率
              'up': 12.53,                # 唐奇安通道上轨
              'down': 11.65,              # 唐奇安通道下轨
              'sma5': 11                  # 5日移动平均
              'sma20': 11                 # 20日移动平均
              'atr': 0.2365               # 真实波动幅度均值
              }
    """
    factor_list = ['open', 'high', 'low', 'close']
    dt = context.current_dt.strftime('%Y-%m-%d')

    # 截止到昨日的数据
    df1 = context.attribute_history(security=sec_code,
                                    count=N1,
                                    unit='1d',
                                    fields=factor_list,
                                    dividend_type=context.dividend_type)  # 获取截止到昨日的数据
    df1.reset_index(inplace=True)

    # 截止到上一分钟的数据, 当天的数据需要按日累计
    df2 = context.attribute_history(security=sec_code,
                                    start_date=dt,
                                    end_date=dt,
                                    unit='1m',
                                    fields=factor_list,
                                    dividend_type=context.dividend_type)  # 获取上1分钟的数据

    if df2.empty:
        df = df1
    else:
        # 使用resample聚合为1天的数据
        daily_df = df2.resample('D').agg({
            'open': 'first',  # 每天的第一个值
            'high': 'max',  # 每天的最大值
            'low': 'min',  # 每天的最小值
            'close': 'last'  # 每天的最后一个值
        })
        daily_df.reset_index(inplace=True)

        daily_df['trade_date'] = daily_df['datetime'].apply(lambda x: datetime.datetime.strftime(x, "%Y-%m-%d"))
        daily_df = daily_df[['trade_date'] + factor_list]
        df = pd.concat([df1, daily_df])

    df['return'] = df.close.pct_change()
    # 最近N1个交易日最高价
    df['up'] = ta.MAX(df.high, timeperiod=N1)

    # 最近N2个交易日最低价
    df['down'] = ta.MIN(df.low, timeperiod=N2)

    df['sma5'] = ta.SMA(df.close, timeperiod=5)
    df['sma20'] = ta.SMA(df.close, timeperiod=20)

    df['atr'] = ta.ATR(df.high, df.low, df.close, timeperiod=14)
    df = df.round(4)
    return df.iloc[-1].to_dict()  # 仅返回最后一个交易日的bar_dict


def before_trading_start(context):
    # 1. 初始化关键模块的执行状态, 双下划线__开头的全局变量不会持久化
    g.__trade_open_success = False
    g.__trade_in_success = False

    log.debug(f"{context.current_dt} before_trading_start(): 每日开盘前")

    """
    从持仓中初始化，仅对实盘已经含有持仓有效，在回测中持仓为空
    """
    sync_portfolio_positions(context)

    dt = context.current_dt.strftime('%Y-%m-%d')
    for stock, pos in context.portfolio.positions.items():
        transact_date = pos.transact_date  # 最后交易日期
        log.debug(f"{dt} before_trading_start(): 每日开盘前 stock={stock}, "
                  f"{g.positions_dict.get(stock, {}).get('exitPriceType', '未知')} "
                  f"init_date={pos.init_date}, "
                  f"transact_date={transact_date}, "
                  f"open_price={pos.open_price}, "
                  f"volume={pos.volume}")


def risk_balanced(df, total_asset: float = ..., risk_point: float = ...):
    """
    风险均衡，合理分配资金
    :param df: sec_code 粒度，必需有atr_14, close
    :param total_asset: 总资产
    :param risk_point: 风险因子，单只股票每日对整个投资组合产生影响的比例，1个基准点相当于0.01%
    :return:
    """
    df['asset_up_down'] = total_asset * risk_point * 0.0001
    df['total_asset'] = total_asset
    df['share_num'] = numpy.floor(df['asset_up_down'] / df['atr_14']) // 100 * 100
    df1 = df[df['share_num'] > 0]
    df2 = df1.copy()
    df2['allocation_asset'] = df2['share_num'] * df2['close']
    df2['weight'] = round(df2['allocation_asset'] / df2['total_asset'], 3)
    df2['cumulate_allocation_asset'] = df2['allocation_asset'].cumsum()
    df_result = df2[df2['total_asset'] >= df2['cumulate_allocation_asset']]
    return df_result


def choose_long_list(context, stock_list):
    # 获取当前的回测时间点
    dt = context.current_dt.strftime('%Y-%m-%d')
    # 指定股票池
    factor_list = ['close', 'low', 'high']
    df_m = context.get_factor(sec_code_list=stock_list, unit='1d',
                              start_date=get_previous_trading_date(dt, g.slop_period),
                              end_date=get_previous_trading_date(dt),
                              factor_list=factor_list,
                              dividend_type='back')
    df_m = df_m.reset_index()

    # 价格序列的自然对数
    df_m['close_log'] = df_m['close'].apply(numpy.log)

    df = context.get_factor(sec_code_list=stock_list, unit='1d',
                            start_date=get_previous_trading_date(dt, g.slop_period),
                            end_date=get_previous_trading_date(dt), factor_list=['low', 'high'],
                            dividend_type='back')
    # 前一个交易日的最高价
    df['pre_high'] = df.groupby(['sec_code'])['high'].shift(1)
    # 过滤价格缺口大于15%的股票
    df_4 = df[((df['low'] - df['pre_high']) / df['pre_high']) > 0.15]
    df_4 = df_4.reset_index()
    # 价格缺口大于15%的股票去重列表
    gap_sec_code = df_4['sec_code'].unique()
    # 获取最新股票价格高于60日移动平均线的股票
    df_2 = context.get_factor(sec_code_list=stock_list, unit='1d', trade_date=get_previous_trading_date(dt),
                              factor_list=['close', 'ma_10', 'atr_14'],
                              dividend_type='back')
    df_3 = df_2[df_2['close'] - df_2['ma_10'] > 0]
    df_3 = df_3.reset_index()
    # 最新股票价格高于60日移动平均线的股票去重后的列表
    above_ma_5_sec_code = df_3['sec_code'].unique()
    # 最新股票价格高于60日移动平均线的股票 排除 价格缺口大于15%的股票
    sec_codes = list(set(above_ma_5_sec_code) - set(gap_sec_code))
    m_sec_code = df_m['sec_code'].unique()

    # 定义一个空列表用于存放斜率计算结果
    slopes = []
    # 按股票计算斜率和判定系数
    for seccode in list(set(sec_codes) & set(m_sec_code)):
        df_grouped = df_m[df_m['sec_code'] == seccode]
        yy = df_grouped['close_log']
        xx = [i for i in range(1, len(df_grouped) + 1)]
        Xxx = numpy.array(xx).reshape(-1, 1)
        regressor = LinearRegression()
        regressor.fit(Xxx, yy)
        # 斜率
        coefficients = regressor.coef_[0]
        # 判定系数
        r2 = regressor.score(Xxx, yy)
        slopes.append([seccode, coefficients, r2])
    # 列表转换成DataFrame格式
    result = pd.DataFrame(slopes, columns=['sec_code', 'slope', 'r2'])
    # 斜率转换成每日收益率
    result['day_income_rate'] = result['slope'].apply(lambda x: numpy.exp(x))
    # 每日收益率转换成年化收益率
    result['year_income_rate'] = result['day_income_rate'].apply(lambda x: numpy.power(x, 245) - 1)
    # 年化收益率 × 判定系数 得到年华收益率的调整值
    result['year_income_adjust'] = result['year_income_rate'] * result['r2']
    # 按照调整后的年化收益率降序排
    result = result.sort_values(by=["year_income_adjust"], ascending=False)
    result_1 = pd.merge(result, df_2, how="left", on=["sec_code"])
    final_result = risk_balanced(result_1, total_asset=1000000, risk_point=30)
    final_result = final_result[['sec_code', 'weight']]
    final_result.set_index(['sec_code'], inplace=True)
    # print(final_result.to_dict(orient='index'))
    return final_result.to_dict(orient='index')


def Trade_Open(context):
    """
    调仓选股

    :param context:
    :return:
    """

    # 更新牛熊信号
    get_bull_bear_signal(context)

    # 获取当前的回测时间点
    dt = context.current_dt.strftime('%Y-%m-%d')
    # 默认以股票池成分股开始
    stock_list = context.run_info.stock_pool_members
    # 获取股票初筛结果，并保存为全局变量
    sec_code_dict = choose_long_list(context, stock_list)

    hold_maxsize = min(context.parameters.get("hold_maxsize", 10), len(sec_code_dict))
    sec_codes_list = []
    weights_list = []
    for a, b in sec_code_dict.items():
        sec_codes_list.append(a)
        weights_list.append(b)
    seccode_weight_pairs = list(zip(sec_codes_list[:hold_maxsize], weights_list[:hold_maxsize]))
    stock_list = dict(seccode_weight_pairs)
    g.chosen_stock_list = stock_list

    log.info(
        f"{context.current_dt} Trade_Open: {context.current_dt} 股票初筛结束({len(g.chosen_stock_list)}): {g.chosen_stock_list.keys()}")
    g.__trade_open_success = True  # Flag: 选股完成


def Trade_In(context):
    """每个调仓日仅能运行一次"""

    # 获取当前的回测时间点
    dt = context.current_dt.strftime('%Y-%m-%d')
    log.info(f"{context.current_dt} Trade_In(): 买入股票")

    if not g.__trade_open_success:
        raise Exception(f"选股失败，取消买入")

    bar_dict = dict()

    # 持仓组合买入
    long_list = g.chosen_stock_list.keys()
    portfolio_cash = context.portfolio.available_cash  # 可用现金
    market_value = context.portfolio.positions_value  # 持仓总市值
    total_value = portfolio_cash + market_value
    available_cash = portfolio_cash
    if not available_cash > 0:
        log.warning(f"已达最大仓位 {round(market_value / total_value, 2)}, 放弃调仓")
        return
    g.trade_idx += 1
    log.warning(f"{context.current_dt} {g.trade_idx}th 调仓, "
                f"调仓计划：{long_list}，可用现金[{available_cash}]")

    # 买入此次调仓的股票：多退少补原则
    rebal_more_stock = dict()  # 加仓字典
    rebal_less_stock = dict()  # 减仓字典 (由退出线卖出股票，不自动减仓，字典应该为空)
    enter_stock = dict()  # 开仓字典
    # w = 1 / (len(long_list) if len(long_list) > 0 else 1)  # 默认调仓列表股票为等权重买入。
    for stock, stock_feature in g.chosen_stock_list.items():
        if stock not in bar_dict:  # 如果bar_dict中没有统计数据，从数据库初始化
            bar_dict[stock] = get_bar_dict(context, sec_code=stock)

        # order = context.order_target_percent(stock_code=stock_code, target=w * 0.95)  # 为减少可用资金不足的情况，留 5% 的现金做备用
        position = context.get_position(stock_code=stock)
        size_pre = position.volume if position else 0  # 获取股票持仓
        # pos_value = position.value if position else 0  # 持仓市值
        open_price = position.open_price if position else 0  # 平均建仓成本
        new_value = stock_feature.get('weight') * available_cash  # 可用现金分配
        # new_value = w * available_cash  # 可用现金分配
        current_price = get_close_price(context, stock, 1, '1m')  # 前1分钟最新价格
        new_size = int(new_value / current_price // 100 * 100)  # 持股数是100的整数倍
        target_size = new_size + size_pre
        if target_size > 0:
            if size_pre > 0:  # 调仓
                if target_size > size_pre:  # 加仓
                    """持仓股票当日最新价格已经跌破退出线，不能加仓"""
                    # 如果无法获取退出价格，默认平均建仓成本
                    real_exit_price = g.positions_dict.get(stock, {}).get('realExitPrice', open_price)
                    log.debug(f"{dt} stock: {stock} close: {current_price}, exit_price: {real_exit_price}")
                    if current_price <= real_exit_price:
                        log.debug(f"{dt} 放弃加仓: {stock}, close[{current_price}] <= realExitPrice[{real_exit_price}]")
                        continue

                    log.debug(f"{dt} 加仓股票: {stock}")
                    rebal_more_stock[stock] = {"from": size_pre, "to": target_size}  # target_size
                elif target_size < size_pre:  # 减仓
                    log.debug(f"{dt} 减仓股票: {stock}")
                    rebal_less_stock[stock] = {"from": size_pre, "to": target_size}  # target_size
            else:  # 开仓
                log.debug(f"{dt} 开仓股票: {stock}")
                enter_stock[stock] = {"from": 0, "to": target_size}  # target_size

            # 开始委托: 确保右侧交易时买入
            if target_size != size_pre:
                context.order_target_volume(stock, target=target_size)

    if rebal_more_stock:
        log.debug(f'{dt} rebal_to_more: {rebal_more_stock}')  # 打印加仓列表
    if rebal_less_stock:
        log.debug(f'{dt} rebal_to_less: {rebal_less_stock}')  # 打印减仓列表
    if enter_stock:
        log.debug(f'{dt} enter_stock: {enter_stock}')  # 打印建仓列表

    # ====================================================
    # 止盈止损: 更新开仓、加仓后的股票退出价格
    # ====================================================

    for stock in enter_stock:  # 开仓
        # 调仓日 初始化止损价格、使用哪条止损线、止损长度、切换这条止损线的原因
        if stock not in bar_dict:  # 如果bar_dict中没有统计数据，从数据库初始化
            bar_dict[stock] = get_bar_dict(context, sec_code=stock)

        # 仓位变更时间
        if stock not in g.positions_dict:
            g.positions_dict[stock] = {"init_date": dt, "transact_date": dt}

        # ---------------------------------------------------------------------
        # 1. 开仓的时候，初始化每条止损线的退出价格
        # ---------------------------------------------------------------------
        # 开仓，固定该变量为前一分钟的atr
        g.positions_dict[stock]['openPositionAtr'] = bar_dict[stock]['atr']
        # 开仓，固定该变量为昨天的最低价
        g.positions_dict[stock]['longOpenPositionLowPrice'] = bar_dict[stock]['close']
        # 初始化开始止损价：最低价-开始止损线atr倍数*atr
        g.positions_dict[stock]['startExitPrice'] = bar_dict[stock]['low'] \
                                                    - g.startStopAtrMulti * bar_dict[stock]['atr']
        # 初始化宽松止损价：最低价-宽松止损线atr倍数*atr
        g.positions_dict[stock]['looseExitPrice'] = bar_dict[stock]['low'] \
                                                    - g.looseStopAtrMulti * bar_dict[stock]['atr']

        # ---------------------------------------------------------------------
        # 2.开仓的时候，初始化选择哪条止损线
        # ---------------------------------------------------------------------
        if g.isStartStopOn:  # 如果启用开始止损线
            g.positions_dict[stock]['exitPriceType'] = "开"
        elif g.isLooseStopOn:  # 如果启用宽松止损线
            g.positions_dict[stock]['exitPriceType'] = "松"

        # ---------------------------------------------------------------------
        # 3.开仓的时候止损线变更原因默认
        # ---------------------------------------------------------------------
        g.positions_dict[stock]['exitPriceChangeReason'] = "开仓默认"

    for stock in rebal_more_stock:  # 加仓
        # 调仓日 对加仓股票更新止损价格、使用哪条止损线、止损长度、切换这条止损线的原因
        if stock not in bar_dict:  # 如果bar_dict中没有统计数据，从数据库初始化
            bar_dict[stock] = get_bar_dict(context, sec_code=stock)

        # 仓位变更时间
        g.positions_dict[stock]['transact_date'] = dt

        size_pre = rebal_more_stock[stock]["from"]
        target_size = rebal_more_stock[stock]["to"]
        size_extra = target_size - size_pre
        # 1. 加仓的时候，更新每条止损线的退出价格
        g.positions_dict[stock]['openPositionAtr'] = (size_pre / target_size) * g.positions_dict[stock][
            'openPositionAtr'] + (size_extra / target_size) * bar_dict[stock]['atr']
        g.positions_dict[stock]['longOpenPositionLowPrice'] = (size_pre / target_size) * g.positions_dict[stock][
            'longOpenPositionLowPrice'] \
                                                              + (size_extra / target_size) * bar_dict[stock]['close']
        g.positions_dict[stock]['startExitPrice'] = g.positions_dict[stock][
                                                        'longOpenPositionLowPrice'] - g.startStopAtrMulti * \
                                                    g.positions_dict[stock]['openPositionAtr']
        g.positions_dict[stock]['looseExitPrice'] = g.positions_dict[stock][
                                                        'longOpenPositionLowPrice'] - g.looseStopAtrMulti * \
                                                    g.positions_dict[stock]['openPositionAtr']

    g.__trade_in_success = True  # 买入股票完成
    log.info(f"{context.current_dt}: Trade_In(): 本次调仓完成!")


# 平仓，卖出指定持仓
def close_position(context, stock, force: bool = False):
    log.info(f"{context.current_dt} 平仓股票: {stock}")
    order = context.order_target_value(stock, 0, force=force)  # 可能会因停牌或跌停失败

    if order is None:
        log.warning("委托条件未满足，放弃平仓")
        return


def handle_bar(context):
    """根据策略执行的主图BAR运行周期，可能为1d, 1m, 5m, 建设实盘中设置为最少5分钟(5m), 方便及时止盈止损"""

    # 获取当前的回测时间点
    dt = context.current_dt.strftime('%Y-%m-%d')

    # 指定日期增加出入金测试
    if dt == "2024-01-11":
        # 入金50万
        context.inout_cash(500000)
    elif dt == "2024-03-11":
        # 出金10万
        context.inout_cash(-100000)

    bar_dict = dict()
    # 同步g.positions_dict 和 context.portfolio.positions
    sync_portfolio_positions(context)

    # 非调仓日 持仓：止损价格变化逻辑、切换止损线逻辑、触发止损止盈逻辑
    for stock in list(g.positions_dict.keys()):
        if stock not in bar_dict:  # 如果bar_dict中没有统计数据，从数据库初始化
            bar_dict[stock] = get_bar_dict(context, sec_code=stock)
        open_price = g.positions_dict[stock]['longOpenPositionLowPrice']
        current_obt = (bar_dict[stock]['close'] - open_price) / open_price
        if current_obt < -0.03 or current_obt > 0.06:
            log.debug(f"{dt} {stock} 收益达到平仓标准={current_obt}")
            close_position(context, stock, force=g.force_close)
