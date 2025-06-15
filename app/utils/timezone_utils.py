"""
时区工具函数
统一处理时间转换为北京时间
"""

from datetime import datetime, timezone, timedelta
import pytz

# 北京时区
BEIJING_TZ = pytz.timezone('Asia/Shanghai')
UTC_TZ = pytz.UTC


def utc_now() -> datetime:
    """获取当前UTC时间"""
    return datetime.now(UTC_TZ)


def beijing_now() -> datetime:
    """获取当前北京时间"""
    return datetime.now(BEIJING_TZ)


def utc_to_beijing(utc_dt: datetime) -> datetime:
    """将UTC时间转换为北京时间"""
    if utc_dt.tzinfo is None:
        utc_dt = UTC_TZ.localize(utc_dt)
    elif utc_dt.tzinfo != UTC_TZ:
        utc_dt = utc_dt.astimezone(UTC_TZ)
    
    return utc_dt.astimezone(BEIJING_TZ)


def beijing_to_utc(beijing_dt: datetime) -> datetime:
    """将北京时间转换为UTC时间"""
    if beijing_dt.tzinfo is None:
        beijing_dt = BEIJING_TZ.localize(beijing_dt)
    elif beijing_dt.tzinfo != BEIJING_TZ:
        beijing_dt = beijing_dt.astimezone(BEIJING_TZ)
    
    return beijing_dt.astimezone(UTC_TZ)


def format_beijing_time(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """格式化为北京时间字符串"""
    if dt.tzinfo is None:
        # 假设是UTC时间
        dt = UTC_TZ.localize(dt)
    
    beijing_dt = dt.astimezone(BEIJING_TZ)
    return beijing_dt.strftime(format_str)


def parse_beijing_time(time_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """解析北京时间字符串为datetime对象"""
    naive_dt = datetime.strptime(time_str, format_str)
    return BEIJING_TZ.localize(naive_dt) 