from datetime import datetime, timedelta


def now():
    """
    获取当前时间
    :return:
    """
    return datetime.now()


def time_diff_second(start_time, end_time):
    """
    计算两个时间相差的秒数
    :param start_time:
    :param end_time:
    :return:
    """
    return (end_time - start_time).total_seconds()


def time_diff_minute(start_time, end_time):
    """
    计算两个时间相差的分钟数

    如果要计算大于多少时间，可以这样计算

    构建两个时间

    datetime1 = datetime(2023, 8, 2, 0, 0, 3, 0)
    datetime2 = datetime(2023, 8, 1, 0, 0, 0, 0)

    计算两个时间相差的时间

    diff_time = datetime1 - datetime2
    if diff_time > timedelta(minutes=10):
        print("时间差大于10分钟")

    :param start_time:
    :param end_time:
    :return:
    """
    return time_diff_second(start_time, end_time) / 60


def format_time(time, format="%Y-%m-%d %H:%M:%S"):
    """
    格式化时间
    :param time:
    :param format: 格式化字符串
    :return:
    """
    return time.strftime(format)


# 解析时间
def parse_time(time_str, format="%Y-%m-%d %H:%M:%S"):
    """
    解析时间
    :param time_str:
    :param format: 格式化字符串
    :return:
    """
    return datetime.strptime(time_str, format)
