from trajectory_planning import *


class Controller:
	def __init__(self):
		reference_points = [
			[0, 0, 0, 0],
			[1, 1, -1, 20],
			[0, 0, -1, 200],
			[-1, -1, -1, 20],
			[0, 0, -0, 0]
		]
		self.path = interpolate_path(reference_points, 1)
		self.path_len = len(self.path)
		self.front_left_pos = 0
		self.front_right_pos = self.path_len // 4
		self.rear_left_pos = self.path_len // 2
		self.rear_right_pos = self.path_len // 4 * 3
		self.front_speed = 0
		self.right_speed = 0
		self.rotation_speed = 0
		self.steps = 1
		self.height_top = -90
		self.height_bottom = -110

	def next_point(self):
		self.front_left_pos += self.steps
		self.front_right_pos += self.steps
		self.rear_left_pos += self.steps
		self.rear_right_pos += self.steps
		if self.front_left_pos >= self.path_len:
			self.front_left_pos = 0
		if self.front_right_pos >= self.path_len:
			self.front_right_pos = 0
		if self.rear_left_pos >= self.path_len:
			self.rear_left_pos = 0
		if self.rear_right_pos >= self.path_len:
			self.rear_right_pos = 0

	def get_positions(self):
		front_left = self.path[self.front_left_pos]
		front_right = self.path[self.front_right_pos]
		rear_left = self.path[self.rear_left_pos]
		rear_right = self.path[self.rear_right_pos]

		height_proportion = self.height_top - self.height_bottom

		front_left = [front_left[0] * self.right_speed, front_left[1] * self.front_speed, front_left[2] * height_proportion + self.height_top]
		front_right = [front_right[0] * self.right_speed, front_right[1] * self.front_speed, front_right[2] * height_proportion + self.height_top]
		rear_left = [rear_left[0] * self.right_speed, rear_left[1] * self.front_speed, rear_left[2] * height_proportion + self.height_top]
		rear_right = [rear_right[0] * self.right_speed, rear_right[1] * self.front_speed, rear_right[2] * height_proportion + self.height_top]

		return [front_left, front_right, rear_left, rear_right]

	def set_speeds(self, forward, right, rotation, steps=1):
		self.front_speed = forward
		self.right_speed = -right
		self.rotation_speed = rotation
		self.steps = steps



if __name__ == '__main__':
	controller = Controller()
	controller.height_top = -80
	controller.height_bottom = -120
	controller.set_speeds(20, 0, 0,2)
	for i in range(1000):
		print(controller.get_positions())
		controller.next_point()
