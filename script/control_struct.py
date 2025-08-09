import struct
from typing import List
from ctypes import (
	c_int8 as int8_t,
	c_uint8 as uint8_t,
	c_int16 as int16_t,
	c_uint16 as uint16_t,
	c_int32 as int32_t,
	c_uint32 as uint32_t,
	c_int64 as int64_t,
	c_uint64 as uint64_t,
	c_char as char,
	c_wchar as wchar_t,
	c_float as float_t,
	c_double as double_t
)


class ControlData:
	def __init__(self):

		self.forward: int = 0
		self.right: int = 0
		self.rotation: int = 0
		self.delay_ms: int = 0
		self.step_count: int = 0

	def to_struct(self):
		res = bytes()
		res += struct.pack("i", self.forward)
		res += struct.pack("i", self.right)
		res += struct.pack("i", self.rotation)
		res += struct.pack("i", self.delay_ms)
		res += struct.pack("i", self.step_count)
		return res

	def from_struct(self, binary, parsed=False):
		if not parsed:
			format_string = self.get_format_string()
			unpacked = struct.unpack(format_string, binary)
		else:
			unpacked = binary
		pos = 0

		self.forward = unpacked[pos]
		pos += 1
		self.right = unpacked[pos]
		pos += 1
		self.rotation = unpacked[pos]
		pos += 1
		self.delay_ms = unpacked[pos]
		pos += 1
		self.step_count = unpacked[pos]
		pos += 1
		return pos

	def get_size(self):
		format_string = self.get_format_string()
		return struct.calcsize(format_string)

	def get_format_string(self, secondary_call=False):

		format_string = ""
		format_string += 'i'  # forward
		format_string += 'i'  # right
		format_string += 'i'  # rotation
		format_string += 'i'  # delay_ms
		format_string += 'i'  # step_count
		format_string = '<' * (not secondary_call) + format_string
		return format_string
