import board
import busio
from adafruit_pca9685 import PCA9685
import time
from dog import *
from trajectory_planning import *
from setting_reader import *
from controller import *
from udp_listener import *
# Initialize I2C bus using the Pi's default SCL and SDA pins
i2c = busio.I2C(3, 2)

# Create the PCA9685 instance
pca = PCA9685(i2c)
# pca = PCA9685()
pca.frequency = 50  # Set frequency to 50Hz for servo control


settings, default, front_left_s, front_right_s, rear_left_s, rear_right_s = read_settings("settings.json")

front_left = Leg(pca, default, front_left_s)
front_right = Leg(pca, default, front_right_s)
rear_left = Leg(pca, default, rear_left_s)
rear_right = Leg(pca, default, rear_right_s)

controller = Controller()

# desired_positions = [[0, -0, -150]]



front_left_pos = 0

pos_update_time = 0.01

last_pos_update_time = time.time()
controller.set_speeds(0, 0, 0, 1)
controller.height_top = -65
controller.height_bottom = -75

listener = UDPControlListener("0.0.0.0", 9998)
listener.start()
control_data = ControlData()


def handle_exit(signum, frame):
	print("\nStopping listener and cleaning up...")
	listener.stop()

controller.trot = True
while True:
	control_data = listener.get_last_received_data()
	print(control_data.forward, control_data.right)
	controller.set_speeds(control_data.forward, control_data.right, control_data.rotation, control_data.step_count)
	if time.time() - last_pos_update_time > control_data.delay_ms / 1000:
		controller.next_point()
		positions = controller.get_positions()
		print(positions)
		front_left.go_to_position(*positions[0])
		front_right.go_to_position(*positions[1])
		rear_left.go_to_position(*positions[2])
		rear_right.go_to_position(*positions[3])
		last_pos_update_time = time.time()
		front_left.set_angles()
		front_right.set_angles()
		rear_left.set_angles()
		rear_right.set_angles()
