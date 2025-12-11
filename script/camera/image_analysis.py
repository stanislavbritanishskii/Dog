#!/usr/bin/env python3
import cv2
import numpy as np

def process_image(frame_bytes):
	arr = np.frombuffer(frame_bytes, dtype=np.uint8)
	frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
	frame = cv2.flip(frame, 0)
	# frame = cv2.resiz1e(frame, (640, 480))
	if frame is None:
		return frame_bytes
	_, new_jpeg = cv2.imencode(".jpg", frame)
	return new_jpeg.tobytes()
