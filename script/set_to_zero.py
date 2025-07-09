import board
import busio
from adafruit_pca9685 import PCA9685
# from Adafruit_PCA9685 import PCA9685


import time

# Initialize I2C bus using the Pi's default SCL and SDA pins
i2c = busio.I2C(3, 2)
ms_to_sig = int(1024 / 300)


def to_pulse(t, freq):
	period_us = 1_000_000 / freq
	duty_12bit = (t / period_us) * 4096  # Calculate 12-bit value
	return int(duty_12bit) << 4  # Scale to 16-bit by shifting left 4 bits


# Create the PCA9685 instance
pca = PCA9685(i2c)
# pca = PCA9685()
pca.frequency = 50  # Set frequency to 50Hz for servo control
for i in range(16):
	pca.channels[i].duty_cycle = to_pulse(1500, 50)

