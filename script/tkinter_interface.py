import socket
import struct
import time
import tkinter as tk


# =========================
# ======= CONFIG ==========
# =========================
TARGET_IP = "192.168.0.117"
TARGET_PORT = 9998

SEND_HZ = 60.0					# transmit rate (Hz)
DEADZONE = 0.05					# joystick deadzone (0..1), 0.05 = 5%

# ----- Per-axis output limits (int32) -----
# Joystick left: forward (from Y, inverted so Up=positive), right (from X)
going_limit = 35
FORWARD_MIN, FORWARD_MAX = -going_limit, going_limit
RIGHT_MIN,   RIGHT_MAX   = -going_limit // 3, going_limit // 3

# Joystick right: rotation (from X only)
ROTATION_MIN, ROTATION_MAX = -5, 5

# ----- Sliders (int32) -----
DELAY_MS_MIN, DELAY_MS_MAX = 0, 200
STEPS_MIN,    STEPS_MAX    = 0, 10

# UI visual sizes (not limits)
JOYSTICK_SIZE = 200
KNOB_RADIUS = 18
# =========================


class ControlData:
	def __init__(self):
		self.forward = 0
		self.right = 0
		self.rotation = 0
		self.delay_ms = 0
		self.step_count = 0

	def pack(self):
#		little-endian 5x int32
#		forward, right, rotation, delay_ms, step_count
		return struct.pack("<iiiii", self.forward, self.right, self.rotation, self.delay_ms, self.step_count)


def clamp_int(v, lo, hi):
	if v < lo:
		return lo
	if v > hi:
		return hi
	return v


def map_norm_to_range(norm, vmin, vmax):
	# norm in [-1, 1] -> int in [vmin, vmax], linear
	if norm < -1.0:
		norm = -1.0
	elif norm > 1.0:
		norm = 1.0
	val = vmin + (norm + 1.0) * 0.5 * (vmax - vmin)
	return int(round(val))


