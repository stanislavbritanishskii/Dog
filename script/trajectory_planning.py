import math

def interpolate_3d(start, end, step):
	dx = end[0] - start[0]
	dy = end[1] - start[1]
	dz = end[2] - start[2]

	distance = math.sqrt(dx*dx + dy*dy + dz*dz)
	if distance == 0.0 or step <= 0.0:
		return [list(start)]

	ux = dx / distance
	uy = dy / distance
	uz = dz / distance

	points = []
	current_step = 0.0

	while current_step < distance:
		x = start[0] + ux * current_step
		y = start[1] + uy * current_step
		z = start[2] + uz * current_step
		points.append([x, y, z])
		current_step += step

	points.append(list(end))
	return points


def interpolate_path(points, step):
	if len(points) < 2:
		return [list(points[0])] if points else []

	full_path = []

	for i in range(len(points) - 1):
		segment = interpolate_3d(points[i], points[i + 1], step)
		if i > 0:
			segment = segment[1:]  # avoid duplicating the junction
		full_path.extend(segment)

	return full_path
