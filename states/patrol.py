"""
Created by Epic at 12/25/20
"""
from .base import BaseState


class PatrolState(BaseState):
    name = "patrol"

    def __init__(self, drone):
        super().__init__(drone)
        self.distance = 20

    def on_activate(self):
        self.drone.send("forward %s" % self.distance)
