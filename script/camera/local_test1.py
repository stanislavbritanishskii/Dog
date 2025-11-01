#!/usr/bin/env python3
# Tabs are used consistently

import cv2
import numpy as np

# === Camera setup ===
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
	print("Error: Cannot open camera")
	exit(1)

print("Press 'q' to quit")

while True:
	ret, frame = cap.read()
	if not ret:
		break

	# --- Mirror image for natural control view ---
	frame = cv2.flip(frame, 1)

	# --- Convert to grayscale ---
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

	# --- Normalize lighting and improve contrast ---
	gray = cv2.equalizeHist(gray)

	# --- Mild denoise while preserving edges ---
	gray = cv2.bilateralFilter(gray, d=7, sigmaColor=50, sigmaSpace=50)

	# --- Compute gradient magnitude with Sobel ---
	grad_x = cv2.Sobel(gray, cv2.CV_16S, 1, 0, ksize=3)
	grad_y = cv2.Sobel(gray, cv2.CV_16S, 0, 1, ksize=3)
	grad_mag = cv2.convertScaleAbs(cv2.magnitude(grad_x.astype(np.float32), grad_y.astype(np.float32)))

	# --- Sharpen the image using gradient information ---
	sharp = cv2.addWeighted(gray, 1.5, grad_mag, -0.5, 0)

	# --- Canny edge detection (sensitive but stable) ---
	edges = cv2.Canny(sharp, 10, 80, apertureSize=3, L2gradient=True)

	# --- Morphological clean-up ---
	kernel = np.ones((3, 3), np.uint8)
	edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=1)
	edges = cv2.morphologyEx(edges, cv2.MORPH_OPEN, kernel, iterations=1)

	# --- Optional: thin edges for precision ---
	edges_thin = cv2.ximgproc.thinning(edges) if hasattr(cv2, "ximgproc") else edges

	# --- Overlay edges on the original frame for visualization ---
	display = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
	display[edges_thin > 0] = (0, 255, 0)

	cv2.putText(display, "Stable Edge Extractor", (10, 25),
				cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

	cv2.imshow("Edges", edges_thin)
	cv2.imshow("Overlay", display)

	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

cap.release()
cv2.destroyAllWindows()
