# Attendify - AI-Powered Attendance System

A web-based face recognition attendance system using YOLOv8 for face detection and DeepFace for recognition. Features automatic attendance tracking with course schedule management, multi-camera support, and comprehensive admin controls.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Admin Features](#admin-features)
- [API Endpoints](#api-endpoints)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Features

### Core Functionality
- **Real-time Face Recognition**: Automatic attendance marking when students are detected
- **Multi-Face Detection**: Detect and recognize multiple students simultaneously
- **Automatic Camera Detection**: Dynamically detects and lists all available cameras with proper labels
- **Multi-Camera Support**: Switch between USB webcams, built-in cameras, and IP/CCTV streams
- **Week Tracking**: Record attendance by week (Week 1-14) for semester planning
- **Schedule-Based Sessions**: Attendance automatically linked to active course sessions
- **Duplicate Prevention**: One attendance record per student per course session per day

### Student Management
- **Student CRUD**: Add, edit, and delete students from admin panel
- **Database Lookup**: Search and select students when enrolling faces
- **Bulk Import**: Import students from Excel with auto-enrollment option
- **Multiple Face Photos**: Enroll multiple photos per student for better accuracy
- **Student Records**: Track name, ID, email, phone, and enrollment status

### Course Management
- **Course Schedules**: Define courses with specific time slots and days of week
- **Week Selection**: Choose which week (1-14) when starting attendance sessions
- **Course Enrollment**: Manage which students are enrolled in each course
- **Active/Inactive Courses**: Enable or disable courses as needed

### Admin Dashboard
- **Secure Login**: Password-protected admin access
- **User Management**: Add, edit, and delete student records
- **Course Management**: Create, update, and delete courses
- **Enrollment Management**: Enroll students in courses
- **Bulk Operations**: Import students from Excel spreadsheets
- **Data Export**: Export attendance records to CSV with filters

### Attendance Features
- **Live Video Feed**: Real-time camera preview with face detection
- **Automatic Recognition**: Attendance marked when face is recognized
- **Confidence Display**: Shows recognition confidence percentage
- **Status Indicators**: Visual feedback (✓ marked, "Recent", "Not Enrolled", etc.)
- **Bounding Boxes**: Shows student names on detected faces
- **Live Reports**: Real-time attendance list for current session

## Tech Stack

- **Backend**: Flask 3.0+
- **Database**: PostgreSQL 12+
- **Face Detection**: YOLOv8 (Ultralytics)
- **Face Recognition**: DeepFace with Facenet512
- **Computer Vision**: OpenCV
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Data Processing**: Pandas (for Excel import/export)
- **ORM**: SQLAlchemy

## Prerequisites

- **Python**: 3.8 or higher
- **PostgreSQL**: 12 or higher
- **Camera**: USB webcam or built-in camera
- **OS**: macOS, Linux, or Windows
- **RAM**: Minimum 4GB (8GB recommended for better performance)

## Installation

### Quick Setup

1. **Clone the repository:**
```bash
git clone https://github.com/firmanhadi21/attendify.git
cd attendify
```

2. **Run the automated setup script:**
```bash
chmod +x setup.sh
./setup.sh
```

The script will:
- Create Python virtual environment
- Install all dependencies
- Set up environment configuration
- Create database tables
- Initialize admin user

### Manual Setup

1. **Clone and create virtual environment:**
```bash
git clone https://github.com/firmanhadi21/attendify.git
cd attendify
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up PostgreSQL:**
```bash
# macOS (Homebrew)
brew install postgresql@15
brew services start postgresql@15

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql

# Create database
createdb attendify_db
```

4. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. **Initialize database:**
```bash
python init_admin.py
```

Creates:
- Database tables (students, courses, enrollments, attendance, admins)
- Default admin (username: `admin`, password: `admin123`)
- Sample courses for testing

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5433          # 5432 for standard PostgreSQL, 5433 for Postgres.app
DB_NAME=attendify_db
DB_USER=postgres
DB_PASSWORD=

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
```

### Database Connection Pool

The system uses an optimized connection pool for better stability and performance:

- **Pool Size**: 20 connections (handles concurrent users)
- **Max Overflow**: 40 additional connections during peak load
- **Pool Recycle**: Connections recycled every hour (3600s) to prevent stale connections
- **Pre-ping**: Validates connections before use to avoid database errors

These settings are configured automatically in `database.py` and require no manual configuration.

### macOS Camera Access

For macOS, add this to your `~/.zshrc` to enable camera access:

```bash
export OPENCV_AVFOUNDATION_SKIP_AUTH=1
```

Then reload:
```bash
source ~/.zshrc
```

### Camera Configuration

The system **automatically detects and enumerates all available cameras** when you navigate to the Mark Attendance tab. The camera dropdown is populated dynamically with actual device names (e.g., "Logitech C920", "FaceTime HD Camera") instead of generic labels.

**How it works:**
1. When entering the attendance tab, the browser requests camera permissions
2. All available video input devices are detected and listed
3. Cameras are shown with their actual device names for easy identification
4. Select your preferred camera from the dropdown before starting a session

**Supported camera types:**
- USB webcams (automatically detected)
- Built-in laptop cameras
- IP/CCTV cameras (via RTSP URL in config)
- Virtual cameras (OBS, etc.)

## Usage

### Starting the Application

1. **Activate virtual environment:**
```bash
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. **Start the server:**
```bash
python app.py
```

3. **Access the application:**
```
http://localhost:5001
```

### Initial Setup

1. **Login to Admin:**
   - Click "Admin" tab
   - Username: `admin`
   - Password: `admin123`
   - **Change password immediately after first login!**

2. **Create Courses:**
   - Go to Admin → Courses
   - Add courses with schedule (time, days of week)
   
3. **Add Students:**
   - Option A: Admin → Students → Add New Student
   - Option B: Admin → Import Students → Upload Excel file

4. **Enroll Students in Courses:**
   - Admin → Enrollments → Enroll Student in Course

5. **Enroll Face Photos:**
   - Go to "Enroll Student" tab
   - Click "Select from Database"
   - Search or filter by course
   - Select student and capture face photo

### Marking Attendance

1. **Start Session:**
   - Go to "Mark Attendance" tab
   - Select Camera (0 or 1)
   - Select Course Session
   - Select Week (1-14)
   - Click "Start Attendance Session"

2. **Automatic Recognition:**
   - Students stand in front of camera
   - System detects faces and shows bounding boxes
   - Names appear above faces
   - Attendance marked automatically when recognized
   - Status shows: ✓ (marked), "Recent" (already seen), "Not Enrolled", etc.

3. **End Session:**
   - Click "Stop Attendance Session"

4. **View Results:**
   - Go to "Live Attendance Report" tab
   - Filter by course, date, or week
   - Export to CSV if needed

## Admin Features

### Student Management

**Add Student:**
- Admin → Students → Add New Student
- Enter Student ID, Name, Email, Phone
- Click "Save Student"

**Edit Student:**
- Find student in list
- Click "Edit"
- Update information
- Click "Update Student"

**Delete Student:**
- Click "Delete" button
- Confirms deletion of student, face photos, enrollments, and attendance records
- **Warning**: This action cannot be undone!

### Course Management

**Create Course:**
- Admin → Courses → Add New Course
- Course Code (e.g., "CS201")
- Course Name (e.g., "Data Structures")
- Start Time / End Time
- Select days of week
- Click "Save Course"

**Edit/Delete Courses:**
- Edit: Update course details
- Delete: Removes course and all enrollments

### Bulk Import Students

1. **Download Template:**
   - Admin → Import Students
   - Click "Download Excel Template"

2. **Prepare Excel File:**
   ```
   | Student ID | Full Name    | Email                 | Phone       |
   |------------|--------------|-----------------------|-------------|
   | 123456     | John Doe     | john@example.com      | +1234567890 |
   | 123457     | Jane Smith   | jane@example.com      | +1234567891 |
   ```

3. **Import:**
   - Select Course (optional) for auto-enrollment
   - Choose Excel file
   - Click "Import Students"
   - Review import results

### Export Attendance

- Admin → Export Data
- Filter by Course (optional)
- Select Date Range
- Click "Download CSV"
- Opens in Excel/Sheets with columns: Student ID, Name, Course, Date, Time, Week, Confidence

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

## API Endpoints

### Authentication
- `POST /api/admin/login` - Admin login

### Students
- `GET /api/students` - List all students
- `POST /api/students` - Create new student
- `PUT /api/students/<id>` - Update student
- `DELETE /api/students/<id>` - Delete student
- `GET /api/students/search` - Search students with filters
- `POST /api/students/<id>/enroll` - Enroll student face photo
- `POST /api/students/bulk-import` - Bulk import from Excel

### Courses
- `GET /api/courses` - List all courses
- `POST /api/courses` - Create new course
- `PUT /api/courses/<id>` - Update course
- `DELETE /api/courses/<id>` - Delete course

### Enrollments
- `GET /api/enrollments` - List all enrollments
- `POST /api/enrollments` - Enroll student in course
- `DELETE /api/enrollments/<id>` - Remove enrollment

### Attendance
- `GET /api/attendance` - Get attendance records
- `GET /api/attendance/live` - Get live attendance for active session
- `GET /api/video_feed` - Live camera stream with face recognition
- `POST /api/export-attendance` - Export attendance to CSV

## Troubleshooting

### Camera Issues

**"Camera not available" error:**
```bash
# macOS - Add to ~/.zshrc
export OPENCV_AVFOUNDATION_SKIP_AUTH=1

# Then reload
source ~/.zshrc
```

**"Camera access denied" in dropdown:**
- Allow camera permissions when prompted by browser
- Check browser settings: Site permissions → Camera → Allow
- Try refreshing the page after granting permissions

**No cameras detected:**
- Ensure cameras are connected before opening the page
- Check camera indices with: `python list_cameras.py`
- Refresh the attendance tab to re-detect cameras

**Camera feed shows black screen:**
- Check camera permissions in System Preferences
- Try different camera index (0 or 1)
- Ensure no other app is using the camera

### Database Issues

**"Connection refused" error:**
```bash
# Check if PostgreSQL is running
brew services list  # macOS
sudo systemctl status postgresql  # Linux

# Start if not running
brew services start postgresql@15  # macOS
sudo systemctl start postgresql  # Linux
```

**"Database does not exist":**
```bash
createdb attendify_db
python init_admin.py
```

**"Connection pool exhausted" or timeout errors:**
- The system uses a connection pool (20 connections + 40 overflow)
- If still experiencing issues, restart the application
- Check for long-running database queries
- Ensure PostgreSQL is not under heavy load from other applications

### Face Recognition Issues

**Low accuracy:**
- Ensure good lighting when enrolling faces
- Enroll multiple photos per student from different angles
- Check that enrolled photos are clear and front-facing
- Adjust confidence threshold in face_recognizer.py if needed

**"No face detected" during enrollment:**
- Ensure face is clearly visible and well-lit
- Position face directly in front of camera
- Remove sunglasses or face coverings
- Try uploading a clear photo instead

### Performance Issues

**Slow recognition:**
- Close unnecessary applications
- Use lower resolution camera settings
- Reduce number of enrolled students per course
- Use GPU acceleration if available

**High memory usage:**
- Restart application periodically
- Clear old attendance photos from data/attendance_photos/
- Optimize database with VACUUM command

### Excel Import Issues

**"Invalid file format":**
- Ensure file is .xlsx or .xls format
- Download and use provided template
- Check that required columns exist (Student ID, Full Name)

**"Duplicate Student ID":**
- Check for existing students with same ID
- Update existing student instead of re-importing

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/YourFeature`)
3. Commit changes (`git commit -m 'Add YourFeature'`)
4. Push to branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide for Python code
- Add comments for complex logic
- Update README if adding new features
- Test thoroughly before submitting PR

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or contributions:
- **GitHub Issues**: [Create an issue](https://github.com/firmanhadi21/attendify/issues)
- **Email**: firmanhadi21@lecturer.undip.ac.id

## Acknowledgments

- **YOLOv8** by Ultralytics for face detection
- **DeepFace** for face recognition
- **Flask** framework
- **OpenCV** for computer vision
- All contributors and users of this project

---

**Made with ❤️ for smarter classroom management**
1. Go to "Mark Attendance" tab
2. Click "Upload Image"
3. Select image with multiple student faces
   - Can be a group photo
