"""
Created by Epic at 12/25/20
"""
from .base import BaseState


class PatrolState(BaseState):
    name = "patrol"

    def __init__(self, drone):
        super().__init__(drone)
        self.distance = 20
        self.times = 10

    async def on_activate(self):
        for i in range(self.times):
            await self.drone.send_confirmation("forward %s" % self.distance)
            await self.drone.send_confirmation("cw 180")
