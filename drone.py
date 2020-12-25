"""
Created by Epic at 12/25/20
"""
import socket
from threading import Thread
from context import Context
from states.takeoff import Takeoff
from states.idle import IdleState


class Drone:
    def __init__(self):
        self.state = IdleState(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", 9000))
        self.listeners = []
        self.ip = ('192.168.10.1', 8889)
        self.receive_t = Thread(target=self.receive_thread)
        self.receive_t.start()
        self.using_state_queue = True
        self.state_queue = []

        self.states = {
            "idle": IdleState(self),
            "takeoff": Takeoff(self)
        }

    def send(self, data):
        print("> %s" % data)
        self.sock.sendto(data.encode("utf-8"), self.ip)

    def receive_thread(self):
        data = self.sock.recv(2048).decode("utf-8")
        print("< %s" % data)
        for listener in self.listeners:
            context = Context(self, data)
            listener(context)

    def exit_state(self):
        print("State exited!")
        self.state.on_deactivate()
        try:
            self.state = self.states[self.state_queue.pop()]
        except IndexError:
            self.state = self.states["idle"]
        self.state.on_activate()
        print("New state: %s" % self.state)

    def change_state(self, new_state):
        self.state.on_deactivate()
        print("Changed state: %s to %s" % (self.state, new_state))
        self.state = self.states[new_state]
        self.state.on_activate()
