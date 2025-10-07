#!/usr/bin/env python3

import io
import threading
import time
import logging
import asyncio
import socketserver
from http import server
import websockets
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
import json
import overal_controller
from controller import Controller

# === Configuration ===
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
HTTP_PORT = 8000
WS_PORT = 8765

# === Shared joystick state ===
joystick_state = {
	"joy1": {"x": 0.0, "y": 0.0},
	"joy2": {"x": 0.0, "y": 0.0},
	"joy3": {"x": 0.0, "y": 0.0},
	"keyboard": {"x": 0, "y": 0}
}
joystick_lock = threading.Lock()

# === MJPEG output handler for streaming ===
class StreamingOutput(io.BufferedIOBase):
	def __init__(self):
		self.frame = None
		self.condition = threading.Condition()

	def write(self, buf):
		with self.condition:
			self.frame = buf
			self.condition.notify_all()

# === HTTP server for index.html and MJPEG ===
class MJPEGHandler(server.BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path in ('/', '/index.html'):
			try:
				with open("static/index.html", "rb") as f:
					content = f.read()
				self.send_response(200)
				self.send_header('Content-Type', 'text/html')
				self.send_header('Content-Length', len(content))
				self.end_headers()
				self.wfile.write(content)
			except Exception as e:
				self.send_error(500, f"Error loading index.html: {e}")
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
				logging.warning(f"Client disconnected: {e}")
		else:
			self.send_error(404)
			self.end_headers()

class ThreadedHTTPServer(socketserver.ThreadingMixIn, server.HTTPServer):
	allow_reuse_address = True
	daemon_threads = True

# === WebSocket handler (receives joystick data) ===
async def ws_handler(websocket):
	try:
		while True:
			data = await websocket.recv()
			update_joystick_state(data)
	except Exception as e:
		logging.warning(f"WebSocket closed: {e}")

# === Update joystick values into shared dictionary ===
def update_joystick_state(json_data):
	try:
		data = json.loads(json_data)
		with joystick_lock:
			joystick_state["joy1"] = data.get("joy1", {"x": 0, "y": 0})
			joystick_state["joy2"] = data.get("joy2", {"x": 0, "y": 0})
			joystick_state["joy3"] = data.get("joy3", {"x": 0, "y": 0})
			joystick_state["keyboard"] = data.get("keyboard", {"x": 0, "y": 0})
	except Exception as e:
		logging.warning(f"Failed to parse joystick data: {e}")

# === Dummy background thread that reacts to joystick input ===
class DummyBackgroundThread(threading.Thread):
	def __init__(self):
		super().__init__(daemon=True)
		self.Controller = overal_controller.OveralController()

	def run(self):
		while True:
			# time.sleep(1.0 / 30.0)  # ~30Hz
			with joystick_lock:
				js = joystick_state.copy()
			# Replace with actual control logic here
			self.Controller.iterate(-js['joy1']['y'], js['joy1']['x'], js['joy2']['x'], js['joy3']['x'], js['joy3']['y'])
			# print(f"[Dummy] joy1: {js['joy1']} joy2: {js['joy2']} joy3: {js['joy3']} keyboard: {js['keyboard']}")

# === Camera setup ===
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (FRAME_WIDTH, FRAME_HEIGHT)}))
output = StreamingOutput()
picam2.start_recording(JpegEncoder(), FileOutput(output))

# === HTTP server startup ===
http_server = ThreadedHTTPServer(('', HTTP_PORT), MJPEGHandler)
http_thread = threading.Thread(target=http_server.serve_forever, daemon=True)
http_thread.start()
print(f"[HTTP] MJPEG stream available at http://<this-ip>:{HTTP_PORT}")

# === Background process startup ===
dummy_thread = DummyBackgroundThread()
dummy_thread.start()

# === WebSocket server startup ===
async def main_async():
	print(f"[WebSocket] Listening on ws://<this-ip>:{WS_PORT}/ (no path restriction)")
	async with websockets.serve(ws_handler, "", WS_PORT):
		await asyncio.Future()  # keep alive

try:
	asyncio.run(main_async())
finally:
	picam2.stop_recording()
