import cv2
import numpy as np
import torch
from ultralytics import YOLO
from pathlib import Path
from config import Config

class FaceDetector:
    def __init__(self):
        """Initialize YOLO model for face detection"""
        model_path = Config.MODELS_FOLDER / Config.YOLO_MODEL

        # Download YOLOv8 model if not exists
        if not model_path.exists():
            print("Downloading YOLOv8 model...")

        # Fix for PyTorch 2.6+ weights_only default change
        # Temporarily patch torch.load to allow YOLO model loading
        original_torch_load = torch.load
        def patched_load(*args, **kwargs):
            kwargs.setdefault('weights_only', False)
            return original_torch_load(*args, **kwargs)

        torch.load = patched_load
        self.model = YOLO(Config.YOLO_MODEL)
        torch.load = original_torch_load  # Restore original

        self.confidence_threshold = Config.CONFIDENCE_THRESHOLD

    def detect_faces(self, frame):
        """
        Detect faces in a frame using YOLO

        Args:
            frame: OpenCV image/frame

        Returns:
            List of face bounding boxes [(x1, y1, x2, y2), ...]
        """
        # Run YOLO detection
        results = self.model(frame, verbose=False)

        faces = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Get confidence and class
                conf = float(box.conf[0])
                cls = int(box.cls[0])

                # Class 0 is 'person' in COCO dataset
                # For face detection, we'll use person detection
                # You can fine-tune YOLO for face detection specifically
                if conf >= self.confidence_threshold and cls == 0:
                    # Get bounding box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    faces.append((int(x1), int(y1), int(x2), int(y2)))

        return faces

    def extract_face(self, frame, bbox):
        """
        Extract face region from frame

        Args:
            frame: OpenCV image/frame
            bbox: Bounding box tuple (x1, y1, x2, y2)

        Returns:
            Cropped face image
        """
        x1, y1, x2, y2 = bbox
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
