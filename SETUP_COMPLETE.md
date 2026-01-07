# Attendify Setup Complete!

## Your Application is Running

**Access URL:** http://localhost:5001

## New Features Added

### 1. Webcam Photo Capture for Enrollment
You can now capture student photos directly from your USB webcam during enrollment!

**How to use:**
1. Go to "Enroll Student" tab
2. Fill in student details and click "Create Student"
3. Click **"Use Webcam"** button
4. Allow camera access when prompted by browser
5. Select your USB webcam from the browser's camera selection
6. Click **"Capture Photo"**
7. Review the captured photo
8. Click **"Use This Photo"** to enroll OR **"Retake"** to try again

### 2. USB Webcam Support
The system is configured to use your USB webcam (Camera Index = 1).

**Camera Configuration:**
- **Backend (Mark Attendance)**: Uses Camera Index from `.env` file (currently set to 1 for USB webcam)
- **Frontend (Enrollment)**: Browser will let you choose the camera when you click "Use Webcam"

## Quick Start Guide

### Enroll Your First Student

1. Open http://localhost:5001 in your browser
2. Go to **"Enroll Student"** tab
3. Fill in:
   - Student ID: STU001
   - Name: Your Name
   - Email & Phone (optional)
4. Click **"Create Student"**
5. Click **"Use Webcam"** button
6. Allow camera access
7. Position your face in the frame
8. Click **"Capture Photo"**
9. If happy with photo, click **"Use This Photo"**
10. Wait for "Face enrolled successfully!"

### Mark Attendance

**Method 1: Live Camera**
1. Go to **"Mark Attendance"** tab
2. Stand in front of the camera
3. Click **"Capture & Mark Attendance"**
4. System will recognize you and mark attendance

**Method 2: Upload Photo**
1. Go to **"Mark Attendance"** tab
2. Click **"Upload Image"**
3. Select a photo with your face
4. System will process and mark attendance

### View Reports

1. Go to **"Attendance Reports"** tab
2. See all attendance records
3. Filter by date if needed

## Camera Setup

### Current Configuration
- **Backend Camera (Attendance)**: Index 1 (USB Webcam)
- **Frontend Camera (Enrollment)**: Browser-selectable

### Change Camera (if needed)

Edit `.env` file:
```bash
CAMERA_INDEX=0  # Built-in camera
CAMERA_INDEX=1  # First USB webcam (current)
CAMERA_INDEX=2  # Second USB webcam
```

Then restart:
```bash
# Kill the running app (Ctrl+C in terminal)
python app.py
```

For detailed camera setup, see `CAMERA_SETUP.md`

## System Architecture

### Technologies Used
- **Face Detection**: YOLOv8 (Ultralytics)
- **Face Recognition**: DeepFace with Facenet512
- **Database**: PostgreSQL
- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Webcam**: getUserMedia API (browser), OpenCV (backend)

### File Structure
```
attendify/
├── app.py                      # Main Flask application
├── config.py                   # Configuration
├── database.py                 # Database models
├── face_detector.py            # YOLO face detection
├── face_recognizer.py          # DeepFace recognition
├── templates/index.html        # Web interface
├── static/
│   ├── css/style.css          # Styling
│   └── js/app.js              # Webcam capture logic
├── data/student_faces/         # Stored face images
└── models/                     # Face encodings database

Documentation:
├── README.md                   # Full documentation
├── QUICKSTART.md              # Quick start guide
├── CAMERA_SETUP.md            # Camera configuration
└── START_HERE.md              # Getting started
```

## Troubleshooting

### Camera Not Working
- **Browser**: Make sure to allow camera access when prompted
- **Select USB Webcam**: Choose your USB camera from browser's camera list
- **Backend**: Change `CAMERA_INDEX` in `.env` file

### Face Not Recognized
- Ensure good lighting
- Face should be clearly visible
- Try re-enrolling with better quality photo
- Adjust `FACE_RECOGNITION_THRESHOLD` in `config.py` (default: 0.6)

### Database Issues
- Make sure Postgres.app is running
- Check port 5433 is correct
- Verify credentials in `.env` file

### Port Already in Use
- Port 5001 is configured to avoid macOS AirPlay
- If still in use, change port in `app.py`

## Performance Tips

### Improve Accuracy
1. **Enrollment**:
   - Use good lighting
   - Face front-facing
   - High resolution photos
   - Enroll multiple photos (feature to add)

2. **Recognition**:
   - Adjust threshold in `config.py`
   - `FACE_RECOGNITION_THRESHOLD = 0.6` (lower = stricter)
   - `CONFIDENCE_THRESHOLD = 0.5` (YOLO detection)

### Improve Speed
1. Use faster YOLO model:
   - Current: `yolov8n.pt` (fastest)
   - Options: `yolov8s.pt`, `yolov8m.pt` (slower, more accurate)

2. Reduce camera resolution in `config.py`:
   ```python
   FRAME_WIDTH = 320  # Lower = faster
   FRAME_HEIGHT = 240
   ```

## Next Steps

1. **Test the System**:
   - Enroll yourself using webcam
   - Mark attendance with live camera
   - Check reports

2. **Enroll More Students**:
   - Add your classmates/colleagues
   - Test with multiple people

3. **Customize**:
   - Adjust thresholds for your environment
   - Modify UI colors in `static/css/style.css`
   - Add custom fields to student model

4. **Production Deployment** (when ready):
   - Use production WSGI server (Gunicorn)
   - Enable HTTPS
   - Set strong SECRET_KEY
   - Use production database credentials
   - Implement user authentication

## Support

- **README.md**: Comprehensive documentation
- **QUICKSTART.md**: Step-by-step setup
- **CAMERA_SETUP.md**: Camera troubleshooting
- **GitHub Issues**: Report bugs or request features

## Security Note

This is a development setup. For production:
- Change SECRET_KEY in `.env`
- Use strong database passwords
- Implement user authentication
- Enable HTTPS
- Follow data privacy regulations (GDPR, etc.)
- Store face data securely

## Success!

Your Attendify system is fully operational with:
- ✓ YOLO face detection
- ✓ DeepFace recognition
- ✓ PostgreSQL database
- ✓ Web interface
- ✓ Webcam capture for enrollment
- ✓ USB webcam support
- ✓ Live attendance marking
- ✓ Attendance reporting

Open http://localhost:5001 and start using it!

Happy tracking!
