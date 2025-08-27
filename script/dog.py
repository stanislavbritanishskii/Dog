import math

from numpy.f2py.crackfortran import privatepattern


def bound(val, lower_limit, upper_limit):
	return min(max(val, lower_limit), upper_limit)


def is_zero(val: float) -> bool:
	if 0.01 > val > -0.01:
		return True
	return False


class Coordinate:
	def __init__(self, x: float, y: float, z: float):
		self.x = x
		self.y = y
		self.z = z

	def __str__(self) -> str:
		return f"({self.x}, {self.y}, {self.z})"

	def __sub__(self, other: "Coordinate") -> "Coordinate":
		return Coordinate(self.x - other.x, self.y - other.y, self.z - other.z)

	def length(self) -> float:
		return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)


def angle_between_vectors(a, b):
	dot = a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
	norm_a = math.sqrt(a[0] ** 2 + a[1] ** 2 + a[2] ** 2)
	norm_b = math.sqrt(b[0] ** 2 + b[1] ** 2 + b[2] ** 2)

	if norm_a == 0.0 or norm_b == 0.0:
		raise ValueError("One of the vectors is zero-length.")

	cos_theta = dot / (norm_a * norm_b)

	# Clamp to avoid math domain error due to floating-point inaccuracy
	cos_theta = max(-1.0, min(1.0, cos_theta))

	return math.acos(cos_theta)  # in radians


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
	def __init__(self, pca, default_settings: dict, private_settings: dict):
		self.base_channel = pca.channels[private_settings.get("base_channel")]
		self.hip_channel = pca.channels[private_settings.get("hip_channel")]
		self.knee_channel = pca.channels[private_settings.get("knee_channel")]
		self.default_settings = default_settings
		self.private_settings = private_settings

		# Segment lengths (in mm or your unit)
		self.upper_len = private_settings.get("upper_len")  # Fixed length from base joint to hip joint
		self.thigh_len = private_settings.get("thigh_len")  # Thigh length
		self.shank_len = private_settings.get("shank_len")  # Shank length

		# Pre-calculate squared lengths if needed
		self.thigh_len_squared = self.thigh_len ** 2
		self.shank_len_squared = self.shank_len ** 2

		# Joint angle limits (in degrees)
		self.base_min_angle = default_settings.get("base_min_angle") + private_settings.get("base_offset")
		self.base_max_angle = default_settings.get("base_max_angle") + private_settings.get("base_offset")

		self.hip_min_angle = default_settings.get("hip_min_angle") + private_settings.get("hip_offset")
		self.hip_max_angle = default_settings.get("hip_max_angle") + private_settings.get("hip_offset")

		self.knee_min_angle = default_settings.get("knee_min_angle") + private_settings.get("knee_offset")
		self.knee_max_angle = default_settings.get("knee_max_angle") + private_settings.get("knee_offset")

		self.base_angle = 0
		self.hip_angle = 0
		self.knee_angle = 0

	def reset_angles(self, default_settings: dict, private_settings: dict):

		# Joint angle limits (in degrees)
		self.base_min_angle = default_settings.get("base_min_angle") + private_settings.get("base_offset")
		self.base_max_angle = default_settings.get("base_max_angle") + private_settings.get("base_offset")

		self.hip_min_angle = default_settings.get("hip_min_angle") + private_settings.get("hip_offset")
		self.hip_max_angle = default_settings.get("hip_max_angle") + private_settings.get("hip_offset")

		self.knee_min_angle = default_settings.get("knee_min_angle") + private_settings.get("knee_offset")
		self.knee_max_angle = default_settings.get("knee_max_angle") + private_settings.get("knee_offset")

	def go_to_position(self, x, y, z):
		c = Coordinate(x, y, z)
		if z or x:
			base_angle = math.asin(x / math.sqrt(z ** 2 + x ** 2))
		else:
			base_angle = 0
		self.base_angle = math.degrees(base_angle)
		upper_coord = Coordinate(0, 0, 0)
		upper_coord.x = self.upper_len * math.sin(base_angle)
		upper_coord.z = -self.upper_len * math.cos(base_angle)
		# print(upper_coord)
		# print("distance to desired", (upper_coord - c).length())
		left_distance = (upper_coord - c).length()
		# print(left_distance, self.thigh_len, self.shank_len)
		knee_angle = math.pi - math.acos(bound(
			(self.thigh_len ** 2 + self.shank_len ** 2 - left_distance ** 2) / (2 * self.thigh_len * self.shank_len),
			-1, 1))

		top_vector = [upper_coord.x, upper_coord.y, upper_coord.z]
		bottom_vector = [upper_coord.x - x, upper_coord.y - y, upper_coord.z - z]
		inter_angle = math.copysign(math.pi - angle_between_vectors(top_vector, bottom_vector), y)
		# print("inter_angle;", math.degrees(inter_angle))
		hip_angle = math.acos(bound(
			(self.thigh_len ** 2 - self.shank_len ** 2 + left_distance ** 2) / (2 * self.thigh_len * left_distance), -1,
			1)) + inter_angle
		# print("hip angle: ",math.degrees(hip_angle))
		# print("knee angle: ", math.degrees(knee_angle))

		self.base_angle = math.degrees(base_angle)
		self.hip_angle = math.degrees(hip_angle)
		self.knee_angle = math.degrees(knee_angle)
		self.base_angle *= self.private_settings.get("base")
		self.hip_angle *= self.private_settings.get("hip")
		self.knee_angle *= self.private_settings.get("knee")

	def set_angles(self):
		# 	Update the servo channels based on computed duty cycles.
		# print("Setting angles: Base:", self.base_angle,
		# 	  "Hip:", self.hip_angle,
		# 	  "Knee:", self.knee_angle)
		self.base_channel.duty_cycle = angle_to_pulse(self.base_angle, self.base_min_angle, self.base_max_angle)
		self.hip_channel.duty_cycle = angle_to_pulse(self.hip_angle, self.hip_min_angle, self.hip_max_angle)
		self.knee_channel.duty_cycle = angle_to_pulse(self.knee_angle, self.knee_min_angle, self.knee_max_angle)


if __name__ == "__main__":
	pass
# leg = Leg(1, 2, 3)
#
# leg.hip_angle = 0
# leg.knee_angle = 0
# leg.knee_min_angle = 0
# leg.set_angles()
