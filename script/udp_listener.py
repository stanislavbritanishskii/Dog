import socket
import struct
import threading
import time
from typing import Optional
from control_struct import *


class UDPControlListener:
	def __init__(self, host: str = "0.0.0.127", port: int = 9999, recv_timeout_s: float = 0.1):
		self._host = host
		self._port = port
		self._recv_timeout_s = recv_timeout_s

		self._sock: Optional[socket.socket] = None
		self._thread: Optional[threading.Thread] = None
		self._stop_evt = threading.Event()
		self._lock = threading.Lock()

		self._expected_len = ControlData().get_size()
		self._last_data = ControlData()  # member object updated in place
		self._last_rx_ns: Optional[int] = None

	def start(self) -> None:
		if self.is_running():
			return
		self._stop_evt.clear()
		self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		try:
			self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		except OSError:
			pass
		self._sock.bind((self._host, self._port))
		self._sock.settimeout(self._recv_timeout_s)

		self._thread = threading.Thread(target=self._run, name="UDPControlListener", daemon=True)
		self._thread.start()

	def stop(self) -> None:
		self._stop_evt.set()
		if self._thread is not None:
			self._thread.join(timeout=2.0)
			self._thread = None
		if self._sock is not None:
			try:
				self._sock.close()
			finally:
				self._sock = None

	def is_running(self) -> bool:
		return self._thread is not None and self._thread.is_alive()

	def get_last_received_data(self) -> ControlData:
		# Returns the member object (do not replace it, just return the reference)
		with self._lock:
			return self._last_data

	def get_time_since_last_receive(self) -> float:
		with self._lock:
			if self._last_rx_ns is None:
				return float("inf")
			dt_ns = time.monotonic_ns() - self._last_rx_ns
		return dt_ns / 1e9

	def _run(self) -> None:
		s = self._sock
		if s is None:
			return

		bufsize = max(2048, self._expected_len)
		while not self._stop_evt.is_set():
			try:
				data, _ = s.recvfrom(bufsize)
			except socket.timeout:
				continue
			except OSError:
				# Socket closed or other fatal error: exit loop
				break

			if len(data) < self._expected_len:
				# Incomplete packet: ignore
				continue

			# Truncate any extra padding
			packet = data[:self._expected_len]

			try:
				# Update the member ControlData in place
				with self._lock:
					self._last_data.from_struct(packet)
					self._last_rx_ns = time.monotonic_ns()
			except struct.error:
				# Malformed packet: ignore and continue
				continue


# ---------------------------
# Minimal example of usage
# ---------------------------
if __name__ == "__main__":
	# Listener that binds on all interfaces, UDP/9999
	listener = UDPControlListener(host="0.0.0.0", port=9999)
	listener.start()

	try:
		while True:
			time.sleep(0.5)
			cd = listener.get_last_received_data()
			elapsed = listener.get_time_since_last_receive()
			if elapsed != float("inf"):
				print(f"last: fwd={cd.forward} right={cd.right} rot={cd.rotation} delay_ms={cd.delay_ms} steps={cd.step_count} | age={elapsed:.3f}s")
			else:
				print("no packets yet...")
	except KeyboardInterrupt:
		pass
	finally:
		listener.stop()
