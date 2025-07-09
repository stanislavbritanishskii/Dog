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

		# New segment: the upper leg controlled by the base joint
		self.upper_len = 42  # Length of the segment after the base joint
		self.thigh_len = 81  # Thigh length
		self.shank_len = 66  # Shank length

		# Angle limits (in degrees)
		self.base_min_angle = -45
		self.base_max_angle = 45

		self.hip_min_angle = -45
		self.hip_max_angle = 45

		# Knee limits: allowed range is between 0° and 90° (even though defined as 90 and 0)
		self.knee_min_angle = 90
		self.knee_max_angle = 0

		# Current angles in radians
		self.base_angle = 0
		self.hip_angle = 0
		self.knee_angle = 0

	def go_to_position(self, x, y, z):
		# --- Base Angle ---
		# Calculate desired base angle (yaw) in radians and degrees
		desired_base_angle = math.atan2(y, x)
		desired_base_deg = math.degrees(desired_base_angle)
		# Clamp base angle to allowed range
		base_low = min(self.base_min_angle, self.base_max_angle)
		base_high = max(self.base_min_angle, self.base_max_angle)
		clamped_base_deg = max(base_low, min(desired_base_deg, base_high))
		self.base_angle = math.radians(clamped_base_deg)

		# --- Horizontal Distance ---
		# Compute horizontal distance from origin
		r = math.hypot(x, y)
		# The upper leg requires a minimum horizontal distance equal to its length.
		# If target is too close, clamp r to self.upper_len.
		if r < self.upper_len:
			r = self.upper_len
		# Recompute x,y direction using the clamped r and desired base angle
		clamped_x = r * math.cos(desired_base_angle)
		clamped_y = r * math.sin(desired_base_angle)

		# Effective planar coordinates for the thigh-shank chain
		planar_x = r - self.upper_len
		planar_y = z

		# --- Clamp Planar Target ---
		L1 = self.thigh_len
		L2 = self.shank_len
		# Compute distance in the planar chain
		d = math.hypot(planar_x, planar_y)
		# Reachable distance range for the two-link planar arm
		min_d = abs(L1 - L2)
		max_d = L1 + L2
		# Clamp d to reachable range
		if d < min_d:
			d = min_d
		if d > max_d:
			d = max_d
		# Retain the direction (if d is 0, alpha=0)
		alpha = math.atan2(planar_y, planar_x) if (planar_x != 0 or planar_y != 0) else 0
		planar_x = d * math.cos(alpha)
		planar_y = d * math.sin(alpha)

		# --- Inverse Kinematics for Planar Chain ---
		# Compute cosine for the knee angle
		cos_theta2 = (planar_x ** 2 + planar_y ** 2 - L1 ** 2 - L2 ** 2) / (2 * L1 * L2)
		cos_theta2 = max(-1, min(1, cos_theta2))
		theta2 = math.acos(cos_theta2)
		# Two possible solutions: Candidate A (elbow-down) and Candidate B (elbow-up)
		theta1_a = math.atan2(planar_y, planar_x) - math.atan2(L2 * math.sin(theta2), L1 + L2 * math.cos(theta2))
		theta2_a = theta2

		theta2_b = -theta2
		theta1_b = math.atan2(planar_y, planar_x) - math.atan2(L2 * math.sin(theta2_b), L1 + L2 * math.cos(theta2_b))

		# --- Helper: Clamping Function ---
		def clamp(val, lo, hi):
			return max(lo, min(val, hi))

		# For hip, allowed range in degrees:
		hip_low = min(self.hip_min_angle, self.hip_max_angle)
		hip_high = max(self.hip_min_angle, self.hip_max_angle)
		# For knee, allowed range (0 to 90° in our case):
		knee_low = min(self.knee_min_angle, self.knee_max_angle)
		knee_high = max(self.knee_min_angle, self.knee_max_angle)

		# --- Convert Candidate Solutions to Degrees and Clamp ---
		hip_deg_a = math.degrees(theta1_a)
		knee_deg_a = math.degrees(theta2_a)
		clamped_hip_a = clamp(hip_deg_a, hip_low, hip_high)
		clamped_knee_a = clamp(knee_deg_a, knee_low, knee_high)

		hip_deg_b = math.degrees(theta1_b)
		knee_deg_b = math.degrees(theta2_b)
		clamped_hip_b = clamp(hip_deg_b, hip_low, hip_high)
		clamped_knee_b = clamp(knee_deg_b, knee_low, knee_high)

		# --- Choose the Best Candidate ---
		# Compare the clamped candidate solutions to the current configuration (in degrees)
		current_hip_deg = math.degrees(self.hip_angle)
		current_knee_deg = math.degrees(self.knee_angle)
		error_a = abs(clamped_hip_a - current_hip_deg) + abs(clamped_knee_a - current_knee_deg)
		error_b = abs(clamped_hip_b - current_hip_deg) + abs(clamped_knee_b - current_knee_deg)

		if error_a <= error_b:
			chosen_hip_deg = clamped_hip_a
			chosen_knee_deg = clamped_knee_a
		else:
			chosen_hip_deg = clamped_hip_b
			chosen_knee_deg = clamped_knee_b

		# Update joint angles in radians
		self.hip_angle = math.radians(chosen_hip_deg)
		self.knee_angle = math.radians(chosen_knee_deg)

		self.base_angle = math.degrees (self.base_angle)
		self.hip_angle = math.degrees(self.hip_angle)
		self.knee_angle = math.degrees(self.knee_angle)

	def set_angles(self):
		# Convert angles from radians to degrees for display and servo control
		print("Base:", self.base_angle,
			  "Hip:", self.hip_angle,
			  "Knee:", self.knee_angle)
		self.base_channel.duty_cycle = angle_to_pulse(self.base_angle, self.base_min_angle,
													  self.base_max_angle)
		self.hip_channel.duty_cycle = angle_to_pulse(-self.hip_angle, self.hip_min_angle,
													 self.hip_max_angle)
		self.knee_channel.duty_cycle = angle_to_pulse(self.knee_angle, self.knee_min_angle,
													  self.knee_max_angle)
