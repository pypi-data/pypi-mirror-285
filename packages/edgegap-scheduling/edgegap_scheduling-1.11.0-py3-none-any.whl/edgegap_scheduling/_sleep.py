import asyncio
from asyncio import Task


class AsyncSleep:
    def __init__(self):
        self.tasks = {}

    async def sleep(self, identifier: str, delay: float | int, result=None):
        coro = asyncio.sleep(delay, result=result)
        task = asyncio.ensure_future(coro)
        self.tasks[identifier] = task

        try:
            return await task
        except asyncio.CancelledError:
            return result
        finally:
            self.tasks.pop(task, None)

    def __cancel_one_helper(self, identifier: str) -> Task | None:
        task = self.tasks.get(identifier)

        if task:
            task.cancel()

            return task

    async def cancel_one(self, identifier: str) -> bool:
        task = self.__cancel_one_helper(identifier)

        if task is None:
            raise KeyError(f'Task {identifier} not found')

        await asyncio.wait([task])

        self.tasks.pop(task, None)
        return True

    def __cancel_all_helper(self) -> dict:
        cancelled = {}

        for identifier, task in self.tasks.items():
            if task.cancel():
                cancelled[identifier] = task

        return cancelled

    async def cancel_all(self) -> int:
        cancelled = self.__cancel_all_helper()

        if len(cancelled) > 0:
            await asyncio.wait(self.tasks.values())

            for identifier, _ in cancelled.items():
                self.tasks.pop(identifier)

        return len(cancelled)
