import cv2
import numpy as np
from config import Config


class FaceDetector:
    def __init__(self):
        """Initialize OpenCV DNN face detector (more accurate than Haar cascade)"""
        # Try OpenCV's DNN face detector first (shipped with OpenCV 4.x)
        self.detector = None
        try:
            self.detector = cv2.FaceDetectorYN.create(
                "", "", (320, 320), 0.5, 0.3, 5000
            )
        except Exception:
            pass

        # Fallback to Haar cascade (always available)
        if self.detector is None:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.cascade = cv2.CascadeClassifier(cascade_path)
            self.use_cascade = True
            print("Using Haar cascade face detector")
        else:
            self.cascade = None
            self.use_cascade = True  # DNN detector needs model file, fall back to cascade
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.cascade = cv2.CascadeClassifier(cascade_path)
            print("Using Haar cascade face detector")

        self.confidence_threshold = Config.CONFIDENCE_THRESHOLD

    def detect_faces(self, frame):
        """
        Detect faces in a frame using OpenCV Haar cascade.

        Args:
            frame: OpenCV image/frame

        Returns:
            List of face bounding boxes [(x1, y1, x2, y2), ...]
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        detections = self.cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(60, 60),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        faces = []
        for (x, y, w, h) in detections:
            faces.append((x, y, x + w, y + h))

        return faces

    def extract_face(self, frame, bbox, padding=0.25):
        """
        Extract face region from frame with padding for better recognition.

        Args:
            frame: OpenCV image/frame
            bbox: Bounding box tuple (x1, y1, x2, y2)
            padding: Fraction of bbox size to add as padding

        Returns:
            Cropped face image
        """
        x1, y1, x2, y2 = bbox
        h = y2 - y1
        w = x2 - x1

        # Add padding around the face for better recognition
        pad_x = int(w * padding)
        pad_y = int(h * padding)
        x1 = max(0, x1 - pad_x)
        y1 = max(0, y1 - pad_y)
        x2 = min(frame.shape[1], x2 + pad_x)
        y2 = min(frame.shape[0], y2 + pad_y)

        face = frame[y1:y2, x1:x2]
        return face

    def draw_faces(self, frame, faces, labels=None):
        """
        Draw bounding boxes on detected faces

        Args:
            frame: OpenCV image/frame
            faces: List of bounding boxes
            labels: Optional list of labels for each face

        Returns:
            Frame with drawn bounding boxes
        """
        for i, (x1, y1, x2, y2) in enumerate(faces):
            # Draw rectangle
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Draw label if provided
            if labels and i < len(labels):
                label = labels[i]
                cv2.putText(frame, label, (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        return frame
