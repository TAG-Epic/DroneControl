"""
Created by Epic at 12/25/20
"""
from .base import BaseState


class Takeoff(BaseState):
    def on_activate(self):
        self.drone.send("takeoff")
        self.drone.exit_state()
