"""
Created by Epic at 12/25/20
"""
from logging import getLogger


class BaseState:
    name = "base"

    def __init__(self, drone):
        self.active = False
        self.drone = drone
        self.logger = getLogger("dronecontrol.state.%s" % self.name)

    async def on_activate(self):
        pass

    async def on_deactivate(self):
        pass

    async def on_data(self, context):
        pass
