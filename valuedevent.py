"""
Created by Epic at 12/27/20
"""
from asyncio import Event


class ValuedEvent(Event):
    def __init__(self):
        super().__init__()
        self.value = None

    def set(self, value) -> None:
        self.value = value
        super().set()

    async def wait(self):
        await super().wait()
        return self.value
