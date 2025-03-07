import random
import string
import time
from functools import wraps

import httpx


def timed_async_cache(expiration, condition=lambda x: True):
    def decorator(func):
        cache = {}

        @wraps(func)
        async def wrapper(*args):
            current_time = time.time()
            # 如果是类方法，args[0]是实例，我们获取类名
            if args and hasattr(args[0], "__class__"):
                cache_key = f"{args[0].__class__.__name__}.{func.__name__}"
            else:
                cache_key = func.__name__

            if cache_key in cache:
                value, timestamp = cache[cache_key]
                if current_time - timestamp < expiration:
                    return value

            value = await func(*args)
            if condition(value):
                cache[cache_key] = (value, current_time)
            return value

        return wrapper

    return decorator


# 使用示例
@timed_async_cache(86400)
async def get_public_ip(host="127.0.0.1"):
    # 尝试从 ipify 获取 IP 地址
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get("https://api.ipify.org/?format=json", timeout=4)
            ip = r.json()["ip"]
            return ip
    except:  # noqa:E722, B001
        pass

    # 尝试从 httpbin.org 获取 IP 地址
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get("https://httpbin.org/ip", timeout=4)
            ip = r.json()["origin"]
            return ip
    except Exception:
        pass

    return host


def generate_random_string(length=32):
    # 定义可能的字符集合
    characters = string.ascii_letters + string.digits + string.punctuation
    # 使用random.choice随机选择字符，并连接成字符串
    random_string = "".join(random.choice(characters) for i in range(length))
    return random_string


def hide_uid(uid: str) -> str:
    from ..wutheringwaves_config import WutheringWavesConfig

    HideUid = WutheringWavesConfig.get_config("HideUid").data
    if not HideUid:
        return uid
    if len(uid) < 2:
        return uid
    return uid[:2] + "*" * 4 + uid[-2:]
