import asyncio
import threading
from typing import (
    Any,
    Callable,
    Coroutine,
    Dict,
    Generic,
    List,
    Optional,
    TypeVar,
    Union,
)

from gsuid_core.logger import logger


class QueueThread:
    def __init__(self, target: Callable, daemon: bool = True):
        self.target = target
        self.daemon = daemon

    def start(self):
        threading.Thread(
            target=lambda: asyncio.run(self.target()),
            daemon=self.daemon,
        ).start()


T = TypeVar("T")


class AsyncQueue(Generic[T]):
    def __init__(self, maxsize: int = 0):
        self._queue: asyncio.Queue[T] = asyncio.Queue(maxsize=maxsize)
        self._closed: bool = False
        self._pending_tasks: List[asyncio.Task] = []

    async def put(self, item: T) -> None:
        if self._closed:
            raise RuntimeError("Cannot put items into a closed queue")
        await self._queue.put(item)

    def put_nowait(self, item: T) -> None:
        if self._closed:
            raise RuntimeError("Cannot put items into a closed queue")
        self._queue.put_nowait(item)

    async def get(self) -> T:
        if self._closed and self._queue.empty():
            return None  # type: ignore
        return await self._queue.get()

    async def close(self) -> None:
        self._closed = True

        # Wait for all pending tasks to complete
        if self._pending_tasks:
            await asyncio.gather(*self._pending_tasks, return_exceptions=True)
            self._pending_tasks.clear()

    def task_done(self) -> None:
        self._queue.task_done()

    async def join(self) -> None:
        await self._queue.join()

    @property
    def closed(self) -> bool:
        return self._closed

    @property
    def empty(self) -> bool:
        return self._queue.empty()

    @property
    def full(self) -> bool:
        return self._queue.full()

    def qsize(self) -> int:
        return self._queue.qsize()

    async def process_queue(self, processor: Callable[[T], Any]) -> None:
        while not (self._closed and self._queue.empty()):
            try:
                item = await self.get()
                if item is None:  # Queue is closed and empty
                    break

                try:
                    await processor(item)
                finally:
                    self.task_done()
            except Exception as e:
                # Log the exception or handle it as needed
                logger.exception(f"Error processing queue item: {e}")

    def create_processor_task(self, processor: Callable[[T], Any]) -> asyncio.Task:
        task = asyncio.create_task(self.process_queue(processor))
        self._pending_tasks.append(task)
        return task


# 全局队列注册表，用于在不同模块间共享队列
_queue_registry: Dict[str, AsyncQueue] = {}


def get_queue(name: str, maxsize: int = 0) -> Optional[AsyncQueue]:
    if name in _queue_registry:
        return _queue_registry[name]
    return None


async def put_item(queue_name: str, item: Any) -> None:
    queue = get_queue(queue_name)
    if not queue:
        return
    await queue.put(item)


def put_item_nowait(queue_name: str, item: Any) -> None:
    queue = get_queue(queue_name)
    if not queue:
        return
    queue.put_nowait(item)


async def close_queue(queue_name: str) -> None:
    if queue_name in _queue_registry:
        await _queue_registry[queue_name].close()


def create_queue_processor(
    queue_name: str, processor: Callable[[Any], Union[Any, Coroutine[Any, Any, Any]]]
) -> Optional[asyncio.Task]:
    queue = AsyncQueue(maxsize=0)
    _queue_registry[queue_name] = queue

    async def _processor_wrapper(item: Any) -> None:
        result = processor(item)
        if asyncio.iscoroutine(result):
            await result

    return queue.create_processor_task(_processor_wrapper)


def start_queue_processor_thread(
    queue_name: str,
    processor: Callable[[Any], Union[Any, Coroutine[Any, Any, Any]]],
    daemon: bool = True,
) -> None:
    async def _process_queue() -> None:
        create_queue_processor(queue_name, processor)
        # 保持线程运行，直到队列关闭
        queue = get_queue(queue_name)
        if not queue:
            return
        while not queue.closed:
            await asyncio.sleep(1)

    logger.info(f"启动队列处理器线程: {queue_name}")
    QueueThread(target=_process_queue, daemon=daemon).start()
