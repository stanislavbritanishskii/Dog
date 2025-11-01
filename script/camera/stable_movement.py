import cv2
import numpy as np
import time

# === Image processing loop ===
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


def capture_loop(picam2, output, scale, size_of_interest, size_too_big):
	object_detector = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=30)

	while True:
		frame = picam2.capture_array()
		mask = object_detector.apply(resize_image(frame, 1 / scale))
		_, mask = cv2.threshold(mask, 120, 255, cv2.THRESH_BINARY)
		kernel = np.ones((6, 6), np.uint8)
		mask = cv2.dilate(mask, kernel, iterations=2)
		contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

		rects = []
		for cnt in contours:
			area = cv2.contourArea(cnt)
			if size_of_interest / (scale ** 2) < area < size_too_big / (scale ** 2):
				cnt = (cnt * scale).astype(int)
				cv2.drawContours(frame, [cnt], -1, (0, 255, 0), 2)
				x, y, w, h = cv2.boundingRect(cnt)
				rects.append((x, y, w, h))

		rects = merge_rects(rects, proximity=10)

		for (x, y, w, h) in rects:
			cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

		cv2.putText(frame, time.ctime(), (20, 40),
					cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)

		ret, jpeg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
		if not ret:
			continue
		output.write(jpeg.tobytes())


def capture_loop2(picam2, output, scale, size_of_interest, size_too_big):
	object_detector = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=30)

	while True:
		frame = picam2.capture_array()

		# frame_copy = cv2.cvtColor( resize_image(frame, 1 / scale), cv2.COLOR_RGB2GRAY)
		frame_copy = frame[:, :, 0]
		contours, _ = cv2.findContours(frame_copy, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		rects = []
		for cnt in contours:
			area = cv2.contourArea(cnt)
			if size_of_interest / (scale ** 2) < area < size_too_big / (scale ** 2):
				cnt = (cnt * scale).astype(int)
				cv2.drawContours(frame, [cnt], -1, (0, 255, 0), 2)
				x, y, w, h = cv2.boundingRect(cnt)
				rects.append((x, y, w, h))

		rects = merge_rects(rects, proximity=10)

		for (x, y, w, h) in rects:
			cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

		cv2.putText(frame, time.ctime(), (20, 40),
					cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)

		ret, jpeg = cv2.imencode('.jpg', frame_copy, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
		if not ret:
			continue
		output.write(jpeg.tobytes())