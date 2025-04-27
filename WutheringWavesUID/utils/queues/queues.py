import asyncio
import threading
from typing import Any, Callable, Coroutine, Dict, Union

from gsuid_core.logger import logger


class TaskDispatcher:

    def __init__(self):
        self.queue = asyncio.Queue()
        self.running = False
        self.handlers: Dict[str, Callable] = {}

    def register_handler(
        self,
        task_type: str,
        handler: Callable[[Any], Union[Any, Coroutine[Any, Any, Any]]],
    ) -> None:
        self.handlers[task_type] = handler
        logger.info(f"注册任务处理器: {task_type}")

    async def dispatch(self, task_type: str, data: Any) -> None:
        if not self.running:
            logger.warning("任务分发器未启动或已关闭")
            return
        if task_type not in self.handlers:
            return

        await self.queue.put((task_type, data))

    async def _process(self) -> None:
        while True:
            try:
                # 如果分发器已关闭，退出循环
                if not self.running:
                    break

                # 获取队列任务
                task_type, data = await asyncio.wait_for(self.queue.get(), timeout=3.0)

                # 处理任务
                handler = self.handlers.get(task_type)
                if handler:
                    # 创建异步任务
                    asyncio.create_task(self._run_task(handler, data, task_type))

                # 标记任务完成
                self.queue.task_done()

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.exception(f"任务处理异常: {e}")

    async def _run_task(self, handler: Callable, data: Any, task_type: str) -> None:
        try:
            result = handler(data)
            # 如果是协程，等待它完成
            if asyncio.iscoroutine(result):
                await result
        except Exception as e:
            logger.exception(f"任务执行错误 ({task_type}): {e}")

    def start(self, daemon: bool = True) -> None:
        if self.running:
            return

        self.running = True

        # 启动处理线程
        threading.Thread(
            target=lambda: asyncio.run(self._process()), daemon=daemon
        ).start()


# 创建全局任务分发器实例
dispatcher = TaskDispatcher()


# 工具函数
def register_handler(
    task_type: str,
    handler: Callable[[Any], Union[Any, Coroutine[Any, Any, Any]]],
) -> None:
    dispatcher.register_handler(task_type, handler)


def start_dispatcher(daemon: bool = True) -> None:
    dispatcher.start(daemon=daemon)


# 兼容原有代码的函数
async def put_item(queue_name: str, item: Any) -> None:
    await dispatcher.dispatch(queue_name, item)
