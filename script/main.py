import board
import busio
from adafruit_pca9685 import PCA9685
import time
from dog import *
from trajectory_planning import *
from setting_reader import *
from controller import *
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

# x, y, z - are the main coordinates. x -> left/right,
# y -> front/back
# z -> up/down
# i is a magical coordinate just to increase length of path and number of steps at some intervals
reference_points = [
	[0, 0, -0.9, 0],
	# [0, 0, -189],
	[0, 10, -1.10, 20],
	[0, -25, -1.10, 200],
	[0, -30, -1.10, 20],
	[0, 0, -0.90, 0]
]


desired_positions = interpolate_path(reference_points, 3)

# desired_positions = [[0, -0, -150]]



front_left_pos = 0

pos_update_time = 0.01

last_pos_update_time = time.time()
offset = len(desired_positions) // 4
controller.set_speeds(0, 0, 0, 2)
controller.height_top = -70
controller.height_bottom = -120
while True:

	if time.time() - last_pos_update_time > pos_update_time:
		controller.next_point()
		positions = controller.get_positions()
		front_left.go_to_position(*positions[0])
		front_right.go_to_position(*positions[1])
		rear_left.go_to_position(*positions[2])
		rear_right.go_to_position(*positions[3])
		last_pos_update_time = time.time()
		front_left.set_angles()
		front_right.set_angles()
		rear_left.set_angles()
		rear_right.set_angles()
		# front_left_pos += 1
		# if front_left_pos < 0:
		# 	front_left_pos += len(desired_positions)
		# front_right_pos = front_left_pos + 1 * offset
		# rear_left_pos = front_left_pos + 2 * offset
		# rear_right_pos = front_left_pos + 3 * offset
		# if front_left_pos >= len(desired_positions):
		# 	front_left_pos = 0
		# if front_right_pos >= len(desired_positions):
		# 	front_right_pos -= len(desired_positions)
		# if rear_left_pos >= len(desired_positions):
		# 	rear_left_pos -= len(desired_positions)
		# if rear_right_pos >= len(desired_positions):
		# 	rear_right_pos -= len(desired_positions)
		#
		# front_left.go_to_position(*desired_positions[front_left_pos])
		# front_left.set_angles()
		#
		# front_right.go_to_position(*desired_positions[front_right_pos])
		# front_right.set_angles()
		#
		# rear_left.go_to_position(*desired_positions[rear_left_pos])
		# rear_left.set_angles()
		#
		# rear_right.go_to_position(*desired_positions[rear_right_pos])
		# rear_right.set_angles()
