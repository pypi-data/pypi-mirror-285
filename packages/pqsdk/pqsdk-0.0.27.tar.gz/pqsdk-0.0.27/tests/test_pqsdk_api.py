from pqsdk.api import *
import datetime

res = get_plate_data(end_time='09:30')
print(res)


df = get_last_ticks(['603320.SH', '601138.SH', '600233.SH'], index=True, fields=['last_price'])
print(df)


ret = get_trade_cal(start_date='2018-01-01')
print(ret)

ret = get_previous_trading_date('2024-04-08')
print(ret)

ret = get_open_trade_dates('2024-01-08')
print(ret)

df = get_attribute_history(security='000300.SH',
                           fields=['close', 'pre_close'],
                           unit='1d',
                           start_date='2024-05-22',
                           end_date='2024-05-22',
                           dividend_type='back')
print(df)

# exit()

df = get_factor(sec_code_list=['000001.SZ'], end_date='2023-03-29', unit='1m', count=150, dividend_type='front')
print(df)

# 获取因子数据
# factor_list = ['float_share', 'pe', 'pe_ttm', 'ma_5', 'ema_5', 'dv_ratio']
factor_list = ['open', 'high', 'low', 'close', 'volume', 'amount']
# 获取unit='1d'的数据
df = get_factor(stock_pool=['000300.SH'], trade_date='2023-03-29', factor_list=factor_list)
print(df)
# 获取unit='1m'的数据
df = get_factor(sec_code_list=['000001.SZ'], end_date='2023-03-29', factor_list=factor_list, count=5, unit='1m',
                dividend_type='front')
print(df)

# 获取历史数据，可查询多个标的单个数据字段
current_dt = datetime.datetime.strptime('2023-03-29 14:58:00', '%Y-%m-%d %H:%M:%S')
# current_dt = datetime.datetime.now()
print(current_dt)
stock_list = ['601236.SH', '000002.SZ']
# # 截止昨日同一分钟
end_datetime = (current_dt + datetime.timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
df = get_history(1, unit='1m', end_datetime=end_datetime, field='close', security_list=stock_list,
                 dividend_type='front')
print(df)

# 截止昨日
end_date = (current_dt + datetime.timedelta(days=-1)).strftime('%Y-%m-%d')
df = get_history(5, unit='1d', end_date=end_date, field='close', security_list=stock_list)
print(df)

# 获取历史数据，可查询单个标的多个数据字段
sec_code = '000001.SZ'
end_datetime = (current_dt + datetime.timedelta(minutes=-1)).strftime('%Y-%m-%d %H:%M:%S')
df = get_attribute_history(security=sec_code, count=5, unit='1m', end_datetime=end_datetime, fields=['open', 'close'])
print(df)

# 沪深300分钟行情数据
factor_list = ['open', 'high', 'low', 'close', 'volume']
df = get_factor(sec_code_list=['000300.SH'], unit='1m', trade_date='2022-12-19', factor_list=factor_list)
print(df)

stock_members = get_index_members_lst(['000300.SH'])
print(stock_members)
