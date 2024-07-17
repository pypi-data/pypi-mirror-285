"""
日期时间工具
"""
from datetime import datetime
import time
from dateutil import parser, rrule

one_minute_seconds = 60
one_hour_seconds = 60 * one_minute_seconds
one_day_seconds = one_hour_seconds * 24
one_week_seconds = one_day_seconds * 7


def get_today(time_formate: str = '%Y%m%d'):
    """获取当日的日期字符串"""
    return datetime.today().strftime(time_formate)


def get_now(time_formate: str = '%Y-%m-%d %H:%M:%S') -> str:
    """获取当前时间符串"""
    return datetime.now().strftime(time_formate)


def get_timestamp() -> int:
    """获取时间戳"""
    return int(time.time())


def get_time_str(time_formate: str = '%Y%m%d%H%M%S%f') -> str:
    """获取时间字符串"""
    return datetime.now().strftime(time_formate)


def parse_str(datetime_str: str) -> datetime:
    """格式化日期字符串"""
    return parser.parse(datetime_str)


def calc_space_seconds(start_time: datetime, end_time: datetime) -> int:
    """计算两个时间间隔的秒数"""
    return rrule.rrule(rrule.SECONDLY, dtstart=start_time, until=end_time).count()


def get_now_info():
    """获取现在的信息"""
    now_time = datetime.now()
    year = ('000' + str(now_time.year))[-4:]
    month = ('0' + str(now_time.month))[-2:]
    day = ('0' + str(now_time.day))[-2:]
    hour = ('0' + str(now_time.hour))[-2:]
    minute = ('0' + str(now_time.minute))[-2:]
    second = ('0' + str(now_time.second))[-2:]
    return year, month, day, hour, minute, second


def format_date_time(date_time_value: datetime, time_formate: str = '%Y-%m-%d %H:%M:%S'):
    """格式化日期"""
    if date_time_value:
        return date_time_value.strftime(time_formate)


def format_update_time(update_time: datetime, add_time: datetime = None, time_formate: str = '%Y-%m-%d'):
    """格式化更新日期"""
    if update_time:
        return update_time.strftime(time_formate)
    if add_time:
        return add_time.strftime(time_formate)


if __name__ == '__main__':
    print(get_today())
