#!/usr/bin/env python3
import cv2
import numpy as np

CAM_ID	= 0
MARKER_LENGTH_M	= 0.046	# edge length in meters
camera_matrix	= np.array([[800.0, 0.0, 640.0],
							[0.0, 800.0, 360.0],
							[0.0, 0.0, 1.0]], dtype=np.float32)
dist_coeffs	= np.zeros((5, 1), dtype=np.float32)

def main():
	aruco_dict	= cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)

	params	= cv2.aruco.DetectorParameters()
	params.cornerRefinementMethod	= cv2.aruco.CORNER_REFINE_SUBPIX
	params.adaptiveThreshWinSizeMin	= 3
	params.adaptiveThreshWinSizeMax	= 23
	params.adaptiveThreshWinSizeStep	= 10

	detector	= cv2.aruco.ArucoDetector(aruco_dict, params)

	cap	= cv2.VideoCapture(CAM_ID)
	if not cap.isOpened():
		raise RuntimeError("Camera open failed")

	# Define marker 3D coordinates in its local frame (center = origin)
	obj_points	= np.array([
		[-MARKER_LENGTH_M / 2,  MARKER_LENGTH_M / 2, 0],
		[ MARKER_LENGTH_M / 2,  MARKER_LENGTH_M / 2, 0],
		[ MARKER_LENGTH_M / 2, -MARKER_LENGTH_M / 2, 0],
		[-MARKER_LENGTH_M / 2, -MARKER_LENGTH_M / 2, 0]
	], dtype=np.float32)

	while True:
		ret, frame	= cap.read()
		if not ret:
			break

		corners, ids, _	= detector.detectMarkers(frame)

		if ids is not None and len(ids) > 0:
			cv2.aruco.drawDetectedMarkers(frame, corners, ids)

			for i in range(len(ids)):
				img_points	= corners[i][0].astype(np.float32)
				success, rvec, tvec	= cv2.solvePnP(
					obj_points, img_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_IPPE_SQUARE
				)
				if not success:
					continue

				cv2.drawFrameAxes(frame, camera_matrix, dist_coeffs, rvec, tvec, MARKER_LENGTH_M * 0.5)

				t	= tvec.reshape(3)
				dist_m	= float(np.linalg.norm(t))
				cv2.putText(frame, f"id {int(ids[i])} d={dist_m:.3f} m",
							tuple(np.round(img_points[0]).astype(int)),
							cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

		cv2.imshow("aruco", frame)
		key	= cv2.waitKey(1) & 0xFF
		if key == 27 or key == ord('q'):
			break

	cap.release()
	cv2.destroyAllWindows()

if __name__ == "__main__":
	main()
