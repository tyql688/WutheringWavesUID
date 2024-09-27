import time
from functools import wraps

import httpx


def timed_async_cache(expiration):
    def decorator(func):
        cache = {}

        @wraps(func)
        async def wrapper(*args):
            current_time = time.time()
            if args in cache:
                value, timestamp = cache[args]
                if current_time - timestamp < expiration:
                    return value

            value = await func(*args)
            cache[args] = (value, current_time)
            return value

        return wrapper

    return decorator


# 使用示例
@timed_async_cache(86400)
async def get_public_ip(host='127.0.0.1'):
    # 尝试从 ipify 获取 IP 地址
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get('https://api.ipify.org/?format=json', timeout=4)
            ip = r.json()['ip']
            return ip
    except:  # noqa:E722, B001
        pass

    # 尝试从 httpbin.org 获取 IP 地址
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get('https://httpbin.org/ip', timeout=4)
            ip = r.json()['origin']
            return ip
    except:
        pass

    return host
