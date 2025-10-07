import board
import busio
from adafruit_pca9685 import PCA9685
import time
from dog import *
from setting_reader import *
from controller import *

class OveralController:
	def __init__(self):
		# Initialize I2C bus using the Pi's default SCL and SDA pins
		self.i2c = busio.I2C(3, 2)
		# Create the PCA9685 instance
		self.pca = PCA9685(self.i2c)
		# pca = PCA9685()
		self.pca.frequency = 50  # Set frequency to 50Hz for servo control

		settings, default, front_left_s, front_right_s, rear_left_s, rear_right_s, general, head_s = read_settings("settings.json")

		self.max_forward_speed = general.get('collinear_max_speed')
		self.max_side_speed = general.get('perp_max_speed')
		self.max_rotation_speed = general.get('rotation_max_speed')
		self.step_count = general.get('step_count')
		self.pos_update_time = general.get("delay")
		print(self.max_forward_speed, self.max_side_speed, self.max_rotation_speed)
		print(self.step_count, self.pos_update_time)

		self.front_left = Leg(self.pca, default, front_left_s)
		self.front_right = Leg(self.pca, default, front_right_s)
		self.rear_left = Leg(self.pca, default, rear_left_s)
		self.rear_right = Leg(self.pca, default, rear_right_s)
		self.head = Head(self.pca, head_s)

		self.controller = Controller()



		self.last_pos_update_time = time.time()
		self.controller.set_speeds(0, 0, 0, 2)
		self.controller.height_top = -65
		self.controller.height_bottom = -75
		self.controller.trot = True

	def iterate(self, forward, right, rotation, head_right, head_up):
		self.controller.set_speeds(forward * self.max_forward_speed, right * self.max_side_speed, rotation * self.max_rotation_speed, self.step_count)
		self.head.move(head_right, head_up)
		self.head.set_angles()
		print(forward * self.max_forward_speed, right * self.max_side_speed, rotation * self.max_rotation_speed, self.step_count)
		
		if time.time() - self.last_pos_update_time > self.pos_update_time / 1000:
			self.controller.next_point()
			positions = self.controller.get_positions()
			# print(positions)
			self.front_left.go_to_position(*positions[0])
			self.front_right.go_to_position(*positions[1])
			self.rear_left.go_to_position(*positions[2])
			self.rear_right.go_to_position(*positions[3])
			self.last_pos_update_time = time.time()
			self.front_left.set_angles()
			self.front_right.set_angles()
			self.rear_left.set_angles()
			self.rear_right.set_angles()

