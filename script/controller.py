from trajectory_planning import *


class Controller:
	def __init__(self):
		reference_points = [
			[0, 0, 0, 0],
			[1, 1, -1, 30],
			[0, 0, -1, 200],
			[-1, -1, -1, 35],
			[-1, -1, -1.2, 30],
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
		hx = 1
		hy = 1
		self.leg_base = {
			'front_left': [-hx, +hy],
			'front_right': [-hx, -hy],
			'rear_left': [+hx, +hy],
			'rear_right': [+hx, -hy],
		}


	def next_point(self):
		self.front_left_pos = (self.front_left_pos + self.steps) % self.path_len
		self.front_right_pos = (self.front_right_pos + self.steps) % self.path_len
		self.rear_left_pos = (self.rear_left_pos + self.steps) % self.path_len
		self.rear_right_pos = (self.rear_right_pos + self.steps) % self.path_len


	def get_positions(self):
		def compute_leg(name, leg_point):
			lx, ly, lz = leg_point

			# translation
			vx_t = lx * self.right_speed
			vy_t = ly * self.front_speed

			# rotation about body center
			rx, ry = self.leg_base[name]
			vx_r = self.rotation_speed * rx * lx
			vy_r =  self.rotation_speed * ry * ly

			# combine
			vx = vx_t + vx_r
			vy = vy_t + vy_r

			# vertical lift
			vz = lz * (self.height_top - self.height_bottom) + self.height_top
			return [vx, vy, vz]

		fl = compute_leg('front_left',  self.path[self.front_left_pos])
		fr = compute_leg('front_right', self.path[self.front_right_pos])
		rl = compute_leg('rear_left',   self.path[self.rear_left_pos])
		rr = compute_leg('rear_right',  self.path[self.rear_right_pos])
		return [fl, fr, rl, rr]

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
