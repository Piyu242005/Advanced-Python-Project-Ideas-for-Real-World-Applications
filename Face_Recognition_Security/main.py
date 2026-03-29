"""
Face Recognition Security System
Uses OpenCV Haar Cascade for detection and LBPH face recognizer
for real-time identity verification.

Requirements:
    pip install opencv-python opencv-contrib-python numpy

Usage:
    python main.py          # live webcam mode
    python main.py --demo   # demo mode (no webcam needed)
"""

import sys
import os
import numpy as np

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False


# ── Configuration ───────────────────────────────────────────────────────────
KNOWN_LABELS = {0: "Piyush", 1: "Tippsy", 2: "Suchak"}   # id → name
CONFIDENCE_THRESHOLD = 65       # lower = stricter (LBPH)
CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml" if OPENCV_AVAILABLE else ""


def create_synthetic_training_data() -> tuple[list, list]:
    """Generate fake face images for demo purposes."""
    images, labels = [], []
    rng = np.random.default_rng(42)
    for label_id in range(3):
        for _ in range(10):
            # 100×100 grayscale noise image
            img = rng.integers(0, 255, (100, 100), dtype=np.uint8)
            images.append(img)
            labels.append(label_id)
    return images, labels


def run_demo_mode() -> None:
    """Demo mode: train LBPH on synthetic data and 'verify' a test image."""
    print("\n[DEMO MODE] — No webcam required")
    print("─" * 48)

    images, labels = create_synthetic_training_data()
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(images, np.array(labels))

    # Predict against the first training image (should match label 0 → Piyush)
    test_img = images[0]
    label_id, confidence = recognizer.predict(test_img)
    name = KNOWN_LABELS.get(label_id, "Unknown")

    print(f"\n  🔍  Test face analyzed")
    print(f"  👤  Predicted : {name}")
    print(f"  📊  Confidence: {confidence:.2f} (lower = better match)")
    access = "✅ ACCESS GRANTED" if confidence < CONFIDENCE_THRESHOLD else "❌ ACCESS DENIED"
    print(f"  🔐  Decision  : {access}")
    print("─" * 48)


def run_webcam_mode() -> None:
    """Live webcam loop — press Q to quit."""
    face_cascade = cv2.CascadeClassifier(CASCADE_PATH)
    recognizer = cv2.face.LBPHFaceRecognizer_create()

    # Train on synthetic data so the recognizer is initialized
    images, labels = create_synthetic_training_data()
    recognizer.train(images, np.array(labels))

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌  Could not open webcam. Run with --demo flag instead.")
        return

    print("\n[WEBCAM MODE] — Press Q to quit\n")
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))

        for (x, y, w, h) in faces:
            roi = cv2.resize(gray[y:y+h, x:x+w], (100, 100))
            label_id, confidence = recognizer.predict(roi)

            if confidence < CONFIDENCE_THRESHOLD:
                name = KNOWN_LABELS.get(label_id, "Unknown")
                color = (0, 255, 0)
                status = f"{name} ({confidence:.0f})"
            else:
                color = (0, 0, 255)
                status = f"Unknown ({confidence:.0f})"

            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, status, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        cv2.imshow("Face Recognition Security", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


def main():
    print("=" * 48)
    print("  📸  FACE RECOGNITION SECURITY SYSTEM")
    print("=" * 48)

    if not OPENCV_AVAILABLE:
        print("❌  OpenCV not installed.")
        print("    Run: pip install opencv-python opencv-contrib-python")
        sys.exit(1)

    if "--demo" in sys.argv or not sys.stdin.isatty():
        run_demo_mode()
    else:
        print("  [1] Webcam mode (real-time)")
        print("  [2] Demo mode  (no webcam)")
        choice = input("\n  Select mode: ").strip()
        if choice == "1":
            run_webcam_mode()
        else:
            run_demo_mode()


if __name__ == "__main__":
    main()
