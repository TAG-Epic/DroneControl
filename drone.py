"""
Created by Epic at 12/25/20
"""
import socket
from threading import Thread
from context import Context

from states import TakeoffState, IdleState, PatrolState


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

        self._states = [
            IdleState,
            TakeoffState,
            PatrolState
        ]

        self.states = {}
        self.send("command")

        for state in self._states:
            self.states[state.name] = state(self)
            print("Added state %s" % state.name)

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
        if not self.using_state_queue:
            raise TypeError("State queue isn't active!")
        print("State exited!")
        self.state.on_deactivate()
        try:
            self.state = self.state_queue.pop()
        except IndexError:
            self.state = self.states["idle"]
        print("New state: %s" % self.state.name)
        self.state.on_activate()

    def change_state(self, new_state):
        self.using_state_queue = False
        self.state.on_deactivate()
        print("Changed state: %s to %s" % (self.state.name, new_state.name))
        self.state = self.states[new_state]
        self.state.on_activate()

    def queue_state(self, new_state):
        if not self.using_state_queue:
            raise TypeError("State queue isn't active!")
        self.state_queue.append(self.states[new_state])
        if self.state.name == "idle":
            self.exit_state()
