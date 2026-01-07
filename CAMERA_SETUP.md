# Camera Setup Guide

## Using USB Webcam

### Finding Your USB Webcam

macOS typically assigns camera devices as follows:
- **0** = Built-in FaceTime camera (if available)
- **1** = First USB webcam
- **2** = Second USB webcam
- etc.

### Configuring Your Webcam

#### Method 1: Environment Variable (Recommended)
Add this to your `.env` file:
```
CAMERA_INDEX=1
```

Then restart the application.

#### Method 2: Edit config.py
Open `config.py` and change:
```python
CAMERA_INDEX = 1  # Change to 1 for USB webcam, 2 for second USB camera, etc.
```

### Testing Which Camera is Active

1. Open the app at http://localhost:5001
2. Go to "Mark Attendance" tab
3. Check the video feed to see which camera is active
4. If it's the wrong camera, change the `CAMERA_INDEX` value and restart

### Browser Webcam Access

The enrollment webcam capture uses your browser's camera API (getUserMedia).

**Important:**
- The browser may show a camera selection dialog
- You can choose which camera to use directly in the browser
- Grant camera permission when prompted

### Troubleshooting

#### USB Webcam Not Detected
```bash
# List connected cameras (macOS)
system_profiler SPCameraDataType
```

#### Camera Permission Denied
- Go to System Settings > Privacy & Security > Camera
- Enable camera access for your browser (Safari, Chrome, etc.)
- Enable camera access for Terminal (for backend camera)

#### Wrong Camera Selected
- Backend (YOLO detection): Change `CAMERA_INDEX` in config.py or .env
- Frontend (enrollment): Select camera in browser permission dialog

#### Camera Already in Use
- Close other apps using the camera (Zoom, Skype, etc.)
- Restart the browser
- Restart the Attendify app

### Testing Your Setup

1. **Test Backend Camera (Mark Attendance)**:
   - Go to "Mark Attendance" tab
   - You should see live video feed
   - This uses `CAMERA_INDEX` from config

2. **Test Frontend Camera (Enrollment)**:
   - Create a student
   - Click "Use Webcam"
   - Browser will ask for camera permission
   - Select your USB webcam from the dropdown

### Best Practices

- **USB Webcam Position**: Mount at eye level, 1-3 meters from students
- **Lighting**: Ensure good front lighting, avoid backlighting
- **Resolution**: Higher resolution webcams work better for face recognition
- **Stable Mount**: Use a tripod or stable mount to avoid shaky video

### Recommended USB Webcams

For best results with face detection and recognition:
- Logitech C920/C922/C930e (1080p)
- Microsoft LifeCam HD-3000
- Razer Kiyo (ring light built-in)
- Any 720p+ webcam with auto-focus

### Advanced: Multiple Cameras

If you want to use different cameras for attendance vs enrollment:

1. Backend (attendance marking): Set `CAMERA_INDEX` in config.py
2. Frontend (enrollment): Select camera in browser each time
3. This allows using a high-quality camera for enrollment and a wide-angle camera for classroom attendance

