from drone import Drone

current = Drone()

current.change_state("takeoff")

current.receive_t.join()