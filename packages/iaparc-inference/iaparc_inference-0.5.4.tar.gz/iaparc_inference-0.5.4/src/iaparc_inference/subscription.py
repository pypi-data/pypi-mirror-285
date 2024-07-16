from __future__ import annotations

from ast import Subscript
import asyncio
from typing import (
    TYPE_CHECKING,
    AsyncIterator,
    Awaitable,
    Callable,
    List,
    Optional,
)
from uuid import uuid4

from nats import errors
# Default Pending Limits of Subscriptions
from nats.aio.msg import Msg
from nats.aio.subscription import Subscription

class BatchSubscription:

    def __init__(self, sub: Subscription, batch_size: int):
        self._sub = sub
        self._batch_size = batch_size
        self._dones = {}
        self._pending_tasks = {}
    
    async def get_batch(self, timeout: Optional[float] = 1.0) -> List[Msg]:
        msgs: List[Msg] = []
        task_name = str(uuid4())
        self._dones[task_name] = False
        try:
            msg = await self._sub.next_msg(timeout=600)
            msgs.append(msg)        
            future = asyncio.create_task(
                asyncio.wait_for(self._wait_for_next_batch(task_name), timeout)
            )
            self._pending_tasks[task_name] = future
            await future
        except asyncio.TimeoutError:
            if self._sub._conn.is_closed:
                raise errors.ConnectionClosedError
            self._dones[task_name] = True
            raise errors.TimeoutError
        except asyncio.CancelledError:
            if self._sub._conn.is_closed:
                raise errors.ConnectionClosedError
            self._dones[task_name] = True
            raise
        else:
            msgs.extend(self._pending_tasks[task_name])
            return msgs
        finally:
            self._pending_tasks.pop(task_name, None)        
            self._dones.pop(task_name, None)
        
        return msgs
    
    async def _wait_for_next_batch(self, task_name: str):
        self._pending_tasks[task_name] = []
        limit = self._batch_size - 1
        while not self._dones[task_name]:
            try:
                msg = await self._sub._pending_queue.get()
                self._sub._pending_size -= len(msg.data)
                self._sub._pending_queue.task_done()
                self._pending_tasks[task_name].append(msg)
                if len(self._pending_tasks[task_name]) >= limit:
                    break
            except asyncio.CancelledError:
                break