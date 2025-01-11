import atexit

import redis

from gsuid_core.logger import logger


class WavesRedisClient:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(WavesRedisClient, cls).__new__(cls, *args, **kwargs)
            from ...wutheringwaves_config import WutheringWavesConfig
            REDIS_FROM_URL = WutheringWavesConfig.get_config('RedisFromUrl').data
            try:
                # 创建 Redis 客户端
                cls._instance._redis_client = redis.StrictRedis.from_url(
                    REDIS_FROM_URL,
                    decode_responses=True,
                )
                logger.info(" [鸣潮][Redis连接成功]")
            except Exception as e:
                logger.exception(f" [鸣潮][Redis连接错误]: {e}")
                cls._instance._redis_client = None
        return cls._instance

    @property
    def get_client(self) -> redis.StrictRedis:
        """返回 Redis 客户端实例"""
        return self._redis_client

    def close(self):
        """关闭 Redis 客户端"""
        if self._redis_client:
            self._redis_client.connection_pool.disconnect()
            logger.info("[鸣潮][Redis清理] connection pool cleared.")
            self._redis_client = None
            logger.info("[鸣潮][Redis清理] client connection closed.")


# 实例化 WavesRedisClient
wavesRedis = WavesRedisClient()


# 清理函数
def cleanup():
    logger.info("正在执行清理操作...")
    wavesRedis.close()


# 注册退出时的清理操作
atexit.register(cleanup)
