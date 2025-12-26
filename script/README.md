# RoboDog

**For full details, build logs, wiring, configuration and assembly instructions, please see the Hackaday project page (this README is intentionally short):**  
https://hackaday.io/project/204567-robodog

---

## Demo videos

Replace these with your real links:

- Walking demo (forward / backward / sideways):  
  https://youtu.be/MLuDF5ifEoA

- Early leg prototypes and failures:  
  https://youtube.com/shorts/vF31sKLDyQc?feature=share

  https://youtube.com/shorts/1dqmzk7I934?feature=share

  https://youtube.com/shorts/uwMsMRV7uRQ?feature=share

---

## Overview

Low-budget 3D-printed dog with 14 degrees of freedom:

- 12 DOF in the legs (3 per leg)  
- 2 DOF camera head  
- Raspberry Pi Zero 2 W as main controller  
- PCA9685 servo driver  
- Hobby servos only, no custom PCBs  
- Powered from two 18650 cells with separate step-up converters for Pi and servos

Main features:

- Walks forward, backward, sideways and diagonally  
- Can rotate in place  
- 2-axis camera with wide-angle 8 MP module  
- Web frontend with video stream and joysticks for control

This is not a polished commercial robot, more like a cheap experimental platform that somehow survived many redesigns.

---

## Hardware (very short summary)

- **Brain:** Raspberry Pi Zero 2 W  
- **Servo controller:** PCA9685  
- **Servos (legs):** mostly MG90S / TS90MD style metal gear hobby servos  
- **Servos (head):** 9 g Miuzei servos  
- **Camera:** Freenove 120° 8 MP  
- **Power:**  
  - 2× 18650 cells  
  - 2× step-up converters (one for Pi, one for servos)  
- **Mechanics:**  
  - Modeled in FreeCAD  
  - Printed on an Anycubic Kobra 3 (but any decent FDM printer should work)

Wiring, power explanations and mechanical notes are all documented in the Hackaday logs.

---

## Software

- Runs on the Pi in Python  
- Uses PCA9685 for servo PWM  
- Main controller script for gait and head control  
- `settings.json` for:
  - servo channels and offsets  
  - joint limits  
  - link lengths  
  - speed limits and gait timing  
- Simple web UI (video + joysticks) for remote control

Exact scripts, config format and zeroing procedure are described on Hackaday.

---

## License

MIT License – see the [`LICENSE`](LICENSE) file for details.
