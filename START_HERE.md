# Attendify - Start Here

## Your App is Running!

The application is successfully running at:
- **Local:** http://127.0.0.1:5001
- **Network:** http://192.168.18.7:5001

## How to Use

### 1. Access the Web Interface
Open your browser and go to: **http://localhost:5001**

### 2. Enroll Your First Student

1. Click on the **"Enroll Student"** tab
2. Fill in the student details:
   - Student ID: e.g., "STU001"
   - Name: e.g., "John Doe"
   - Email: (optional)
   - Phone: (optional)
3. Click **"Create Student"**
4. Upload a clear face photo (front-facing, well-lit)
5. Click **"Upload & Enroll Face"**

### 3. Mark Attendance

**Option A: Live Camera**
1. Go to **"Mark Attendance"** tab
2. Position student(s) in front of the camera
3. Click **"Capture & Mark Attendance"**
4. System will detect and recognize faces automatically

**Option B: Upload Image**
1. Go to **"Mark Attendance"** tab
2. Click **"Upload Image"**
3. Select an image with student faces
4. System will process and mark attendance

### 4. View Reports

1. Click **"Attendance Reports"** tab
2. See all attendance records with timestamps
3. Filter by date if needed

## Camera Permissions

If camera doesn't work:
- macOS will prompt you to allow camera access for Terminal/Python
- Go to System Settings > Privacy & Security > Camera
- Enable access for Terminal or Python

## Stopping the Application

To stop the server, press `CTRL+C` in the terminal

## Restarting the Application

```bash
cd /Users/macbook/Dropbox/GitHub/attendify
source venv/bin/activate
python app.py
```

## Troubleshooting

### Port 5001 already in use
Change the port in app.py:
```python
app.run(host='0.0.0.0', port=5002, debug=Config.DEBUG)
```

### Database connection error
Make sure Postgres.app is running on port 5433

### Camera not found
- Check System Settings > Privacy & Security > Camera
- Try different camera index in config.py (0, 1, 2...)

## Tips for Best Results

### Face Enrollment:
- Use clear, well-lit photos
- Face should be front-facing
- No sunglasses or face coverings
- High resolution recommended

### Attendance Marking:
- Ensure good lighting
- Face should be clearly visible
- Distance: 1-3 meters from camera
- Multiple students can be detected at once

## Next Steps

1. Enroll a few students to test the system
2. Try both camera and image upload methods
3. Check the attendance reports
4. Adjust thresholds in config.py if needed:
   - `CONFIDENCE_THRESHOLD` - for face detection
   - `FACE_RECOGNITION_THRESHOLD` - for recognition accuracy

## Need Help?

Check the README.md and QUICKSTART.md for detailed documentation.

Happy tracking!
