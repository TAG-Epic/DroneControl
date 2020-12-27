"""
Created by Epic at 12/25/20
"""
import socket
from context import Context
from asyncio import get_event_loop, sleep, wait_for, TimeoutError, Lock
from logging import getLogger
from os import O_NONBLOCK
from fcntl import fcntl, F_SETFL

from states import TakeoffState, IdleState, PatrolState, LandingState
from valuedevent import ValuedEvent


class Drone:
    def __init__(self):
        # Generic config
        self.send_retry_amount = 10

        # Loggers
        self.logger = getLogger("dronecontrol")
        self.data_logger = getLogger("drone_control.stream")

        # Connection
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", 9000))
        fcntl(self.sock, F_SETFL, O_NONBLOCK)
        self.ip = ('192.168.10.1', 8889)

        # Tasks
        self.loop = get_event_loop()
        self.loop.create_task(self.receive_loop())

        # States
        self.state = IdleState(self)
        self._states = [
            IdleState,
            TakeoffState,
            PatrolState,
            LandingState
        ]
        self.states = {}
        for state in self._states:
            self.states[state.name] = state(self)
            self.logger.debug("Added state %s" % state.name)

        # State queue
        self.using_state_queue = True
        self.state_queue = []
        self.clearing_idle_state = Lock()

        # Etc
        self.listeners = []
        self.confirmation_event = ValuedEvent()

        # Startup
        self.send("command")
        self.loop.create_task(self.main())

    def send(self, data):
        self.data_logger.debug("> %s" % data)
        self.sock.sendto(data.encode("utf-8"), self.ip)

    async def send_confirmation(self, data):
        for i in range(self.send_retry_amount):
            self.send(data)
            try:
                val = await wait_for(self.confirmation_event.wait(), 1)
                self.confirmation_event.clear()
                if not val:
                    self.logger.debug("Warning? Retry count: %s/%s" % (i + 1, self.send_retry_amount))
                    continue
                return val
            except TimeoutError:
                self.logger.debug("No response? Retry count: %s/%s" % (i + 1, self.send_retry_amount))
                await sleep(.2)
                continue
        self.confirmation_event.clear()
        self.logger.warning("No response after %s retries" % self.send_retry_amount)
        return False

    async def receive_loop(self):
        while True:
            try:
                received = self.sock.recv(2048)
            except BlockingIOError:
                await sleep(0.1)
                continue
            try:
                data = received.decode("utf-8")
            except UnicodeDecodeError:
                print("Failed to decode: %s" % received)
                continue
            self.data_logger.debug("< %s" % data)
            for listener in self.listeners:
                context = Context(self, data)
                await listener(context)
            if data == "ok":
                self.confirmation_event.set(True)
            if data.startswith("error"):
                self.confirmation_event.set(False)

    async def exit_state(self):
        if not self.using_state_queue:
            raise TypeError("State queue isn't active!")
        self.logger.debug("State exited!")
        self.logger.debug(self.state_queue)
        await self.state.on_deactivate()
        try:
            self.state = self.state_queue.pop(0)
        except IndexError:
            self.state = self.states["idle"]
            self.logger.warning("No more states in queue. Idling")
        self.logger.info("New state: %s" % self.state.name)
        await self.state.on_activate()

    async def change_state(self, new_state):
        new_state = self.states[new_state]
        self.using_state_queue = False
        await self.state.on_deactivate()
        self.logger.info("Changed state: %s to %s" % (self.state.name, new_state.name))
        self.state = new_state
        await self.state.on_activate()

    async def safe_clear_idle(self):
        async with self.clearing_idle_state:
            if self.state.name == "idle":
                await self.exit_state()

    def queue_state(self, new_state):
        if not self.using_state_queue:
            raise TypeError("State queue isn't active!")
        self.state_queue.append(self.states[new_state])
        if self.state.name == "idle":
            self.loop.create_task(self.safe_clear_idle())

    async def main(self):
        try:
            while True:
                await sleep(10)
        except KeyboardInterrupt:
            ok = await self.send_confirmation("land")
            if not ok:
                while not ok:
                    ok = self.send_confirmation("emergency")

    def start(self):
        self.loop.run_forever()
