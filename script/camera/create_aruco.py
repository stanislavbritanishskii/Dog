#!/usr/bin/env python3
import cv2
import numpy as np
import os

OUT_DIR = "./markers"
DICT_ID = cv2.aruco.DICT_6X6_250
MARKER_IDS = [0, 1, 2, 3]
PX_PER_MARKER = 800
QUIET_ZONE_RATIO = 0.25  # white border ratio relative to marker size


def save_markers():
	os.makedirs(OUT_DIR, exist_ok=True)
	aruco_dict = cv2.aruco.getPredefinedDictionary(DICT_ID)

	for mid in MARKER_IDS:
		marker = cv2.aruco.generateImageMarker(aruco_dict, int(mid), PX_PER_MARKER)

		# Add white border
		border_px = int(PX_PER_MARKER * QUIET_ZONE_RATIO)
		marker_with_border = cv2.copyMakeBorder(
			marker,
			border_px, border_px, border_px, border_px,
			cv2.BORDER_CONSTANT, value=255
		)

		cv2.imwrite(f"{OUT_DIR}/aruco_{mid}.png", marker_with_border)


def save_charuco_board():
	os.makedirs(OUT_DIR, exist_ok=True)
	SQUARES_X = 5
	SQUARES_Y = 7
	SQUARE_PX = 120
	MARKER_PX = 80
	aruco_dict = cv2.aruco.getPredefinedDictionary(DICT_ID)

	board = cv2.aruco.CharucoBoard(
		(SQUARES_X, SQUARES_Y),
		1.0,
		MARKER_PX / SQUARE_PX,
		aruco_dict
	)

	board_img = board.generateImage(
		(SQUARES_X * SQUARE_PX, SQUARES_Y * SQUARE_PX),
		marginSize=int(SQUARE_PX * 0.25),  # white border
		borderBits=1
	)
	cv2.imwrite(f"{OUT_DIR}/charuco_board.png", board_img)


def main():
	save_markers()
	save_charuco_board()
	print("Markers and board saved to", OUT_DIR)


if __name__ == "__main__":
	main()
