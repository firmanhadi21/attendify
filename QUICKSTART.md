# Quick Start Guide

## Step 1: Install Dependencies

### Option A: Using setup script (Recommended)
```bash
chmod +x setup.sh
./setup.sh
```

### Option B: Manual setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

## Step 2: Set Up PostgreSQL Database

### Install PostgreSQL (if not already installed)

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Ubuntu/Debian:**
```bash
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows:**
Download and install from https://www.postgresql.org/download/windows/

### Create Database
```bash
# Using command line
createdb attendify_db

# Or using PostgreSQL CLI
psql -U postgres
CREATE DATABASE attendify_db;
\q
```

## Step 3: Configure Environment

Edit `.env` file with your database credentials:
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=attendify_db
DB_USER=postgres
DB_PASSWORD=your_password
```

## Step 4: Initialize Database

```bash
python -c "from database import init_db; init_db()"
```

You should see: "Database tables created successfully!"

## Step 5: Run the Application

```bash
python app.py
```

The application will start on http://localhost:5000

## Step 6: Using the System

### 1. Enroll Your First Student

1. Open http://localhost:5000 in your browser
2. Click on "Enroll Student" tab
3. Fill in student details:
   - Student ID: e.g., "STU001"
   - Name: e.g., "John Doe"
   - Email: john@example.com (optional)
   - Phone: +1234567890 (optional)
4. Click "Create Student"
5. Upload a clear face photo (front-facing, good lighting)
6. Click "Upload & Enroll Face"

### 2. Mark Attendance

**Using Live Camera:**
1. Go to "Mark Attendance" tab
2. You'll see live camera feed
3. Position student in front of camera
4. Click "Capture & Mark Attendance"
5. System will detect and recognize the face

**Using Image Upload:**
1. Go to "Mark Attendance" tab
2. Click "Upload Image"
3. Select an image containing student faces
4. System will process and mark attendance

### 3. View Reports

1. Click on "Attendance Reports" tab
2. See all attendance records
3. Filter by date if needed
4. View student name, time, and confidence score

## Tips for Best Results

### For Enrollment:
- Use clear, well-lit photos
- Face should be front-facing
- No sunglasses or face coverings
- Neutral expression works best
- High resolution (at least 640x480)

### For Attendance:
- Ensure good lighting
- Face should be clearly visible
- Distance: 1-3 meters from camera
- Look directly at camera
- Multiple students can be detected at once

## Troubleshooting

### Issue: "No module named 'cv2'"
```bash
pip install opencv-python
```

### Issue: "Database connection failed"
- Check if PostgreSQL is running: `pg_isready`
- Verify credentials in .env file
- Ensure database exists: `psql -l`

### Issue: "Camera not found"
- Check camera permissions
- Try different camera index in config.py (0, 1, 2...)
- Close other apps using the camera

### Issue: "Face not recognized"
- Re-enroll with better quality image
- Adjust FACE_RECOGNITION_THRESHOLD in config.py
- Ensure good lighting conditions

### Issue: "YOLO model download fails"
- Check internet connection
- Model will download automatically on first run
- Can manually download from Ultralytics

## System Requirements

- **OS**: macOS, Linux, or Windows
- **Python**: 3.8 or higher
- **RAM**: Minimum 4GB (8GB recommended)
- **Camera**: USB webcam or built-in camera
- **Disk Space**: 2GB for models and dependencies

## Testing the System

1. **Test with sample image:**
   - Enroll yourself first
   - Take a selfie and upload it
   - System should recognize you

2. **Test with multiple faces:**
   - Enroll 2-3 people
   - Take a group photo
   - Upload and verify all are detected

3. **Test live camera:**
   - Enroll yourself
   - Use live camera feed
   - Verify real-time recognition works

## Advanced Configuration

### Change YOLO Model (in config.py):
```python
YOLO_MODEL = 'yolov8s.pt'  # Slower but more accurate
# Options: yolov8n.pt, yolov8s.pt, yolov8m.pt, yolov8l.pt, yolov8x.pt
```

### Adjust Recognition Sensitivity (in config.py):
```python
FACE_RECOGNITION_THRESHOLD = 0.5  # Lower = stricter
CONFIDENCE_THRESHOLD = 0.6  # Lower = fewer false positives
```

### Change Camera Resolution (in config.py):
```python
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
```

## Next Steps

- Add more students
- Test with different lighting conditions
- Customize the UI in `templates/index.html`
- Add authentication for production use
- Set up automated backups of the database

## Support

For issues, check:
1. README.md for detailed documentation
2. Check logs in terminal for error messages
3. Verify all dependencies are installed
4. Ensure camera and database are accessible

Happy tracking!
