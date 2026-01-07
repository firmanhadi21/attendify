import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Base directory
    BASE_DIR = Path(__file__).parent

    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'

    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'attendify_db')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')

    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=disable'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File Storage
    UPLOAD_FOLDER = BASE_DIR / 'data' / 'student_faces'
    MODELS_FOLDER = BASE_DIR / 'models'

    # Create directories if they don't exist
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    MODELS_FOLDER.mkdir(parents=True, exist_ok=True)

    # Face Detection & Recognition Settings
    YOLO_MODEL = 'yolov8n.pt'  # YOLOv8 nano model for speed
    CONFIDENCE_THRESHOLD = 0.5
    FACE_RECOGNITION_THRESHOLD = 0.6  # DeepFace similarity threshold

    # Camera Settings
    CAMERA_INDEX = int(os.getenv('CAMERA_INDEX', '0'))
    FRAME_WIDTH = 640
    FRAME_HEIGHT = 480
