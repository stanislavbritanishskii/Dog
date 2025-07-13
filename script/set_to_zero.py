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
leg2 = Leg(pca.channels[10], pca.channels[11], pca.channels[12])
leg3 = Leg(pca.channels[7], pca.channels[8], pca.channels[9])
leg4 = Leg(pca.channels[4], pca.channels[5], pca.channels[6])
legs = []

for i in range(4,14,3):
	print(i, i+1, i+2)
	legs.append(Leg(pca.channels[i], pca.channels[i+1], pca.channels[i+2]))


while True:
	for leg in legs:
		leg.base_angle = 0
		leg.hip_angle = 0
		leg.knee_angle = 0
		leg.set_angles()

