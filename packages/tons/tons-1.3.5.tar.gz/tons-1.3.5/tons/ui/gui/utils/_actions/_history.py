from copy import copy
from typing import Union, Dict, Sequence, Iterator, Set, Tuple
from uuid import UUID

from ._actions import BroadcastTaskResult, TransferTask, DnsRefreshTask, DeployWalletTask, BroadcastTask


class ActionsHistory:
    def __init__(self):
        self._pending_broadcast_tasks: Dict[UUID, BroadcastTask] = dict()
        self._broadcast_results: Dict[UUID, BroadcastTaskResult] = dict()
        self._taken_tasks: Set[UUID] = set()
        self._cancelled_tasks: Set[UUID] = set()

    def add_pending_task(self, task_id: UUID, task: BroadcastTask):
        self._pending_broadcast_tasks[task_id] = task

    def get_pending_task(self, task_id: UUID) -> BroadcastTask:
        return self._pending_broadcast_tasks[task_id]

    def remove_pending_task(self, task_id: UUID):
        self._pending_broadcast_tasks.pop(task_id)

    def add_broadcast_result(self, task_id: UUID, task_result: BroadcastTaskResult):
        self._broadcast_results[task_id] = task_result

    @property
    def broadcast_results(self) -> Iterator[Tuple[UUID, BroadcastTaskResult]]:
        broadcast_tasks = copy(self._broadcast_results)
        for task_id in sorted(broadcast_tasks.keys(), key=lambda x: broadcast_tasks[x].time_start, reverse=True):
            yield task_id, broadcast_tasks[task_id]

    @property
    def pending_tasks(self) -> Iterator[Tuple[UUID, BroadcastTask]]:
        pending_tasks = copy(self._pending_broadcast_tasks)
        for task_id in sorted(pending_tasks.keys(), key=lambda x: pending_tasks[x].time_start, reverse=True):
            yield task_id, pending_tasks[task_id]

    @property
    def any_pending(self):
        return bool(self._pending_broadcast_tasks)

    def set_pending_task_taken(self, task_id: UUID):
        self._taken_tasks.add(task_id)

    def task_is_taken(self, task_id: UUID) -> bool:
        return task_id in self._taken_tasks

    def set_pending_task_cancelled(self, task_id: UUID):
        self._cancelled_tasks.add(task_id)

    def task_is_cancelled(self, task_id: UUID) -> bool:
        return task_id in self._cancelled_tasks
