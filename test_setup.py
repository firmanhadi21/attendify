"""
Test script to verify Attendify setup
Run this to check if all components are working correctly
"""

import sys
import os

def test_imports():
    """Test if all required packages are installed"""
    print("Testing imports...")
    errors = []

    try:
        import flask
        print("  ✓ Flask installed")
    except ImportError as e:
        errors.append("Flask not installed")
        print(f"  ✗ Flask: {e}")

    try:
        import cv2
        print("  ✓ OpenCV installed")
    except ImportError as e:
        errors.append("OpenCV not installed")
        print(f"  ✗ OpenCV: {e}")

    try:
        import ultralytics
        print("  ✓ Ultralytics (YOLO) installed")
    except ImportError as e:
        errors.append("Ultralytics not installed")
        print(f"  ✗ Ultralytics: {e}")

    try:
        import deepface
        print("  ✓ DeepFace installed")
    except ImportError as e:
        errors.append("DeepFace not installed")
        print(f"  ✗ DeepFace: {e}")

    try:
        import psycopg2
        print("  ✓ PostgreSQL driver installed")
    except ImportError as e:
        errors.append("psycopg2 not installed")
        print(f"  ✗ psycopg2: {e}")

    try:
        import sqlalchemy
        print("  ✓ SQLAlchemy installed")
    except ImportError as e:
        errors.append("SQLAlchemy not installed")
        print(f"  ✗ SQLAlchemy: {e}")

    return errors

def test_directories():
    """Test if required directories exist"""
    print("\nTesting directories...")
    errors = []

    required_dirs = [
        'templates',
        'static',
        'static/css',
        'static/js',
        'data/student_faces',
        'models'
    ]

    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"  ✓ {directory} exists")
        else:
            errors.append(f"Directory {directory} not found")
            print(f"  ✗ {directory} not found")
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"    Created {directory}")
            except Exception as e:
                print(f"    Failed to create {directory}: {e}")

    return errors

def test_files():
    """Test if required files exist"""
    print("\nTesting files...")
    errors = []

    required_files = [
        'app.py',
        'config.py',
        'database.py',
        'face_detector.py',
        'face_recognizer.py',
        'requirements.txt',
        'templates/index.html',
        'static/css/style.css',
        'static/js/app.js'
    ]

    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✓ {file_path} exists")
        else:
            errors.append(f"File {file_path} not found")
            print(f"  ✗ {file_path} not found")

    return errors

def test_env():
    """Test environment configuration"""
    print("\nTesting environment configuration...")
    errors = []

    if os.path.exists('.env'):
        print("  ✓ .env file exists")
    else:
        print("  ⚠ .env file not found")
        if os.path.exists('.env.example'):
            print("    Please copy .env.example to .env and configure it")
        errors.append(".env file missing")

    return errors

def test_camera():
    """Test camera access"""
    print("\nTesting camera...")
    try:
        import cv2
        camera = cv2.VideoCapture(0)
        if camera.isOpened():
            ret, frame = camera.read()
            if ret:
                print("  ✓ Camera is accessible and working")
                camera.release()
                return []
            else:
                print("  ✗ Camera opened but cannot read frames")
                camera.release()
                return ["Camera cannot read frames"]
        else:
            print("  ✗ Cannot open camera")
            return ["Cannot open camera"]
    except Exception as e:
        print(f"  ✗ Camera test failed: {e}")
        return [f"Camera error: {e}"]

def test_database():
    """Test database connection"""
    print("\nTesting database connection...")
    try:
        from dotenv import load_dotenv
        load_dotenv()

        from config import Config
        from sqlalchemy import create_engine

        engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        connection = engine.connect()
        print("  ✓ Database connection successful")
        connection.close()
        return []
    except Exception as e:
        print(f"  ✗ Database connection failed: {e}")
        print("    Make sure PostgreSQL is running and credentials are correct in .env")
        return [f"Database error: {e}"]

def main():
    """Run all tests"""
    print("=" * 50)
    print("Attendify Setup Test")
    print("=" * 50)
    print()

    all_errors = []

    all_errors.extend(test_imports())
    all_errors.extend(test_directories())
    all_errors.extend(test_files())
    all_errors.extend(test_env())
    all_errors.extend(test_camera())
    all_errors.extend(test_database())

    print("\n" + "=" * 50)
    if not all_errors:
        print("✓ All tests passed! Your setup is ready.")
        print("\nYou can now run: python app.py")
    else:
        print(f"✗ Found {len(all_errors)} issue(s):")
        for i, error in enumerate(all_errors, 1):
            print(f"  {i}. {error}")
        print("\nPlease fix these issues before running the application.")
    print("=" * 50)

if __name__ == "__main__":
    main()
