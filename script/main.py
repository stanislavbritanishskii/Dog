import board
import busio
from adafruit_pca9685 import PCA9685
import time
from dog4 import *
from trajectory_planning import *

# Initialize I2C bus using the Pi's default SCL and SDA pins
i2c = busio.I2C(3, 2)

# Create the PCA9685 instance
pca = PCA9685(i2c)
# pca = PCA9685()
pca.frequency = 50  # Set frequency to 50Hz for servo control

leg1 = Leg(pca.channels[13], pca.channels[14], pca.channels[15])


# x, y, z - are the main coordinates. x -> left/right,
# y -> front/back
# z -> up/down
# i is a magical coordinate just to increase length of path and number of steps at some intervals
reference_points = [
	[-10, 0, -80, 0],
	# [0, 0, -189],
	[-10, 20, -120, 0],
	[-10, -30, -120, 100],
	[-10, -45, -120, 0],
	[-10, 0, -80, 0]
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
pos_update_time = 0.01
last_pos_update_time = time.time()
while True:
	# leg1.base_angle = 0
	# leg1.hip_angle = -0
	# leg1.knee_angle = -0
	# leg1.set_angles()
	# continue
	if time.time() - last_pos_update_time > pos_update_time:
		last_pos_update_time = time.time()
		pos += 1
		if pos >= len(desired_positions):
			pos = 0
		leg1.go_to_position(*desired_positions[pos])

		leg1.set_angles()
