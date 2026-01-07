import os
import pickle
import numpy as np
from deepface import DeepFace
from pathlib import Path
from config import Config

class FaceRecognizer:
    def __init__(self):
        """Initialize DeepFace for face recognition"""
        self.threshold = Config.FACE_RECOGNITION_THRESHOLD
        self.model_name = "Facenet512"  # Options: VGG-Face, Facenet, Facenet512, OpenFace, DeepFace, DeepID, ArcFace, Dlib
        self.database_path = Config.UPLOAD_FOLDER
        self.encodings_file = Config.MODELS_FOLDER / "face_encodings.pkl"
        self.face_database = self.load_face_database()

    def load_face_database(self):
        """Load pre-computed face encodings from file"""
        if self.encodings_file.exists():
            with open(self.encodings_file, 'rb') as f:
                return pickle.load(f)
        return {}

    def save_face_database(self):
        """Save face encodings to file"""
        with open(self.encodings_file, 'wb') as f:
            pickle.dump(self.face_database, f)

    def enroll_face(self, student_id, face_image_path):
        """
        Enroll a new face to the database

        Args:
            student_id: Student ID
            face_image_path: Path to the face image

        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate face embedding using DeepFace
            embedding_objs = DeepFace.represent(
                img_path=str(face_image_path),
                model_name=self.model_name,
                enforce_detection=True
            )

            if embedding_objs:
                embedding = embedding_objs[0]["embedding"]
                self.face_database[student_id] = {
                    'embedding': embedding,
                    'image_path': str(face_image_path)
                }
                self.save_face_database()
                return True

            return False
        except Exception as e:
            print(f"Error enrolling face: {str(e)}")
            return False

    def recognize_face(self, face_image_path):
        """
        Recognize a face from the database

        Args:
            face_image_path: Path to the face image to recognize

        Returns:
            Tuple of (student_id, confidence) or (None, 0) if not recognized
        """
        try:
            # Generate embedding for the input face
            embedding_objs = DeepFace.represent(
                img_path=str(face_image_path),
                model_name=self.model_name,
                enforce_detection=False
            )

            if not embedding_objs:
                return None, 0

            input_embedding = np.array(embedding_objs[0]["embedding"])

            # Compare with all enrolled faces
            best_match = None
            best_distance = float('inf')

            for student_id, data in self.face_database.items():
                stored_embedding = np.array(data['embedding'])

                # Calculate cosine distance
                distance = self._cosine_distance(input_embedding, stored_embedding)

                if distance < best_distance:
                    best_distance = distance
                    best_match = student_id

            # Check if best match is below threshold
            if best_match and best_distance < self.threshold:
                confidence = 1 - best_distance  # Convert distance to confidence
                return best_match, confidence

            return None, 0

        except Exception as e:
            print(f"Error recognizing face: {str(e)}")
            return None, 0

    def _cosine_distance(self, vec1, vec2):
        """Calculate cosine distance between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 1.0

        cosine_similarity = dot_product / (norm1 * norm2)
        cosine_distance = 1 - cosine_similarity

        return cosine_distance

    def delete_face(self, student_id):
        """
        Remove a face from the database

        Args:
            student_id: Student ID to remove

        Returns:
            True if successful, False otherwise
        """
        if student_id in self.face_database:
            del self.face_database[student_id]
            self.save_face_database()
            return True
        return False
