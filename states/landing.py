"""
Created by Epic at 12/27/20
"""
from .base import BaseState


class LandingState(BaseState):
    name = "landing"

    async def on_activate(self):
        await self.drone.send_confirmation("land")
        await self.drone.exit_state()
