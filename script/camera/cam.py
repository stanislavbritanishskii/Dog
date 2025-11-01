#!/usr/bin/env python3
# Tabs are used consistently

import io
import logging
import socketserver
import time
from http import server
from threading import Condition
from picamera2 import Picamera2
from stable_movement import capture_loop2 as capture_loop


# === Camera settings ===
FRAME_WIDTH = 1280
FRAME_HEIGHT = 800

scale = 4
size_of_interest = 50
size_too_big = FRAME_WIDTH * FRAME_HEIGHT / 2


def clamp(x, lo, hi):
	return lo if x < lo else hi if x > hi else x


# === Simple HTML page for stream only ===
PAGE = f"""\
<!DOCTYPE html>
<html>
<head>
	<title>Pi5 Camera Stream</title>
	<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
	<style>
		body {{ margin:0; background:black; overflow:hidden; }}
		img {{
			max-width:100vw;
			max-height:100vh;
			width:100%;
			height:100%;
			object-fit:contain;
			display:block;
			margin:0 auto;
		}}
	</style>
</head>
<body>
	<img src="/stream.mjpg">
</body>
</html>
"""


# === MJPEG output ===
class StreamingOutput(io.BufferedIOBase):
	def __init__(self):
		self.frame = None
		self.condition = Condition()

	def write(self, buf):
		with self.condition:
			self.frame = buf
			self.condition.notify_all()


class StreamingHandler(server.BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path in ('/', '/index.html'):
			content = PAGE.encode('utf-8')
			self.send_response(200)
			self.send_header('Content-Type', 'text/html')
			self.send_header('Content-Length', len(content))
			self.end_headers()
			self.wfile.write(content)

		elif self.path == '/stream.mjpg':
			self.send_response(200)
			self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
			self.end_headers()
			try:
				while True:
					with output.condition:
						output.condition.wait()
						frame = output.frame
					self.wfile.write(b'--FRAME\r\n')
					self.send_header('Content-Type', 'image/jpeg')
					self.send_header('Content-Length', len(frame))
					self.end_headers()
					self.wfile.write(frame)
					self.wfile.write(b'\r\n')
			except Exception as e:
				logging.warning(f"Streaming client disconnected: {e}")
		else:
			self.send_error(404)
			self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
	allow_reuse_address = True
	daemon_threads = True



# === Camera setup ===
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (FRAME_WIDTH, FRAME_HEIGHT)}))
output = StreamingOutput()
picam2.start()

# Run capture loop in main thread (no async, no extra threads)
try:
	print("[HTTP] Server running at http://<this-ip>:8000")
	http_server = StreamingServer(('', 8000), StreamingHandler)

	import threading
	threading.Thread(target=capture_loop, args=(picam2, output, scale, size_of_interest, size_too_big), daemon=True).start()

	http_server.serve_forever()

finally:
	picam2.stop()
