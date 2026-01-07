# Attendify - AI-Powered Attendance System

A web-based attendance system that uses YOLO for face detection and DeepFace for face recognition to automatically track student attendance.

## Features

- **Face Detection**: Uses YOLOv8 for fast and accurate face detection
- **Face Recognition**: Leverages DeepFace with Facenet512 for reliable face identification
- **Student Enrollment**: Easy-to-use interface for registering new students
- **Real-time Attendance**: Live camera feed for instant attendance marking
- **Attendance Reports**: View and filter attendance history
- **PostgreSQL Database**: Robust data storage for students and attendance records

## Tech Stack

- **Backend**: Flask (Python)
- **Face Detection**: YOLOv8 (Ultralytics)
- **Face Recognition**: DeepFace
- **Database**: PostgreSQL
- **Frontend**: HTML, CSS, JavaScript
- **Computer Vision**: OpenCV

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Webcam (for live attendance marking)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd attendify
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up PostgreSQL database:
```bash
# Create database
createdb attendify_db

# Or using PostgreSQL CLI
psql -U postgres
CREATE DATABASE attendify_db;
```

5. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

6. Initialize the database:
```bash
python -c "from database import init_db; init_db()"
```

## Usage

1. Start the application:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. **Enroll Students**:
   - Go to the "Enroll Student" tab
   - Fill in student details (ID, name, email, phone)
   - Upload a clear face image
   - Click "Upload & Enroll Face"

4. **Mark Attendance**:
   - Go to the "Mark Attendance" tab
   - Use "Capture & Mark Attendance" for live camera
   - Or use "Upload Image" for batch processing
   - System will detect and recognize faces automatically

5. **View Reports**:
   - Go to "Attendance Reports" tab
   - Filter by date to view specific records
   - Export data as needed

## Project Structure

```
attendify/
├── app.py                  # Flask application
├── config.py               # Configuration settings
├── database.py             # Database models and setup
├── face_detector.py        # YOLO face detection
├── face_recognizer.py      # DeepFace recognition
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── templates/
│   └── index.html         # Web interface
├── static/
│   ├── css/
│   │   └── style.css      # Styling
│   └── js/
│       └── app.js         # Frontend logic
├── data/
│   └── student_faces/     # Stored face images
└── models/
    └── face_encodings.pkl # Face embeddings database
```

## API Endpoints

### Students
- `GET /api/students` - Get all students
- `POST /api/students` - Create new student
- `POST /api/students/<id>/enroll` - Enroll student face

### Attendance
- `GET /api/attendance` - Get attendance records
- `POST /api/attendance/mark` - Mark attendance from image

### Camera
- `GET /api/video_feed` - Live video stream
- `POST /api/camera/capture` - Capture current frame

## Configuration

Edit `config.py` or `.env` to customize:

- Database connection settings
- YOLO model selection (default: yolov8n.pt)
- Face recognition threshold
- Camera settings
- File storage paths

## Performance Tips

1. **YOLO Model Selection**:
   - `yolov8n.pt` - Fastest, good for real-time
   - `yolov8s.pt` - Balanced
   - `yolov8m.pt` - More accurate, slower

2. **Face Recognition**:
   - Adjust `FACE_RECOGNITION_THRESHOLD` in config.py
   - Lower = stricter matching
   - Higher = more lenient

3. **Camera Settings**:
   - Reduce resolution for better performance
   - Increase for better accuracy

## Troubleshooting

### Camera not working
- Check camera permissions
- Try different `CAMERA_INDEX` values (0, 1, 2...)
- Ensure no other application is using the camera

### Database connection errors
- Verify PostgreSQL is running
- Check credentials in `.env`
- Ensure database exists

### Face detection issues
- Ensure good lighting
- Face should be clearly visible
- Try adjusting `CONFIDENCE_THRESHOLD`

### Face recognition not working
- Enroll with multiple clear face images
- Adjust `FACE_RECOGNITION_THRESHOLD`
- Ensure consistent lighting during enrollment and recognition

## Security Considerations

- Change `SECRET_KEY` in production
- Use strong database passwords
- Implement user authentication for production use
- Store face images securely
- Comply with data privacy regulations (GDPR, etc.)

## Future Enhancements

- [ ] Multi-camera support
- [ ] Real-time notifications
- [ ] Export attendance to CSV/Excel
- [ ] Student dashboard
- [ ] Admin authentication
- [ ] Attendance analytics
- [ ] Email/SMS notifications
- [ ] Mobile app

## License

MIT License

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Support

For issues and questions, please open an issue on GitHub.
