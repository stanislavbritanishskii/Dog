import math


class LegControl:
	def __init__(self):
		self.velocity = 1
		self.thigh_len = 10
		self.shank_len = 10
		self.thigh_angle = 0  # hip joint angle in radians
		self.knee = 0  # knee joint angle in radians (relative angle between thigh and shank)
		self.current_iter = 0

	def iterate(self, time):
		self.current_iter += time * self.velocity
		amp1 = math.radians(45)  # converting degrees to radians
		freq1 = 1.0  # frequency in Hz
		phase1 = 0  # phase offset

		amp2 = math.radians(45)
		freq2 = 1.0
		phase2 = math.pi / 4  # 45 degrees in radians

		self.thigh_angle = amp1 * math.sin(2 * math.pi * freq1 * self.current_iter + phase1)
		self.knee = amp2 * math.sin(2 * math.pi * freq2 * self.current_iter + phase2)

	def go_to_position(self, x, y):
		"""
		Compute and update the thigh_angle (hip) and knee angles to position the tip of the leg at (x, y).
		The hip is assumed to be at the origin. If there are two possible solutions, the one closer to the current angles is chosen.
		:param x: X-coordinate of the leg tip.
		:param y: Y-coordinate of the leg tip.
		"""
		L1 = self.thigh_len
		L2 = self.shank_len
		d = math.hypot(x, y)

		# Check if the target is reachable.
		if d > L1 + L2 or d < abs(L1 - L2):
			raise ValueError("Target position is unreachable.")

		# Compute the cosine of the knee angle using the law of cosines.
		cos_theta2 = (x ** 2 + y ** 2 - L1 ** 2 - L2 ** 2) / (2 * L1 * L2)
		# Clamp the value within [-1, 1] to avoid numerical errors.
		cos_theta2 = max(-1, min(1, cos_theta2))
		theta2 = math.acos(cos_theta2)

		# First solution (elbow-down configuration)
		theta1_a = math.atan2(y, x) - math.atan2(L2 * math.sin(theta2), L1 + L2 * math.cos(theta2))
		theta2_a = theta2

		# Second solution (elbow-up configuration)
		theta1_b = math.atan2(y, x) - math.atan2(L2 * math.sin(-theta2), L1 + L2 * math.cos(-theta2))
		theta2_b = -theta2

		# Choose the solution that is closer to the current angles.
		diff_a = abs(theta1_a - self.thigh_angle) + abs(theta2_a - self.knee)
		diff_b = abs(theta1_b - self.thigh_angle) + abs(theta2_b - self.knee)

		if diff_a <= diff_b:
			self.thigh_angle = theta1_a
			self.knee = theta2_a
		else:
			self.thigh_angle = theta1_b
			self.knee = theta2_b

	def get_angles(self):
		return [self.thigh_angle, self.knee]
