import board
import busio
from adafruit_pca9685 import PCA9685
import time
from dog import *
from trajectory_planning import *
from setting_reader import *
# Initialize I2C bus using the Pi's default SCL and SDA pins
i2c = busio.I2C(3, 2)

# Create the PCA9685 instance
pca = PCA9685(i2c)
# pca = PCA9685()
pca.frequency = 50  # Set frequency to 50Hz for servo control


settings, default, front_left_s, front_right_s, rear_left_s, rear_right_s = read_settings("settings.json")

front_right = Leg(pca.channels[13], pca.channels[14], pca.channels[15], right=True)
front_left = Leg(pca.channels[10], pca.channels[11], pca.channels[12], right=False)

# x, y, z - are the main coordinates. x -> left/right,
# y -> front/back
# z -> up/down
# i is a magical coordinate just to increase length of path and number of steps at some intervals
reference_points = [
	[0, 0, -80, 0],
	# [0, 0, -189],
	[0, 20, -120, 0],
	[0, -30, -120, 100],
	[0, -45, -120, 0],
	[0, 0, -80, 0]
]




# reference_points = [
# 	[-10, 0, -80, 0],
# 	# [0, 0, -189],
# 	[-50, 0, -120, 0],
# 	[-0, 0, -120, 100],
# 	[50, 0, -120, 0],
# 	[-10, 0, -80, 0]
# ]
#
#
# reference_points = [
# 	[-50, 0, -80, 0],
# 	# [0, 0, -189],
# 	[-50, 20, -120, 0],
# 	[-50, -30, -120, 100],
# 	[-50, -40, -120, 0],
# 	[-50, 0, -80, 0]
# ]

desired_positions = interpolate_path(reference_points, 3)

# desired_positions = [[0, -0, -150]]



pos = 0
pos_update_time = 0.03
last_pos_update_time = time.time()
offset = len(desired_positions) // 4
while True:

	if time.time() - last_pos_update_time > pos_update_time:
		last_pos_update_time = time.time()
		pos += 1
		other_pos = pos + offset
		if pos >= len(desired_positions):
			pos = 0
		if other_pos >= len(desired_positions):
			other_pos -= len(desired_positions)

		position = desired_positions[pos]
		position[0] -= 5
		front_left.go_to_position(*position)
		front_left.set_angles()

		position = desired_positions[other_pos]
		position[0] += 5
		front_right.go_to_position(*position)
		front_right.set_angles()
