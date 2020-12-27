"""
Created by Epic at 12/25/20
"""
from .base import BaseState


class TakeoffState(BaseState):
    name = "takeoff"

    async def on_activate(self):
        await self.drone.send_confirmation("takeoff")
        await self.drone.exit_state()
