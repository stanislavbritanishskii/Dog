import math
def angle_to_pulse(angle, min_angle, max_angle):
	min_pulse = 500
	max_pulse = 2500
	freq = 50
	normalized = (angle - min_angle) / (max_angle - min_angle)
	pulse = min_pulse + normalized * (max_pulse - min_pulse)
	pulse = min(max(pulse, min_pulse), max_pulse)
	period_us = 1_000_000 / freq
	duty_12bit = (pulse / period_us) * 4096  # Calculate 12-bit value
	return int(duty_12bit) << 4  # Scale to 16-bit by shifting left 4 bits

class Leg:
	def __init__(self, hip_channel, knee_channel):
		self.hip_channel = hip_channel
		self.knee_channel = knee_channel
		self.thigh_len = 10
		self.shank_len = 10

		self.hip_min_angle = -45
		self.hip_max_angle = 45

		self.knee_min_angle = -90
		self.knee_max_angle = 0

		self.hip_angle = 0
		self.knee_angle = 0

	def go_to_position(self, x, y):
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
		diff_a = abs(theta1_a - self.hip_angle) + abs(theta2_a - self.knee_angle)
		diff_b = abs(theta1_b - self.hip_angle) + abs(theta2_b - self.knee_angle)

		if diff_a <= diff_b:
			self.hip_angle = theta1_a
			self.knee_angle = theta2_a
		else:
			self.hip_angle = theta1_b
			self.knee_angle = theta2_b

	def set_angles(self):
		print(math.degrees(self.hip_angle), math.degrees(self.knee_angle))

		self.hip_channel.duty_cycle = angle_to_pulse(math.degrees(self.hip_angle), self.hip_min_angle, self.hip_max_angle)
		self.knee_channel.duty_cycle = angle_to_pulse(math.degrees( self.knee_angle), self.knee_min_angle, self.knee_max_angle)

