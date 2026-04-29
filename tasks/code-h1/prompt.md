You are given a Python asyncio worker pool with a race condition. The pool uses a shared mutable dictionary and a misused `asyncio.Semaphore` that allows concurrent mutation of the shared state.

Your task:
1. **Identify** the exact race condition (explain what goes wrong and under what interleaving).
2. **Fix** the code so it is correct under concurrent execution.
3. Return the complete fixed code.

```python
import asyncio
import random
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, Awaitable

@dataclass
class WorkItem:
    id: int
    payload: Any
    priority: int = 0
    created_at: float = field(default_factory=time.time)
    result: Optional[Any] = None
    error: Optional[str] = None
    status: str = "pending"

class WorkerPoolStats:
    def __init__(self):
        self.completed = 0
        self.failed = 0
        self.total_time = 0.0
        self.active_workers = 0
        self.peak_workers = 0

    def record_completion(self, duration: float):
        self.completed += 1
        self.total_time += duration

    def record_failure(self):
        self.failed += 1

    @property
    def avg_time(self) -> float:
        return self.total_time / self.completed if self.completed else 0

class AsyncWorkerPool:
    """Async worker pool with priority queue, retry logic, and stats tracking."""

    def __init__(self, max_workers: int = 10, max_retries: int = 3):
        self.max_workers = max_workers
        self.max_retries = max_retries
        self.semaphore = asyncio.Semaphore(max_workers)
        self.work_items: Dict[int, WorkItem] = {}
        self.results: Dict[int, Any] = {}
        self.stats = WorkerPoolStats()
        self._handlers: Dict[str, Callable] = {}
        self._running = False
        self._task_counter = 0
        self._pending_queue: List[WorkItem] = []
        self._worker_assignments: Dict[int, int] = {}  # worker_id -> work_item_id

    def register_handler(self, name: str, handler: Callable[[Any], Awaitable[Any]]):
        self._handlers[name] = handler

    async def submit(self, payload: Any, priority: int = 0, handler: str = "default") -> int:
        self._task_counter += 1
        item = WorkItem(id=self._task_counter, payload=payload, priority=priority)
        self.work_items[item.id] = item
        self._pending_queue.append(item)
        self._pending_queue.sort(key=lambda x: -x.priority)
        return item.id

    async def _process_item(self, item: WorkItem, handler_name: str = "default"):
        handler = self._handlers.get(handler_name)
        if not handler:
            item.error = f"No handler '{handler_name}'"
            item.status = "failed"
            self.stats.record_failure()
            return

        retries = 0
        while retries <= self.max_retries:
            try:
                # BUG: Semaphore acquired here but shared state mutated without protection
                async with self.semaphore:
                    self.stats.active_workers += 1
                    if self.stats.active_workers > self.stats.peak_workers:
                        self.stats.peak_workers = self.stats.active_workers

                    worker_id = id(asyncio.current_task())
                    self._worker_assignments[worker_id] = item.id

                    item.status = "running"
                    start = time.time()

                    result = await handler(item.payload)

                    duration = time.time() - start
                    item.result = result
                    item.status = "completed"

                    # BUG: Race condition — multiple coroutines read-modify-write self.results
                    # and self.stats without synchronization
                    current_results = self.results
                    await asyncio.sleep(0)  # yield point that enables interleaving
                    current_results[item.id] = result

                    self.stats.record_completion(duration)

                    # BUG: worker_assignments cleanup races with new assignments
                    del self._worker_assignments[worker_id]
                    self.stats.active_workers -= 1
                    return

            except Exception as e:
                retries += 1
                self.stats.active_workers -= 1
                if retries > self.max_retries:
                    item.error = str(e)
                    item.status = "failed"
                    self.stats.record_failure()
                    return
                # Exponential backoff
                await asyncio.sleep(0.001 * (2 ** retries))
                item.status = "retrying"

    async def run_all(self, handler_name: str = "default") -> Dict[int, Any]:
        self._running = True
        tasks = []

        while self._pending_queue:
            item = self._pending_queue.pop(0)
            task = asyncio.create_task(self._process_item(item, handler_name))
            tasks.append(task)

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        self._running = False
        return dict(self.results)

    async def get_result(self, item_id: int) -> Optional[Any]:
        return self.results.get(item_id)

    async def get_stats(self) -> dict:
        return {
            "completed": self.stats.completed,
            "failed": self.stats.failed,
            "avg_time": self.stats.avg_time,
            "peak_workers": self.stats.peak_workers,
            "active_workers": self.stats.active_workers,
        }

    async def cancel_pending(self):
        cancelled = len(self._pending_queue)
        for item in self._pending_queue:
            item.status = "cancelled"
        self._pending_queue.clear()
        return cancelled

    async def drain(self, timeout: float = 30.0):
        start = time.time()
        while self.stats.active_workers > 0:
            if time.time() - start > timeout:
                raise TimeoutError(f"Pool drain timeout after {timeout}s")
            await asyncio.sleep(0.01)

    def get_work_item(self, item_id: int) -> Optional[WorkItem]:
        return self.work_items.get(item_id)

    @property
    def pending_count(self) -> int:
        return len(self._pending_queue)

    @property
    def active_count(self) -> int:
        return self.stats.active_workers

    async def resize(self, new_max: int):
        old_max = self.max_workers
        self.max_workers = new_max
        # BUG: Replacing the semaphore while workers may be holding it
        self.semaphore = asyncio.Semaphore(new_max)

    async def batch_submit(self, payloads: List[Any], handler: str = "default") -> List[int]:
        ids = []
        for payload in payloads:
            item_id = await self.submit(payload, handler=handler)
            ids.append(item_id)
        return ids

    async def run_with_callback(self, handler_name: str, callback: Callable):
        results = await self.run_all(handler_name)
        for item_id, result in results.items():
            await callback(item_id, result)
        return results


# Utility: create a pool for batch processing
async def create_batch_processor(
    items: List[Any],
    processor: Callable[[Any], Awaitable[Any]],
    max_concurrent: int = 5,
    max_retries: int = 2,
) -> Dict[int, Any]:
    pool = AsyncWorkerPool(max_workers=max_concurrent, max_retries=max_retries)
    pool.register_handler("batch", processor)

    for item in items:
        await pool.submit(item, handler="batch")

    return await pool.run_all("batch")


# Utility: rate-limited pool
class RateLimitedPool(AsyncWorkerPool):
    def __init__(self, max_workers: int = 5, rate_limit: float = 10.0, **kwargs):
        super().__init__(max_workers=max_workers, **kwargs)
        self.rate_limit = rate_limit
        self._last_dispatch = 0.0
        self._rate_lock = None  # BUG: Lock never initialized

    async def _process_item(self, item: WorkItem, handler_name: str = "default"):
        # BUG: Rate limiting without proper lock
        now = time.time()
        min_interval = 1.0 / self.rate_limit
        if now - self._last_dispatch < min_interval:
            await asyncio.sleep(min_interval - (now - self._last_dispatch))
        self._last_dispatch = time.time()

        await super()._process_item(item, handler_name)


# Utility: priority-aware batch
async def priority_batch(
    items: List[tuple],  # (payload, priority)
    processor: Callable,
    max_concurrent: int = 5,
) -> Dict[int, Any]:
    pool = AsyncWorkerPool(max_workers=max_concurrent)
    pool.register_handler("priority", processor)

    for payload, priority in items:
        await pool.submit(payload, priority=priority, handler="priority")

    return await pool.run_all("priority")
```
