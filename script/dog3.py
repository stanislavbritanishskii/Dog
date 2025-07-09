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
	def __init__(self, base_channel, hip_channel, knee_channel):
		self.base_channel = base_channel
		self.hip_channel = hip_channel
		self.knee_channel = knee_channel

		# Segment lengths (in mm or your unit)
		self.upper_len = 42  # Fixed length from base joint to hip joint
		self.thigh_len = 81  # Thigh length
		self.shank_len = 66  # Shank length

		# Pre-calculate squared lengths if needed
		self.thigh_len_squared = self.thigh_len ** 2
		self.shank_len_squared = self.shank_len ** 2

		# Joint angle limits (in degrees)
		self.base_min_angle = -45
		self.base_max_angle = 45

		self.hip_min_angle = -45
		self.hip_max_angle = 45

		self.knee_min_angle = -90
		self.knee_max_angle = 0

		# Current joint angles (in degrees)
		self.base_angle = 0
		self.hip_angle = 0
		self.knee_angle = 0

	def go_to_position(self, x, y, z):
		# ---------------------------
		# 1. Base Joint (Rotation in xz)
		# ---------------------------
		# The base rotates in the xz plane.
		self.base_angle = math.degrees(math.atan2(x, -z))
		self.base_angle = min(max(self.base_angle, self.base_min_angle), self.base_max_angle)

		# ---------------------------
		# 2. Compute Hip Joint Position (End of Upper Segment)
		# ---------------------------
		# Since the base rotates in xz, the upper segment offset is applied in x and z.
		hip_x = math.sin(math.radians(self.base_angle)) * self.upper_len
		hip_y = 0  # No offset in y for the upper segment.
		hip_z = -math.cos(math.radians(self.base_angle)) * self.upper_len

		# ---------------------------
		# 3. Effective Vector from Hip Joint to Target Foot Position
		# ---------------------------
		# We work in the y-z plane (the plane in which the hip and knee operate).
		eff_y = y - hip_y  # equals y (since hip_y is 0)
		eff_z = z - hip_z  # vertical difference from hip joint

		# Lower distance (magnitude of the vector in y-z plane)
		L_lower = math.hypot(eff_y, eff_z)

		# ---------------------------
		# 4. Knee Angle Calculation
		# ---------------------------
		# Use the cosine law for the triangle formed by thigh, shank, and L_lower.
		cos_knee = (self.thigh_len ** 2 + self.shank_len ** 2 - L_lower ** 2) / (2 * self.thigh_len * self.shank_len)
		cos_knee = max(min(cos_knee, 1), -1)
		knee_angle_calc = math.degrees(math.acos(cos_knee))
		# Depending on your servo orientation, adjust the knee angle.
		self.knee_angle = knee_angle_calc - 180

		# ---------------------------
		# 5. Hip Angle Calculation
		# ---------------------------
		total_dist = math.dist([0, 0, 0], [x, y, z])
		ang1_cos = (self.upper_len ** 2 + L_lower ** 2 - total_dist ** 2) / (2 * self.upper_len * L_lower)
		ang1_cos = max(min(ang1_cos, 1), -1)
		ang1 = math.degrees(math.acos(ang1_cos))

		ang2_cos = (self.thigh_len_squared + L_lower ** 2 - self.shank_len_squared) / (2 * self.thigh_len * L_lower)
		ang2_cos = max(min(ang2_cos, 1), -1)
		ang2 = math.degrees(math.acos(ang2_cos))

		self.hip_angle = 180 - ang1 + ang2
		if y < 0:
			self.hip_angle *= -1
		# hip_angle_calc += 90
		# Clamp the hip angle to its allowed range.
		# print(self.hip_angle)
		# ---------------------------
		# Debug Prints (for verification)
		# ---------------------------
		# print("Target Position:", (x, y, z))
		# print("Base Angle (xz):", self.base_angle)
		# print("Hip Joint Position (upper segment end):", (hip_x, hip_y, hip_z))
		# print("Effective Vector (y, z):", (eff_y, eff_z), "with L_lower:", L_lower)
		# print("Computed Knee Angle:", self.knee_angle)
		# print("Line Angle in (y, z):", line_angle, "Angle Thigh Correction:", angle_thigh)
		# print("Computed Hip Angle:", self.hip_angle)

	def set_angles(self):
		# Update the servo channels based on computed duty cycles.
		print("Setting angles: Base:", self.base_angle,
			  "Hip:", self.hip_angle,
			  "Knee:", self.knee_angle)
		self.base_channel.duty_cycle = angle_to_pulse(self.base_angle, self.base_min_angle, self.base_max_angle)
		self.hip_channel.duty_cycle = angle_to_pulse(self.hip_angle, self.hip_min_angle, self.hip_max_angle)
		self.knee_channel.duty_cycle = angle_to_pulse(self.knee_angle, self.knee_min_angle, self.knee_max_angle)


if __name__ == "__main__":
	leg = Leg(1,2,3)
	leg.go_to_position(0,100,0)
	print(leg.base_angle, leg.knee_angle, leg.hip_angle )