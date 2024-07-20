import datetime


def is_valid_time(start_time, t, interval: int, unit: str = 'm'):
    """
    判断给定时间t是否大于或等于开始时间start_time，并且t是以n个unit做为间隔的

    :param start_time: 检查的起始时间，datetime.datetime类型
    :param t: 被检查的时间，datetime.datetime类型
    :param interval: 单位间隔
    :param unit: 单位
    :return: bool
    """

    if unit not in ['m', 's']:
        raise Exception("unit is wrong, must be 'm' for minutes, or 's' for second.")
    # 确保t不小于start_time
    if t < start_time:
        return False

        # 计算t和start_time之间的时间差
    time_diff = t - start_time

    # 将时间差转换为分钟，并检查是否为n分钟的整数倍
    if unit == 'm':
        minutes_diff = time_diff.total_seconds() // 60  # 转换为分钟
    else:
        minutes_diff = time_diff.total_seconds()
    return minutes_diff % interval == 0


# 示例使用
start_time = datetime.datetime(2023, 4, 1, 0, 0, 0)  # 2023年4月1日00:00
t = datetime.datetime(2023, 4, 1, 0, 30, 0)  # 2023年4月1日00:30
interval = 30  # 30分钟间隔

print(is_valid_time(start_time, t, interval))  # 应该输出True，因为t是start_time后30分钟

t_invalid = datetime.datetime(2023, 4, 1, 0, 45, 0)  # 2023年4月1日00:45
print(is_valid_time(start_time, t_invalid, interval))  # 应该输出False，因为t_invalid不是start_time后n分钟的整数倍


t_invalid = datetime.datetime(2023, 4, 1, 0, 45, 3)
interval = 2  # 30分钟间隔
print(is_valid_time(start_time, t_invalid, interval, 's'))