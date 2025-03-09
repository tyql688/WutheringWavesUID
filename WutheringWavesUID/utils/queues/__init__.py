from typing import Any

import httpx

from gsuid_core.logger import logger

from ..api.wwapi import UPLOAD_URL
from .const import QUEUE_SCORE_RANK
from .queues import start_queue_processor_thread


async def send_score_rank(item: Any):
    if not item:
        return
    if not isinstance(item, dict):
        return
    from ...wutheringwaves_config import WutheringWavesConfig

    WavesToken = WutheringWavesConfig.get_config("WavesToken").data

    if not WavesToken:
        return

    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(
                UPLOAD_URL,
                json=item,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {WavesToken}",
                },
                timeout=httpx.Timeout(10),
            )
            logger.info(f"上传面板结果: {res.status_code} - {res.text}")
        except Exception as e:
            logger.exception(f"上传面板失败: {res.text} {e}")


def init_queues():
    start_queue_processor_thread(QUEUE_SCORE_RANK, send_score_rank)
