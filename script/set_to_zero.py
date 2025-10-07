import board
import busio
from adafruit_pca9685 import PCA9685
import time
from dog import *
from trajectory_planning import *
from setting_reader import *
import time
# Initialize I2C bus using the Pi's default SCL and SDA pins
i2c = busio.I2C(3, 2)

# Create the PCA9685 instance
pca = PCA9685(i2c)

pca.frequency = 50  # Set frequency to 50Hz for servo control
settings, default, front_left_s, front_right_s, rear_left_s, rear_right_s, general, head_s = read_settings("settings.json")

front_left = Leg(pca, default, front_left_s)
front_right = Leg(pca, default, front_right_s)
rear_left = Leg(pca, default, rear_left_s)
rear_right = Leg(pca, default, rear_right_s)
head = Head(pca, head_s)

legs = [front_left, front_right, rear_left, rear_right]


while True:
	time.sleep(0.5)
	settings, default, front_left_s, front_right_s, rear_left_s, rear_right_s, general, head_s = read_settings("settings.json")
	front_left.reset_angles(default, front_left_s)
	front_right.reset_angles(default, front_right_s)
	rear_left.reset_angles(default, rear_left_s)
	rear_right.reset_angles(default, rear_right_s)
	head.reset_angles(head_s)
	head.set_angles()
	for leg in legs:
		leg.base_angle = 0
		leg.hip_angle = 0
		leg.knee_angle = 0
		leg.set_angles()