class Joystick(tk.Canvas):
	def __init__(self, master, size=200, knob_radius=18, **kwargs):
		tk.Canvas.__init__(self, master, width=size, height=size, highlightthickness=0, **kwargs)
		self.size = size
		self.center = (size // 2, size // 2)
		self.knob_radius = knob_radius
		self.active = False
		self.norm_x = 0.0		# [-1..1], +right
		self.norm_y = 0.0		# [-1..1], +down (we invert later for forward)
		self._draw_base()
		self._draw_knob(*self.center)

		self.bind("<Button-1>", self._on_press)
		self.bind("<B1-Motion>", self._on_drag)
		self.bind("<ButtonRelease-1>", self._on_release)
		self.bind("<Leave>", self._on_release)

	def _draw_base(self):
		cx, cy = self.center
		r = self.size // 2 - 2
		self.create_oval(cx - r, cy - r, cx + r, cy + r, outline="#777", width=2)
		self.create_line(cx, 4, cx, self.size - 4, fill="#999")
		self.create_line(4, cy, self.size - 4, cy, fill="#999")

	def _draw_knob(self, x, y):
		if hasattr(self, "_knob"):
			self.delete(self._knob)
		self._knob = self.create_oval(x - self.knob_radius, y - self.knob_radius,
									  x + self.knob_radius, y + self.knob_radius,
									  fill="#ccc", outline="#555", width=2)

	def _clamp_to_circle(self, x, y):
		cx, cy = self.center
		dx = x - cx
		dy = y - cy
		max_r = self.size // 2 - self.knob_radius - 3
		dist2 = dx * dx + dy * dy
		if dist2 <= max_r * max_r:
			return x, y
		if dist2 == 0:
			return cx, cy
		dist = dist2 ** 0.5
		scale = float(max_r) / dist
		return int(cx + dx * scale), int(cy + dy * scale)

	def _update_norm_from_xy(self, x, y):
		cx, cy = self.center
		max_r = self.size // 2 - self.knob_radius - 3
		self.norm_x = (x - cx) / float(max_r)
		self.norm_y = (y - cy) / float(max_r)
		# deadzone
		if abs(self.norm_x) < DEADZONE:
			self.norm_x = 0.0
		if abs(self.norm_y) < DEADZONE:
			self.norm_y = 0.0
		# clamp
		if self.norm_x < -1.0:
			self.norm_x = -1.0
		if self.norm_x > 1.0:
			self.norm_x = 1.0
		if self.norm_y < -1.0:
			self.norm_y = -1.0
		if self.norm_y > 1.0:
			self.norm_y = 1.0

	def _on_press(self, event):
		self.active = True
		x, y = self._clamp_to_circle(event.x, event.y)
		self._draw_knob(x, y)
		self._update_norm_from_xy(x, y)

	def _on_drag(self, event):
		if not self.active:
			return
		x, y = self._clamp_to_circle(event.x, event.y)
		self._draw_knob(x, y)
		self._update_norm_from_xy(x, y)

	def _on_release(self, event=None):
		self.active = False
		self.set_norm_xy(0.0, 0.0)

	def set_norm_xy(self, nx, ny):
		# external setter (keyboard)
		if nx < -1.0: nx = -1.0
		if nx > 1.0: nx = 1.0
		if ny < -1.0: ny = -1.0
		if ny > 1.0: ny = 1.0
		self.norm_x = float(nx)
		self.norm_y = float(ny)

		cx, cy = self.center
		max_r = self.size // 2 - self.knob_radius - 3
		x = int(cx + self.norm_x * max_r)
		y = int(cy + self.norm_y * max_r)
		self._draw_knob(x, y)

	def get_norm_xy(self):
		return self.norm_x, self.norm_y


class App:
	def __init__(self, root):
		self.root = root
		self.root.title("UDP Control Joysticks (mouse + keyboard, configurable limits)")
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.setblocking(False)

		self.control = ControlData()

		# Layout
		container = tk.Frame(root)
		container.pack(padx=10, pady=10)

		# Left joystick: forward (Y), right (X)
		left_frame = tk.Frame(container)
		left_frame.grid(row=0, column=0, padx=10, pady=10)
		tk.Label(left_frame, text="Forward / Right (WASD)").pack()
		self.j_left = Joystick(left_frame, size=JOYSTICK_SIZE, knob_radius=KNOB_RADIUS, bg="#f4f4f4")
		self.j_left.pack()

		# Right joystick: rotation (X)
		right_frame = tk.Frame(container)
		right_frame.grid(row=0, column=1, padx=10, pady=10)
		tk.Label(right_frame, text="Rotation (← →)").pack()
		self.j_right = Joystick(right_frame, size=JOYSTICK_SIZE, knob_radius=KNOB_RADIUS, bg="#f4f4f4")
		self.j_right.pack()

		# Sliders
		sliders = tk.Frame(container)
		sliders.grid(row=0, column=2, padx=10, pady=10, sticky="ns")

		tk.Label(sliders, text=f"delay_ms [{DELAY_MS_MIN}..{DELAY_MS_MAX}]").pack(anchor="w")
		self.delay_scale = tk.Scale(sliders, from_=DELAY_MS_MIN, to=DELAY_MS_MAX, orient=tk.HORIZONTAL, length=220)
		self.delay_scale.set(DELAY_MS_MIN)
		self.delay_scale.pack(pady=(0, 12))

		tk.Label(sliders, text=f"step_count [{STEPS_MIN}..{STEPS_MAX}]").pack(anchor="w")
		self.steps_scale = tk.Scale(sliders, from_=STEPS_MIN, to=STEPS_MAX, orient=tk.HORIZONTAL, length=220)
		self.steps_scale.set(STEPS_MIN)
		self.steps_scale.pack(pady=(0, 12))

		# Status
		self.status_var = tk.StringVar(value="idle")
		tk.Label(root, textvariable=self.status_var).pack(pady=(6, 0))

		# ---------- Keyboard control state ----------
		self.left_keys = set()		# tracks 'w','a','s','d'
		self.right_keys = set()		# tracks 'Left','Right'
		self.keyboard_left_active = False
		self.keyboard_right_active = False

		# Focus bindings (catch keys anywhere)
		self.root.bind("<KeyPress>", self._on_key_press)
		self.root.bind("<KeyRelease>", self._on_key_release)
		self.root.bind("<space>", self._on_space)	# SPACE to center joysticks
		self.root.after(50, lambda: self.root.focus_set())

		self.period_ms = int(1000.0 / SEND_HZ)
		self._schedule_tick()

	def _schedule_tick(self):
		self._tick()
		self.root.after(self.period_ms, self._schedule_tick)

	# ---------- Keyboard handling ----------
	def _on_key_press(self, event):
		k = event.keysym
		if k in ("w", "W", "a", "A", "s", "S", "d", "D"):
			self._track_left_key(k.lower(), pressed=True)
		elif k in ("Left", "Right"):
			self._track_right_key(k, pressed=True)

	def _on_key_release(self, event):
		k = event.keysym
		if k in ("w", "W", "a", "A", "s", "S", "d", "D"):
			self._track_left_key(k.lower(), pressed=False)
		elif k in ("Left", "Right"):
			self._track_right_key(k, pressed=False)

	def _on_space(self, _event):
		# Center both joysticks and clear key states so they stay centered
		self.left_keys.clear()
		self.right_keys.clear()
		self.j_left.set_norm_xy(0.0, 0.0)
		self.j_right.set_norm_xy(0.0, 0.0)
		self.status_var.set("centered by SPACE")

	def _track_left_key(self, k, pressed):
		if pressed:
			self.left_keys.add(k)
		else:
			if k in self.left_keys:
				self.left_keys.remove(k)
		self._update_left_from_keys()

	def _track_right_key(self, k, pressed):
		if pressed:
			self.right_keys.add(k)
		else:
			if k in self.right_keys:
				self.right_keys.remove(k)
		self._update_right_from_keys()

	def _update_left_from_keys(self):
		# Compute normalized vector from WASD (diagonals allowed)
		nx = 0
		ny = 0
		if "a" in self.left_keys:
			nx -= 1
		if "d" in self.left_keys:
			nx += 1
		if "w" in self.left_keys:
			ny -= 1		# up on screen is negative y (we invert later for forward)
		if "s" in self.left_keys:
			ny += 1
		self.keyboard_left_active = (nx != 0 or ny != 0)
		if self.keyboard_left_active:
			if nx != 0 and ny != 0:
				nx *= 0.70710678
				ny *= 0.70710678
			self.j_left.set_norm_xy(nx, ny)

	def _update_right_from_keys(self):
		# Only X from arrows; Y ignored
		nx = 0
		if "Left" in self.right_keys:
			nx -= 1
		if "Right" in self.right_keys:
			nx += 1
		self.keyboard_right_active = (nx != 0)
		if self.keyboard_right_active:
			self.j_right.set_norm_xy(nx, 0.0)

	# ---------- Periodic read + send ----------
	def _tick(self):
		# Read joysticks
		lx, ly = self.j_left.get_norm_xy()
		rx, _ = self.j_right.get_norm_xy()

		# Map to configured ranges
		forward_norm = -ly						# invert Y so Up=positive forward
		right_norm = lx
		rotation_norm = rx

		forward = map_norm_to_range(forward_norm, FORWARD_MIN, FORWARD_MAX)
		right   = map_norm_to_range(right_norm,   RIGHT_MIN,   RIGHT_MAX)
		rotation= map_norm_to_range(rotation_norm, ROTATION_MIN, ROTATION_MAX)

		# Clamp just in case
		forward = clamp_int(forward, FORWARD_MIN, FORWARD_MAX)
		right   = clamp_int(right,   RIGHT_MIN,   RIGHT_MAX)
		rotation= clamp_int(rotation, ROTATION_MIN, ROTATION_MAX)

		delay_ms = int(self.delay_scale.get())
		step_count = int(self.steps_scale.get())

		self.control.forward = forward
		self.control.right = right
		self.control.rotation = rotation
		self.control.delay_ms = delay_ms
		self.control.step_count = step_count

		packet = self.control.pack()
		try:
			self.sock.sendto(packet, (TARGET_IP, TARGET_PORT))
			self.status_var.set(
				f"sent → fwd={forward} right={right} rot={rotation} delay_ms={delay_ms} steps={step_count} @ {time.strftime('%H:%M:%S')}"
			)
		except Exception as e:
			self.status_var.set(f"send error: {e}")

	def close(self):
		try:
			self.sock.close()
		except Exception:
			pass


if __name__ == "__main__":
	root = tk.Tk()
	app = App(root)
	try:
		root.mainloop()
	finally:
		app.close()
