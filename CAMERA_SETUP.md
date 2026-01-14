# Camera Setup Guide

## Automatic Camera Detection

The Mark Attendance tab now **automatically detects and lists all available cameras** when you open it. You'll see a dropdown with actual camera names (e.g., "Logitech C920", "FaceTime HD Camera") instead of generic labels.

### How It Works

1. Navigate to the **Mark Attendance** tab
2. Your browser will request camera permission (allow it)
3. All connected cameras are automatically detected and listed
4. Select your preferred camera from the dropdown
5. Start your attendance session

### Camera Selection UI

The camera dropdown shows:
- Actual device names when available
- Camera index as fallback (Camera 0, Camera 1, etc.)
- Error messages if camera access is denied

## Using USB Webcam

### Finding Your USB Webcam

The system automatically detects USB webcams. If you need to identify cameras manually, macOS typically assigns:
- **0** = Built-in FaceTime camera (if available)
- **1** = First USB webcam
- **2** = Second USB webcam
- etc.

### Backend Camera Configuration (for RTSP/IP Cameras)

For IP cameras or RTSP streams, configure in `.env` or `config.py`:

#### Method 1: Environment Variable (Recommended)
Add this to your `.env` file:
```
CAMERA_INDEX=rtsp://username:password@192.168.1.100:554/stream1
```

#### Method 2: Edit config.py
Open `config.py` and change:
```python
CAMERA_INDEX = 'rtsp://username:password@192.168.1.100:554/stream1'
```

### Testing Which Camera is Active

1. Open the app at http://localhost:5001
2. Go to "Mark Attendance" tab
3. Wait for cameras to be detected (dropdown will populate)
4. Select a camera and click "Start Attendance Session"
5. Check the video feed to verify correct camera

### Browser Webcam Access

The enrollment webcam capture uses your browser's camera API (getUserMedia).

**Important:**
- The browser may show a camera selection dialog
- You can choose which camera to use directly in the browser
- Grant camera permission when prompted

### Troubleshooting

#### "Camera access denied" in dropdown
- Allow camera permissions when prompted by browser
- Check browser settings: Site permissions > Camera > Allow
- Refresh the page after granting permissions

#### "No cameras detected" message
- Ensure cameras are connected before opening the page
- Refresh the attendance tab to re-detect cameras
- Run `python list_cameras.py` to verify camera detection at system level

#### USB Webcam Not Detected
```bash
# List connected cameras (macOS)
system_profiler SPCameraDataType

# Or use the built-in script
python list_cameras.py
```

#### Camera Permission Denied (Browser)
- Go to browser settings > Privacy > Camera
- Enable camera access for the site (localhost:5001)
- Reload the page

#### Camera Permission Denied (System)
- Go to System Settings > Privacy & Security > Camera
- Enable camera access for your browser (Safari, Chrome, etc.)
- Enable camera access for Terminal (for backend camera)

#### Wrong Camera Selected
- Use the dropdown to select the correct camera by name
- Backend (RTSP/IP cameras): Change `CAMERA_INDEX` in config.py or .env
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

