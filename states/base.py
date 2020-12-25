"""
Created by Epic at 12/25/20
"""


class BaseState:
    def __init__(self, drone):
        self.active = False
        self.drone = drone

    def on_activate(self):
        pass

    def on_deactivate(self):
        pass

    def on_data(self):
        pass
