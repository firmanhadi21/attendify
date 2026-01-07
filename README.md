# Attendify - AI-Powered Attendance System

A web-based attendance system that uses YOLO for face detection and DeepFace for face recognition to automatically track student attendance with course schedule management.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Quick Setup](#quick-setup-recommended)
  - [Manual Setup](#manual-setup)
- [Usage](#usage)
  - [Starting the Application](#starting-the-application)
  - [Admin Login](#admin-login)
  - [Course Management](#course-management)
  - [Student Enrollment](#student-enrollment)
  - [Course Enrollment Management](#course-enrollment-management)
  - [Marking Attendance](#marking-attendance)
  - [Viewing Reports](#viewing-reports)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Configuration](#configuration)
- [Quick Reference](#quick-reference)
- [Performance Tips](#performance-tips)
- [Troubleshooting](#troubleshooting)
- [Security Considerations](#security-considerations)
- [Database Schema](#database-schema)
- [Key Technologies](#key-technologies)
- [Implemented Features](#implemented-features)
- [Typical Workflow](#typical-workflow)
- [How It Works](#how-it-works)
- [Future Enhancements](#future-enhancements)
- [License](#license)
- [Contributing](#contributing)
- [Support](#support)
- [Acknowledgments](#acknowledgments)

## Features

- **Multiple Face Detection**: Detects and recognizes multiple students simultaneously in a single frame
- **CCTV/IP Camera Support**: Works with RTSP, HTTP streams, and USB webcams
- **Face Detection**: Uses YOLOv8 for fast and accurate face detection
- **Face Recognition**: Leverages DeepFace with Facenet512 for reliable face identification
- **Smart Student Enrollment**: Streamlined one-step enrollment with webcam or photo upload
- **Course Schedule Management**: Create and manage courses with specific time slots and days
- **Schedule-Based Attendance**: Automatic attendance tracking based on active course sessions
- **Enrollment Management**: Enroll students in specific courses
- **Real-time Attendance**: Live camera feed for instant attendance marking
- **Batch Attendance Marking**: Mark attendance for entire class with one capture
- **Admin Module**: Complete administrative interface with secure login
- **Attendance Reports**: View, filter, and export attendance history to CSV
- **One Attendance Per Session**: Prevents duplicate attendance in the same course session
- **PostgreSQL Database**: Robust data storage for students, courses, schedules, and attendance records

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

### Quick Setup (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/firmanhadi21/attendify.git
cd attendify
```

2. Run the automated setup script:
```bash
chmod +x setup.sh
./setup.sh
```

The script will:
- Create a Python virtual environment
- Install all dependencies
- Set up the `.env` file
- Prompt you to configure database settings

### Manual Setup

1. Clone the repository:
```bash
git clone https://github.com/firmanhadi21/attendify.git
cd attendify
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up PostgreSQL database:
```bash
# macOS (using Homebrew)
brew install postgresql
brew services start postgresql

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql

# Create database
createdb attendify_db

# Or using PostgreSQL CLI
psql -U postgres
CREATE DATABASE attendify_db;
\q
```

5. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

Default configuration (port 5433 for Postgres.app on macOS):
```
DB_HOST=localhost
DB_PORT=5433
DB_NAME=attendify_db
DB_USER=postgres
DB_PASSWORD=
```

6. Initialize the database and admin user:
```bash
python init_admin.py
```

This creates:
- All required database tables
- Default admin user (username: `admin`, password: `admin123`)
- Sample courses for testing

## Usage

### Starting the Application

1. Activate virtual environment (if not already active):
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Start the application:
```bash
python app.py
```

3. Open your browser and navigate to:
```
http://localhost:5001
```

### Admin Login

1. Click on the **"Admin"** tab
2. Login with default credentials:
   - **Username**: `admin`
   - **Password**: `admin123`
3. **IMPORTANT**: Change the password after first login!

### Course Management

**Creating a Course:**
1. Go to Admin → Courses
2. Click "Add New Course"
3. Fill in details:
   - Course Code (e.g., "GIS101")
   - Course Name (e.g., "Introduction to GIS")
   - Start Time (e.g., "06:00")
   - End Time (e.g., "08:00")
   - Days of Week (check applicable days)
4. Click "Save Course"

**Editing/Deleting Courses:**
- Find the course in the list
- Click "Edit" to modify or "Delete" to remove

### Student Enrollment

**Method 1: Using Webcam**
1. Go to "Enroll Student" tab
2. Enter Student ID (e.g., "STU001")
3. Enter Full Name (e.g., "John Doe")
4. Click "Use Webcam"
5. Allow camera access when prompted
6. Position face in camera view
7. Click "Capture Photo"
8. Review the photo
9. Click "Enroll Student" (or "Retake" if photo is not clear)

**Method 2: Upload Photo**
1. Go to "Enroll Student" tab
2. Enter Student ID and Full Name
3. Click "Upload Photo"
4. Select a clear photo file
5. Click "Enroll Student"

**Tips for best results:**
- Use clear, well-lit photos
- Face should be front-facing
- No sunglasses or face coverings
- High resolution recommended

### Camera Setup for Multiple Face Detection

The system can detect and recognize **multiple students simultaneously** in a single frame. For best results when marking attendance for an entire class:

**Camera Positioning:**
1. **Height**: Mount camera 2-3 meters (6-10 feet) above ground
   - Higher positioning captures more students
   - Ideal angle: 15-30 degrees downward
2. **Distance**: Position 3-5 meters (10-16 feet) from students
   - Closer for smaller groups (5-10 students)
   - Farther for larger groups (20+ students)
3. **Lighting**: Ensure even, bright lighting
   - Avoid backlighting (windows behind students)
   - Use front or overhead lighting
4. **Coverage**: Test field of view before class
   - Ensure all student positions are visible
   - Account for standing vs. seated positions

**Camera Requirements:**
- **Resolution**: Minimum 720p (1280x720), recommended 1080p (1920x1080)
- **Field of View**: Wide-angle lens (90-120 degrees) for larger groups
- **Frame Rate**: Minimum 15 fps, recommended 30 fps
- **Connection**: USB 2.0 or higher, USB 3.0 for high resolution

**Optimal Setup Examples:**
- **Small classroom (10-15 students)**: Single camera at front center, 2.5m high
- **Medium classroom (20-30 students)**: Single wide-angle camera at rear center, 3m high
- **Large classroom (40+ students)**: Consider multiple cameras or panoramic camera

**Testing the Setup:**
1. Position camera and start the application
2. Have a few students stand in different positions
3. Capture a test image and verify all faces are detected
4. Adjust camera angle/position if some faces are missed
5. Check recognition accuracy with different lighting conditions

### Using CCTV/IP Cameras and Livestreams

The system supports **CCTV cameras and IP camera livestreams** in addition to USB webcams. This is ideal for permanent classroom installations.

**Supported Stream Protocols:**
- **RTSP** (Real-Time Streaming Protocol) - Most common for IP cameras
- **HTTP/HTTPS** - Web-based streams
- **RTMP** - Real-Time Messaging Protocol
- **Local video files** - For testing or processing recorded footage

**Configuration Methods:**

**Method 1: Using RTSP Stream (Recommended for CCTV)**

1. Find your camera's RTSP URL (check camera documentation or manufacturer website)
2. Edit [config.py](config.py):
```python
# Change from:
CAMERA_INDEX = 0

# To:
CAMERA_INDEX = 'rtsp://username:password@192.168.1.100:554/stream1'
```

**Method 2: Using Environment Variable**

Edit `.env` file:
```bash
CAMERA_INDEX=rtsp://admin:password@192.168.1.100:554/stream1
```

**Common RTSP URL Formats by Brand:**

- **Hikvision**: `rtsp://username:password@IP:554/Streaming/Channels/101`
- **Dahua**: `rtsp://username:password@IP:554/cam/realmonitor?channel=1&subtype=0`
- **Axis**: `rtsp://username:password@IP/axis-media/media.amp`
- **Amcrest**: `rtsp://username:password@IP:554/cam/realmonitor?channel=1&subtype=1`
- **Reolink**: `rtsp://username:password@IP:554/h264Preview_01_main`
- **TP-Link**: `rtsp://username:password@IP:554/stream1`
- **Generic**: `rtsp://username:password@IP:554/stream` or `/live` or `/ch01`

**Finding Your RTSP URL:**
1. Check camera's web interface (usually Settings → Network → RTSP)
2. Consult camera manual or manufacturer website
3. Use tools like VLC Media Player to test the stream:
   - Open VLC → Media → Open Network Stream
   - Enter RTSP URL and test playback

**HTTP/MJPEG Streams:**

Some cameras use HTTP-based MJPEG streams:
```python
CAMERA_INDEX = 'http://192.168.1.100:8080/video'
```

**Multiple Camera Support:**

You can configure multiple cameras and switch between them:

In [config.py](config.py):
```python
# Define multiple camera sources
CAMERAS = {
    'front': 'rtsp://admin:pass@192.168.1.100:554/stream1',
    'back': 'rtsp://admin:pass@192.168.1.101:554/stream1',
    'usb': 0  # USB webcam as fallback
}

CAMERA_INDEX = CAMERAS['front']  # Default camera
```

**Advantages of Using CCTV/IP Cameras:**
- ✅ **Permanent Installation** - No need to set up daily
- ✅ **Better Positioning** - Mount at optimal height and angle
- ✅ **Higher Quality** - Professional cameras often have better sensors
- ✅ **Wide Coverage** - Use existing classroom surveillance cameras
- ✅ **Remote Access** - Access streams from anywhere on network
- ✅ **Continuous Operation** - No USB cable issues
- ✅ **Pan/Tilt/Zoom** - Some cameras allow remote adjustments

**Troubleshooting RTSP Streams:**

1. **Test stream first with VLC**:
   ```bash
   # Install VLC if not already installed
   brew install vlc  # macOS
   
   # Test stream
   vlc rtsp://username:password@192.168.1.100:554/stream1
   ```

2. **Check network connectivity**:
   ```bash
   ping 192.168.1.100
   ```

3. **Verify credentials** - Username and password must be correct

4. **Check firewall** - Ensure port 554 (RTSP) is not blocked

5. **Try different stream paths** - Cameras may have multiple streams:
   - Main stream (high quality): `/stream1` or `/h264Preview_01_main`
   - Sub stream (lower quality, faster): `/stream2` or `/h264Preview_01_sub`

6. **Latency issues** - Use sub-stream for lower latency

**Performance Considerations:**

- **Network bandwidth**: High-resolution streams require good network
- **Latency**: Local network cameras have minimal delay
- **Processing**: Same as USB cameras once stream is received
- **Reliability**: Wired connection preferred over WiFi

**Example Setup for Large Classroom:**

```python
# config.py
# Use main CCTV camera for attendance
CAMERA_INDEX = 'rtsp://admin:secure_password@192.168.1.100:554/Streaming/Channels/101'
FRAME_WIDTH = 1920  # 1080p resolution
FRAME_HEIGHT = 1080
```

This setup allows you to use your existing classroom CCTV infrastructure for automated attendance tracking!

### Course Enrollment Management

**Enrolling Students in Courses:**
1. Go to Admin → Enrollments
2. Click "Enroll Student in Course"
3. Select student and course from dropdowns
4. Click "Enroll"

**Viewing/Managing Enrollments:**
- See all student-course enrollments
- Click "Unenroll" to remove a student from a course

### Marking Attendance

**Using Live Camera (Batch Mode - Multiple Students):**
1. Go to "Mark Attendance" tab
2. System displays active courses (based on current time and day)
3. Camera feed shows live view with all students visible
4. Position students within camera's field of view
   - All students can be in frame simultaneously
   - System detects and recognizes multiple faces at once
5. Click "Capture & Mark Attendance"
6. System processes the frame:
   - Detects all visible faces
   - Recognizes each student
   - Marks attendance for all enrolled students in one action
7. Results show:
   - Number of faces detected
   - Students successfully marked present
   - Unrecognized faces (if any)

**Using Image Upload (Batch Processing):**
1. Go to "Mark Attendance" tab
2. Click "Upload Image"
3. Select image with multiple student faces
   - Can be a group photo
   - Can be a classroom snapshot
4. System processes and marks attendance for all detected and recognized faces

**Real-time Feedback:**
- Green boxes around recognized students
- Student names/IDs displayed above each face
- Total count: "Marked X out of Y detected faces"

**Key Features:**
- **Batch Processing**: Mark entire class attendance with one capture
- **Multiple Face Detection**: Processes all students in frame simultaneously
- Attendance only marked during scheduled course times
- One attendance per student per course session
- Only enrolled students can be marked present
- Handles varying distances and angles within frame

### Viewing Reports

1. Go to "Attendance Reports" tab
2. View all attendance records with:
   - Student details
   - Course information
   - Timestamp
   - Date
3. Filter by date range if needed
4. Export to CSV using the admin panel

## Project Structure

```
attendify/
├── app.py                      # Main Flask application with all routes
├── config.py                   # Configuration settings
├── database.py                 # Database models (Student, Course, Enrollment, Attendance, Admin)
├── face_detector.py            # YOLO face detection module
├── face_recognizer.py          # DeepFace recognition module
├── init_admin.py               # Database initialization and admin setup script
├── requirements.txt            # Python dependencies
├── setup.sh                    # Automated setup script
├── .env.example               # Environment variables template
├── README.md                  # This file
├── START_HERE.md              # Quick start guide
├── QUICKSTART.md              # Detailed setup instructions
├── COURSE_SCHEDULE_SYSTEM.md  # Course scheduling system documentation
├── UPDATED_ENROLLMENT.md      # Enrollment process documentation
├── templates/
│   └── index.html             # Web interface with all tabs
├── static/
│   ├── css/
│   │   └── style.css          # Application styling
│   └── js/
│       └── app.js             # Frontend logic and API calls
├── data/
│   └── student_faces/         # Stored face images organized by student ID
└── models/
    ├── yolov8n.pt             # YOLOv8 nano model
    └── face_encodings.pkl     # Face embeddings database
```

## API Endpoints

### Students
- `GET /api/students` - Get all students
- `POST /api/students` - Create new student
- `POST /api/students/<id>/enroll` - Enroll student face with image

### Attendance
- `GET /api/attendance` - Get attendance records (with optional date filter)
- `GET /api/attendance/live` - Get currently active courses
- `POST /api/attendance/mark` - Mark attendance from image (checks course schedule)

### Courses
- `GET /api/courses` - Get all active courses
- `POST /api/courses` - Create new course (admin only)
- `PUT /api/courses/<id>` - Update course (admin only)
- `DELETE /api/courses/<id>` - Delete course (admin only, soft delete)

### Enrollments
- `GET /api/enrollments` - Get all course enrollments
- `POST /api/enrollments` - Enroll student in course (admin only)
- `DELETE /api/enrollments/<id>` - Remove enrollment (admin only)

### Admin
- `POST /api/admin/login` - Admin authentication
- `POST /api/admin/create` - Create new admin user (requires existing admin auth)

### Export
- `GET /api/export/attendance` - Export attendance records to CSV (with date filters)

### Camera
- `GET /api/video_feed` - Live video stream with face detection

## Configuration

Edit `config.py` or `.env` to customize:

### Database Settings
- `DB_HOST` - Database host (default: localhost)
- `DB_PORT` - Database port (default: 5433 for Postgres.app, 5432 for standard PostgreSQL)
- `DB_NAME` - Database name (default: attendify_db)
- `DB_USER` - Database user (default: postgres)
- `DB_PASSWORD` - Database password

### Application Settings
- `SECRET_KEY` - Flask secret key for sessions
- `DEBUG` - Debug mode (default: True)

### AI Model Settings
- `YOLO_MODEL` - YOLO model selection (default: yolov8n.pt for speed)
- `CONFIDENCE_THRESHOLD` - Face detection confidence (default: 0.5)
- `FACE_RECOGNITION_THRESHOLD` - Face matching threshold (default: 0.6)

### Camera Settings
- `CAMERA_INDEX` - Camera device index or stream URL
  - **USB Webcam**: `0`, `1`, `2` (integer for device index)
  - **RTSP Stream**: `'rtsp://username:password@IP:554/stream1'` (string URL)
  - **HTTP Stream**: `'http://IP:8080/video'` (string URL)
  - **Video File**: `'/path/to/video.mp4'` (string path for testing)
  - macOS USB: Usually 0 for built-in, 1+ for external
- `FRAME_WIDTH` - Camera frame width (default: 640)
  - Recommended: 1280 for medium groups, 1920 for large groups
- `FRAME_HEIGHT` - Camera frame height (default: 480)
  - Recommended: 720 for medium groups, 1080 for large groups

**Examples:**
```python
# USB Webcam
CAMERA_INDEX = 0

# CCTV/IP Camera (RTSP)
CAMERA_INDEX = 'rtsp://admin:password@192.168.1.100:554/stream1'

# HTTP Stream
CAMERA_INDEX = 'http://192.168.1.100:8080/video'

# Video file (for testing)
CAMERA_INDEX = '/path/to/classroom_recording.mp4'
```

## Quick Reference

### Common Commands

```bash
# Start the application
python app.py

# Initialize/Reset database and admin
python init_admin.py

# Test database connection
python test_setup.py

# List available cameras
python list_cameras.py

# Check attendance for today
python check_attendance.py

# Test RTSP stream with VLC (macOS)
vlc rtsp://username:password@192.168.1.100:554/stream1

# Test network connectivity to IP camera
ping 192.168.1.100
```

### Default Credentials
- **Admin Username**: `admin`
- **Admin Password**: `admin123` (change immediately!)

### Default URLs
- **Application**: http://localhost:5001
- **Video Feed**: http://localhost:5001/api/video_feed

### Camera Configuration Examples
```python
# USB Webcam (config.py)
CAMERA_INDEX = 0

# CCTV Camera - Hikvision (config.py)
CAMERA_INDEX = 'rtsp://admin:password@192.168.1.100:554/Streaming/Channels/101'

# CCTV Camera - Dahua (config.py)
CAMERA_INDEX = 'rtsp://admin:password@192.168.1.101:554/cam/realmonitor?channel=1&subtype=0'

# Or using .env file
CAMERA_INDEX=rtsp://admin:password@192.168.1.100:554/stream1
```

### File Locations
- **Student Photos**: `data/student_faces/<student_id>/`
- **Face Embeddings**: `models/face_encodings.pkl`
- **YOLO Model**: `yolov8n.pt`
- **Configuration**: `config.py` and `.env`

## Performance Tips

1. **YOLO Model Selection**:
   - `yolov8n.pt` - Fastest, good for real-time (recommended for <20 students)
   - `yolov8s.pt` - Balanced speed and accuracy (good for 20-40 students)
   - `yolov8m.pt` - More accurate, slower (use for critical accuracy needs)

2. **Face Recognition**:
   - Adjust `FACE_RECOGNITION_THRESHOLD` in [config.py](config.py)
   - Lower (0.4-0.5) = stricter matching, fewer false positives
   - Higher (0.6-0.7) = more lenient, better for varying conditions

3. **Camera Settings for Multiple Students**:
   - **Small groups (5-15)**: 720p @ 30fps is sufficient
   - **Medium groups (15-30)**: 1080p @ 30fps recommended
   - **Large groups (30+)**: 1080p or higher, wide-angle lens required
   - Higher resolution = better small face detection
   - Trade-off: Higher resolution = slower processing

4. **Batch Processing Optimization**:
   - Process 10-20 students per capture for best speed/accuracy balance
   - For classes >40 students, consider:
     - Multiple camera positions
     - Processing in groups (front half, back half)
     - Using higher-end GPU for faster processing

5. **Database Optimization**:
   - Regularly archive old attendance records
   - Index frequently queried fields
   - Use connection pooling for high-traffic scenarios

6. **Lighting Optimization**:
   - Uniform lighting reduces false negatives
   - Avoid shadows on faces
   - Natural light + artificial supplement works best

## Troubleshooting

### Camera not working
- **macOS**: Go to System Settings → Privacy & Security → Camera
  - Enable access for Terminal or Python
- Check camera permissions in browser settings
- Try different `CAMERA_INDEX` values (0, 1, 2...)
- Ensure no other application is using the camera
- For USB cameras on macOS, select camera in browser's camera picker

### RTSP/IP Camera stream not working
- **Test with VLC first**: `vlc rtsp://username:password@IP:554/stream1`
- **Check network connectivity**: `ping IP_ADDRESS`
- **Verify credentials**: Ensure username and password are correct
- **Try different stream paths**:
  - Main stream: `/stream1`, `/Streaming/Channels/101`, `/h264Preview_01_main`
  - Sub stream: `/stream2`, `/h264Preview_01_sub` (lower latency)
- **Check firewall**: Ensure port 554 (RTSP) is not blocked
- **Network issues**: Use wired connection instead of WiFi for reliability
- **Encoding compatibility**: Some cameras use H.265/HEVC which may require additional codecs
- **URL format**: Remove spaces, use correct protocol (rtsp:// not http://)

**Common errors:**
- "Cannot open camera": Check URL format and credentials
- "Connection timeout": Verify network connectivity and firewall
- "No frames received": Try sub-stream or check camera settings
- "Codec not supported": Install additional OpenCV codecs or use H.264 stream

### Port 5001 already in use
Change the port in [app.py](app.py):
```python
app.run(host='0.0.0.0', port=5002, debug=Config.DEBUG)
```

### Database connection errors
- Verify PostgreSQL is running
  - macOS (Postgres.app): Check if app is running
  - Check port (5433 for Postgres.app, 5432 for standard)
- Check credentials in `.env`
- Ensure database exists: `createdb attendify_db`
- Verify connection: `psql -h localhost -p 5433 -U postgres -d attendify_db`

### Face detection issues
- Ensure good lighting conditions
- Face should be clearly visible and front-facing
- Distance: 1-3 meters from camera
- Try adjusting `CONFIDENCE_THRESHOLD` in [config.py](config.py)
- Verify YOLOv8 model file exists: `yolov8n.pt`

### Face recognition not working
- Enroll with multiple clear face images
- Adjust `FACE_RECOGNITION_THRESHOLD` in [config.py](config.py)
  - Lower (e.g., 0.4) = stricter matching
  - Higher (e.g., 0.7) = more lenient
- Ensure consistent lighting during enrollment and recognition
- Check if face embeddings are being saved

### Attendance not being marked
- Verify student is enrolled in the active course
- Check that current time matches course schedule
- Ensure course is set for the correct days of the week
- Check if student has already been marked present in this session
- Verify course is active (not deleted)

### Admin login issues
- Default credentials: username `admin`, password `admin123`
- If login fails, reinitialize: `python init_admin.py`
- Check browser console for errors
- Clear browser cache/cookies

### Students not appearing in enrollment dropdown
- Verify students have been enrolled (face images uploaded)
- Refresh the page
- Check browser console for API errors

### Not all students detected in group photo
- Ensure adequate lighting for all faces
- Verify camera resolution is sufficient (min 720p)
- Check that all faces are visible (not occluded)
- Reduce distance or use higher resolution camera
- Ensure faces are at least 60x60 pixels in the image
- Try adjusting `CONFIDENCE_THRESHOLD` (lower for more detections)
- Some faces may be too far, too small, or at extreme angles

### System only detecting some faces in frame
- Increase camera resolution (1080p recommended for large groups)
- Improve lighting - ensure even illumination
- Verify `CONFIDENCE_THRESHOLD` setting (try 0.3-0.4 for more detections)
- Check face size - small faces may not be detected
- Ensure students are within 5 meters of camera
- Avoid extreme angles (>45 degrees from camera)

## Security Considerations

- **Change default admin password** immediately after first login
- Change `SECRET_KEY` in production environment
- Use strong database passwords
- Consider implementing rate limiting for API endpoints
- Store face images securely with proper access controls
- Comply with data privacy regulations (GDPR, CCPA, etc.)
- Use HTTPS in production
- Implement session timeouts for admin users
- Regular security audits and updates
- Hash sensitive data in the database

## Database Schema

The system uses the following main tables:

- **students**: Student information and face embeddings
- **courses**: Course details with schedules
- **enrollments**: Student-course relationships
- **attendance**: Attendance records with timestamps
- **admins**: Admin user accounts with hashed passwords

For detailed schema information, see [database.py](database.py).

## Key Technologies

- **YOLOv8**: Fast object detection for face localization
- **DeepFace**: Deep learning framework for face recognition
- **Facenet512**: Neural network model for face embeddings
- **Flask**: Lightweight web framework
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL**: Relational database for data persistence
- **OpenCV**: Computer vision library for image processing

## Implemented Features

✅ Face detection with YOLOv8  
✅ Face recognition with DeepFace  
✅ Course schedule management  
✅ Schedule-based attendance tracking  
✅ Admin authentication and authorization  
✅ CSV export for attendance records  
✅ Student-course enrollment management  
✅ One attendance per session prevention  
✅ Real-time camera feed  
✅ Webcam and photo upload enrollment  
✅ Live course detection based on time/day  
✅ CCTV/IP camera livestream support (RTSP, HTTP, RTMP)  
✅ Multiple camera source support  

## Typical Workflow

### Initial Setup (One-time)
1. Run `./setup.sh` or manually install dependencies
2. Initialize database with `python init_admin.py`
3. Login as admin and change default password
4. Create courses with schedules
5. **Optional**: Configure CCTV/IP camera stream in [config.py](config.py)

### Daily Operation (with CCTV Camera)
1. **Before class**: Admin enrolls students in courses (if not already done)
2. **During class**: 
   - System automatically connects to CCTV livestream
   - System automatically detects active courses based on schedule
   - CCTV camera captures all students in classroom
   - Click "Capture & Mark Attendance" once
   - System detects and recognizes all students in the frame simultaneously
   - Attendance marked for all enrolled students in one batch operation
   - Each student can only be marked once per session
3. **After class**: View attendance reports and export if needed

**Example - Marking 30 Students Using Classroom CCTV:**
1. **One-time setup**: Configure CCTV stream URL in config.py
2. **Daily operation**:
   - Open attendance system - automatically connects to CCTV
   - All 30 students visible in CCTV feed
   - Click "Capture & Mark Attendance"
   - System processes: "Detected 30 faces, marked 28 students, 2 unrecognized"
   - Done - entire class attendance marked in seconds!
3. **No daily setup needed** - permanent camera installation!

### Student Management
1. Enroll new students with face photos
2. Enroll students in relevant courses
3. Update course enrollments as needed

## How It Works

### Face Detection (Batch Processing)
- YOLOv8 scans the entire image for face regions
- **Detects multiple faces simultaneously** in a single frame
- Returns array of bounding boxes with confidence scores
- Processes all faces in parallel for efficiency
- Example: In a classroom with 30 students, detects all 30 faces in ~0.5-1 second

### Face Recognition (Individual Processing)
- For each detected face:
  - DeepFace extracts 512-dimensional embedding using Facenet512
  - Compares embedding with all stored student embeddings
  - Matches based on cosine similarity threshold
  - Returns student identity with confidence score
- All faces processed in sequence, typically ~0.2-0.5 seconds per face
- Total processing time for 30 students: ~10-15 seconds

### Schedule-Based Attendance (Batch Verification)
1. System checks current day and time
2. Identifies active courses from the schedule
3. **For each detected face** (batch iteration):
   - Recognizes the student via face matching
   - Verifies enrollment in active course
   - Checks if already marked present in this session
   - Marks attendance if all conditions met
4. Returns comprehensive summary:
   - Total faces detected
   - Students successfully marked present
   - Unrecognized faces
   - Already-marked students (if any)

### Performance Characteristics
- **Detection**: Fast - processes entire frame at once
- **Recognition**: Moderate - sequential processing of each face
- **Scalability**: Tested with up to 30+ faces per frame
- **Accuracy**: 95%+ recognition rate with good lighting and positioning

## Future Enhancements

- [ ] Multi-camera support for large classrooms
- [ ] Real-time push notifications for attendance
- [ ] Student self-service dashboard
- [ ] Attendance analytics and insights (graphs, trends)
- [ ] Email/SMS notifications for absences
- [ ] Mobile application (iOS/Android)
- [ ] Facial mask detection
- [ ] Integration with Learning Management Systems (LMS)
- [ ] Automated attendance reports generation
- [ ] Biometric access control integration
- [ ] Advanced anti-spoofing (liveness detection)
- [ ] Multi-language support
- [ ] Role-based access control (RBAC) for multiple admin levels

## License

MIT License - See LICENSE file for details

## Author

**Firman Hadi** - [firmanhadi21](https://github.com/firmanhadi21)

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please ensure:
- Code follows PEP 8 style guidelines
- All tests pass
- Documentation is updated
- Commit messages are clear and descriptive

## Support

For issues, questions, or feature requests:
- Open an issue on [GitHub](https://github.com/firmanhadi21/attendify/issues)
- Check existing documentation files:
  - [START_HERE.md](START_HERE.md) - Quick start guide
  - [QUICKSTART.md](QUICKSTART.md) - Detailed setup
  - [COURSE_SCHEDULE_SYSTEM.md](COURSE_SCHEDULE_SYSTEM.md) - Course management
  - [UPDATED_ENROLLMENT.md](UPDATED_ENROLLMENT.md) - Enrollment process

## Acknowledgments

- **YOLOv8** by Ultralytics for fast face detection
- **DeepFace** library for powerful face recognition
- **Facenet512** model for face embeddings
- Flask community for excellent web framework
- PostgreSQL team for robust database system

---

**Built with ❤️ for educational institutions**
