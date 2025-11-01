import cv2
import numpy as np


def resize_image(image, scale_factor):
	dimensions = (int(image.shape[1] * scale_factor), int(image.shape[0] * scale_factor))
	return cv2.resize(image, dimensions, interpolation=cv2.INTER_AREA)


def merge_rects(rects, proximity=30):
	merged = []
	for r in rects:
		x, y, w, h = r
		added = False
		for i, (xx, yy, ww, hh) in enumerate(merged):
			if not (x > xx + ww + proximity or xx > x + w + proximity or
					y > yy + hh + proximity or yy > y + h + proximity):
				nx = min(x, xx)
				ny = min(y, yy)
				nw = max(x + w, xx + ww) - nx
				nh = max(y + h, yy + hh) - ny
				merged[i] = (nx, ny, nw, nh)
				added = True
				break
		if not added:
			merged.append(r)
	return merged





# === Open camera ===
cap = cv2.VideoCapture(0)	# usually /dev/video0

# Optional: set resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
	print("Error: Cannot open camera")
	exit(1)

print("Press 'q' to quit")

# === threshold level (0–255) ===
THRESHOLD = 20

while True:
	ret, frame = cap.read()

	if not ret:
		print("Failed to grab frame")
		break
	frame = cv2.flip(frame, 1)
	# Split BGR channels

	b = frame[:, :, 0]
	g = frame[:, :, 1]
	r = frame[:, :, 2]

	# Upcast to avoid uint8 wrap
	r16 = r.astype('int16')
	g16 = g.astype('int16')
	b16 = b.astype('int16')

	mask_r = (r16 > g16 + THRESHOLD) & (r16 > b16 + THRESHOLD)
	mask_g = (g16 > r16 + THRESHOLD) & (g16 > b16 + THRESHOLD)
	mask_b = (b16 > r16 + THRESHOLD) & (b16 > g16 + THRESHOLD)

	mask_r = mask_r.astype('uint8') * 255
	mask_g = mask_g.astype('uint8') * 255
	mask_b = mask_b.astype('uint8') * 255

	cv2.imshow("Red Mask", mask_r)
	cv2.imshow("Green Mask", mask_g)
	cv2.imshow("Blue Mask", mask_b)

	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

cap.release()
cv2.destroyAllWindows()
