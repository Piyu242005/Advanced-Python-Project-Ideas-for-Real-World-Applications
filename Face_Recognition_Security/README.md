# 📸 Face Recognition Security System

## Purpose
Detect human faces in a video stream and verify their identity — granting or denying access based on confidence score.

## Use Case
Door access control, attendance systems, or any security application that needs real-time face-based authentication.

## Tech Used
| Library | Role |
|:---|:---|
| `OpenCV` | Live webcam capture + Haar Cascade face detection |
| `opencv-contrib-python` | LBPH face recognizer for identity matching |
| `NumPy` | Image array manipulation |

## Run
```bash
pip install -r requirements.txt

# Webcam mode (live)
python main.py

# Demo mode (no webcam needed)
python main.py --demo
```
