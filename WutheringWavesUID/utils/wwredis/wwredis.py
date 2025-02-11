import asyncio
from contextlib import asynccontextmanager
from typing import Dict

from redis.asyncio import RedisCluster, Redis

from gsuid_core.logger import logger


class WavesRedisClient:
    _instances: Dict[int, Redis | RedisCluster] = {}

    def __init__(self):
        self._redis_client = None
        self._is_cluster = False

    @asynccontextmanager
    async def get_client(self) -> Redis | RedisCluster:
        """
        获取 Redis 客户端的上下文管理器
        使用方式:
        async with wavesRedis.get_client() as client:
            await client.get("key")
        """
        current_loop = None
        try:
            current_loop = id(asyncio.get_running_loop())
            if current_loop not in self._instances:
                await self._initialize_redis_connection(current_loop)
            client = self._instances[current_loop]
            yield client
        except RuntimeError:
            raise RuntimeError(
                "No running event loop - Redis client must be accessed within an async context"
            )
        finally:
            logger.debug(f" [鸣潮][Redis连接关闭] - Loop ID: {current_loop}")

    async def _initialize_redis_connection(self, loop_id: int):
        """初始化 Redis 连接"""
        from ...wutheringwaves_config import WutheringWavesConfig

        REDIS_FROM_URL = WutheringWavesConfig.get_config("RedisFromUrl").data
        is_cluster = WutheringWavesConfig.get_config("IsRedisCluster").data

        try:
            if is_cluster:
                client = RedisCluster.from_url(REDIS_FROM_URL, decode_responses=True)
                self._is_cluster = True
                logger.info(f" [鸣潮][Redis连接成功] (Cluster) - Loop ID: {loop_id}")
            else:
                client = Redis.from_url(REDIS_FROM_URL, decode_responses=True)
                logger.info(f" [鸣潮][Redis连接成功] (Node) - Loop ID: {loop_id}")

            self._instances[loop_id] = client
        except Exception as e:
            logger.exception(f" [鸣潮][Redis连接错误] - Loop ID: {loop_id}: {e}")
            raise

    @property
    def is_cluster(self) -> bool:
        """返回是否连接到 Redis Cluster"""
        return self._is_cluster


# 全局单例
wavesRedis = WavesRedisClient()
