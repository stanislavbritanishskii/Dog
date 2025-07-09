import pygame
import math
from leg_control import LegControl
import time
# Constants for leg segment lengths
THIGH_LENGTH = 100
SHANK_LENGTH = 100


class Leg:
	"""
	A simple leg class with two joints: hip and ankle.
	The leg is drawn with two segments.
	"""

	def __init__(self, base_pos, hip_angle=0, ankle_angle=0):
		# Base position (hip position)
		self.base_pos = base_pos
		# Angles in degrees
		self.hip_angle = hip_angle
		self.ankle_angle = ankle_angle

	def set_angles(self, hip_angle, ankle_angle):
		"""
		Update the angles for the hip and ankle joints.
		"""
		self.hip_angle = hip_angle
		self.ankle_angle = ankle_angle

	def draw(self, surface):
		"""
		Draw the leg on the given surface.
		Calculates the ankle and foot positions based on the angles.
		"""
		# Convert angles to radians for calculation
		hip_rad = self.hip_angle
		ankle_rad = self.ankle_angle

		# Calculate the position of the ankle (end of the thigh)
		ankle_pos = (
			int(self.base_pos[0] + THIGH_LENGTH * math.cos(hip_rad)),
			int(self.base_pos[1] + THIGH_LENGTH * math.sin(hip_rad))
		)

		# For simplicity, assume the ankle_angle is relative to horizontal.
		# Calculate the foot position (end of the shank)
		foot_pos = (
			int(ankle_pos[0] + SHANK_LENGTH * math.cos(ankle_rad + hip_rad)),
			int(ankle_pos[1] + SHANK_LENGTH * math.sin(ankle_rad + hip_rad))
		)

		# Draw thigh
		pygame.draw.line(surface, (255, 0, 0), self.base_pos, ankle_pos, 5)
		# Draw shank
		pygame.draw.line(surface, (0, 0, 255), ankle_pos, foot_pos, 5)

		# Draw joints for visualization
		pygame.draw.circle(surface, (0, 255, 0), self.base_pos, 7)  # hip
		pygame.draw.circle(surface, (0, 255, 0), ankle_pos, 7)  # ankle


def main():

	desired_positions = []
	for i in range(30):
		desired_positions.append([17, i / 1.5 - 10])
	for i in range(30, 0, -1):
		desired_positions.append([17, i / 1.5 - 10])
	# for i in range(30, 0, -1):
	# 	desired_positions.append()
	controller = LegControl()
	pygame.init()
	screen = pygame.display.set_mode((640, 480))
	pygame.display.set_caption("Leg Simulation")
	clock = pygame.time.Clock()

	# Create a leg instance with the hip at the center of the window
	leg = Leg(base_pos=(320, 240))

	running = True
	cur_t = time.time()
	controller.velocity = 0.5
	pos = 0
	pos_update_time = 0.01
	last_pos_update_time = time.time()
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			# Example: change angles when a key is pressed (for demonstration)
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_UP:
					leg.set_angles(leg.hip_angle + 5, leg.ankle_angle + 5)
				elif event.key == pygame.K_DOWN:
					leg.set_angles(leg.hip_angle - 5, leg.ankle_angle - 5)
		if time.time() - last_pos_update_time >= pos_update_time:
			last_pos_update_time = time.time()
			pos += 1
			if pos >= len(desired_positions):
				pos = 0
		controller.go_to_position(*desired_positions[pos])
		print(controller.thigh_angle / math.pi * 180, controller.knee / math.pi * 180)
		leg.set_angles(*controller.get_angles())
		cur_t = time.time()
		screen.fill((255, 255, 255))
		leg.draw(screen)
		pygame.display.flip()
		clock.tick(30)

	pygame.quit()


if __name__ == "__main__":
	main()
