import cv2
import numpy as np


def process_frame(frame_bytes):
	# frame_bytes is a JPEG image in bytes
	# Example: decode → modify → re-encode
	arr = np.frombuffer(frame_bytes, dtype=np.uint8)
	img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
	# ---- do something with img ----
	# Example: grayscale
	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	# --------------------------------
	_, new_jpeg = cv2.imencode(".jpg", img)
	return new_jpeg.tobytes()
