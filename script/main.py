import board
import busio
from adafruit_pca9685 import PCA9685
import time
from dog3 import *
from trajectory_planning import *

# Initialize I2C bus using the Pi's default SCL and SDA pins
i2c = busio.I2C(3, 2)

# Create the PCA9685 instance
pca = PCA9685(i2c)
# pca = PCA9685()
pca.frequency = 50  # Set frequency to 50Hz for servo control

leg1 = Leg(pca.channels[13], pca.channels[14], pca.channels[15])

reference_points = [
	[0, 0, -100],
	[0, 0, -189],
	[0, 50, -150],
	[0, -50, -150],
	[0, 0, -100]
]

desired_positions = interpolate_path(reference_points, 3)

desired_positions = [[10, 20, -150]]



pos = 0
pos_update_time = 0.04
last_pos_update_time = time.time()
while True:
	if time.time() - last_pos_update_time > pos_update_time:
		last_pos_update_time = time.time()
		pos += 1
		if pos >= len(desired_positions):
			pos = 0
		leg1.go_to_position(*desired_positions[pos])

		leg1.set_angles()
