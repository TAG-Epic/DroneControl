from drone import Drone

current = Drone()

current.queue_state("takeoff")

current.receive_t.join()
