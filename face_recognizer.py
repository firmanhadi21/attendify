import os
import pickle
import numpy as np
from deepface import DeepFace
from pathlib import Path
from config import Config
import cv2

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
    
    def _preprocess_image(self, image_path):
        """
        Preprocess image to improve recognition in varying conditions
        
        Args:
            image_path: Path to image
            
        Returns:
            Preprocessed image path
        """
        try:
            img = cv2.imread(str(image_path))
            if img is None:
                return image_path
            
            # Convert to LAB color space
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to L channel
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            
            # Merge channels and convert back to BGR
            enhanced = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
            
            # Save temporarily
            temp_path = str(image_path).replace('.jpg', '_enhanced.jpg')
            cv2.imwrite(temp_path, enhanced)
            
            return temp_path
        except Exception as e:
            print(f"Preprocessing warning: {str(e)}, using original image")
            return image_path

    def enroll_face(self, student_id, face_image_path, stored_image_path=None):
        """
        Enroll a new face to the database with multiple embeddings for robustness

        Args:
            student_id: Student ID
            face_image_path: Path to the face image to read
            stored_image_path: Path to record in the database, if the image will
                live somewhere else once enrollment succeeds (defaults to face_image_path)

        Returns:
            Tuple of (success, error_message). error_message is None on success.
        """
        recorded_path = str(stored_image_path or face_image_path)
        try:
            embeddings = []

            # Generate embedding from original image
            # Try multiple detector backends for better face detection
            embedding_objs = None
            working_detector = None
            for detector in ['retinaface', 'opencv', 'ssd', 'mtcnn']:
                try:
                    embedding_objs = DeepFace.represent(
                        img_path=str(face_image_path),
                        model_name=self.model_name,
                        enforce_detection=True,
                        detector_backend=detector
                    )
                    if embedding_objs:
                        working_detector = detector
                        break
                except Exception:
                    continue

            # No backend found a face. Refuse the enrollment instead of embedding
            # the whole image, which would store a meaningless vector under this
            # student and cause false matches during recognition.
            if not embedding_objs:
                print(f"Enrollment rejected for {student_id}: no face detected by any detector backend")
                return False, ('No face detected in the photo. Use a clear, well-lit, front-facing '
                               'image where the face fills a good part of the frame.')

            embeddings.append(embedding_objs[0]["embedding"])

            # Generate embedding from preprocessed image for better lighting tolerance.
            # A face is known to be present, so keep detection enforced here too and
            # just skip the enhanced variant if the detector misses it.
            enhanced_path = self._preprocess_image(face_image_path)
            if enhanced_path != face_image_path:
                try:
                    enhanced_objs = DeepFace.represent(
                        img_path=enhanced_path,
                        model_name=self.model_name,
                        enforce_detection=True,
                        detector_backend=working_detector
                    )
                    if enhanced_objs:
                        embeddings.append(enhanced_objs[0]["embedding"])
                except Exception as e:
                    print(f"CLAHE-enhanced embedding skipped for {student_id}: {str(e)}")
                finally:
                    # Clean up temp file
                    if os.path.exists(enhanced_path):
                        os.remove(enhanced_path)

            if embeddings:
                # Store multiple embeddings or average them
                if student_id in self.face_database:
                    # Append to existing embeddings
                    existing = self.face_database[student_id].get('embeddings', [self.face_database[student_id]['embedding']])
                    existing.extend(embeddings)
                    self.face_database[student_id] = {
                        'embeddings': existing,
                        'embedding': embeddings[0],  # Keep for backward compatibility
                        'image_path': recorded_path
                    }
                else:
                    self.face_database[student_id] = {
                        'embeddings': embeddings,
                        'embedding': embeddings[0],  # Primary embedding
                        'image_path': recorded_path
                    }
                self.save_face_database()
                return True, None

            return False, 'Could not generate a face embedding from the photo.'
        except Exception as e:
            print(f"Error enrolling face: {str(e)}")
            return False, f"Face enrollment failed: {str(e)}"

    def recognize_face(self, face_image_path):
        """
        Recognize a face from the database with improved tolerance for varying conditions

        Args:
            face_image_path: Path to the face image to recognize

        Returns:
            Tuple of (student_id, confidence) or (None, 0) if not recognized
        """
        try:
            input_embeddings = []

            # Try multiple detector backends to find a face
            embedding_objs = None
            for detector in ['retinaface', 'opencv', 'ssd']:
                try:
                    embedding_objs = DeepFace.represent(
                        img_path=str(face_image_path),
                        model_name=self.model_name,
                        enforce_detection=True,
                        detector_backend=detector
                    )
                    if embedding_objs:
                        break
                except Exception:
                    continue

            # Last resort: no face detection enforcement
            if not embedding_objs:
                try:
                    embedding_objs = DeepFace.represent(
                        img_path=str(face_image_path),
                        model_name=self.model_name,
                        enforce_detection=False,
                        detector_backend='opencv'
                    )
                except Exception:
                    pass

            if embedding_objs:
                input_embeddings.append(np.array(embedding_objs[0]["embedding"]))

            if not input_embeddings:
                return None, 0

            # Compare with all enrolled faces using minimum distance across all embeddings
            best_match = None
            best_distance = float('inf')

            for student_id, data in self.face_database.items():
                # Get all stored embeddings for this student
                stored_embeddings = data.get('embeddings', [data['embedding']])
                
                # Compare each input embedding with each stored embedding
                min_distance = float('inf')
                for input_emb in input_embeddings:
                    for stored_emb in stored_embeddings:
                        stored_embedding = np.array(stored_emb)
                        distance = self._cosine_distance(input_emb, stored_embedding)
                        min_distance = min(min_distance, distance)
                
                if min_distance < best_distance:
                    best_distance = min_distance
                    best_match = student_id

            # Check if best match is below threshold
            if best_match and best_distance < self.threshold:
                confidence = 1 - best_distance  # Convert distance to confidence
                print(f"Face recognition result: student_id={best_match}, confidence={confidence:.2f}, distance={best_distance:.3f}")
                return best_match, confidence

            print(f"Face recognition result: student_id=None, confidence=0, best_distance={best_distance:.3f}, threshold={self.threshold}")
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
