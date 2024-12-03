# 异步缓存

import asyncio
from typing import Dict, Generic, Optional, TypeVar

T = TypeVar("T")  # 定义一个类型变量


class AsyncCache(Generic[T]):
    def __init__(self):
        """
        初始化异步缓存。
        """
        self.cache: Dict[str, T] = {}
        self.lock = asyncio.Lock()

    async def set(self, uid: str, value: T):
        """
        设置单个缓存值。

        :param uid: 缓存键。
        :param value: 任意类型的缓存值。
        """
        async with self.lock:
            self.cache[uid] = value

    async def get(self, uid: str) -> Optional[T]:
        """
        获取缓存值。

        :param uid: 缓存键。
        :return: 缓存值（如果存在），否则返回 None。
        """
        async with self.lock:
            return self.cache.get(uid, None)

    async def delete(self, uid: str):
        """
        删除缓存值。

        :param uid: 缓存键。
        """
        async with self.lock:
            if uid in self.cache:
                del self.cache[uid]

    async def size(self) -> int:
        """
        获取当前缓存的大小。

        :return: 缓存的键数量。
        """
        async with self.lock:
            return len(self.cache)

    async def set_all(self, data: Dict[str, T]):
        """
        批量设置缓存值。

        :param data: 一个包含多个 UID -> 缓存值 的字典。
        """
        async with self.lock:
            self.cache.update(data)

    async def get_all(self) -> Dict[str, T]:
        """
        获取所有缓存内容。

        :return: 当前缓存的所有键值对。
        """
        async with self.lock:
            return self.cache.copy()


card_cache = AsyncCache[Dict]()
user_bind_cache = AsyncCache()
