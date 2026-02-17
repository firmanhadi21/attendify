#!/usr/bin/env python3
"""
List all available cameras on the system
"""
import cv2

def get_available_cameras(max_cameras=10):
    """Test camera indices to find available cameras"""
    available_cameras = []
    
    # Try to disable authorized warning
    import os
    os.environ['OPENCV_AVFOUNDATION_SKIP_AUTH'] = '0'

    print("Scanning for available cameras...\n")
    print("=" * 60)

    for index in range(max_cameras):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            # Try to read a frame to verify camera works
            ret, frame = cap.read()
            if ret:
                # Get camera properties
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = int(cap.get(cv2.CAP_PROP_FPS))
                
                # Try to get camera name (macOS specific)
                backend = cap.getBackendName()
                
                camera_info = {
                    'index': index,
                    'name': f"Camera {index}",
                    'resolution': f"{width}x{height}",
                    'fps': fps,
                    'backend': backend
                }
                
                # Check if it looks like an iPhone/Continuity Camera
                # Often 1920x1080 or higher with specific FPS
                if width >= 1920 and height >= 1080:
                    camera_info['name'] += " (High Res/iPhone?)"

                print(f"Camera {index}:")
                print(f"  Status: Available ✓")
                print(f"  Resolution: {width}x{height}")
                print(f"  FPS: {fps}")
                print(f"  Backend: {backend}")
                print("-" * 60)

                available_cameras.append(camera_info)
            cap.release()
        else:
            print(f"Camera {index}: Not available")

    print("=" * 60)
    print(f"\nTotal available cameras: {len(available_cameras)}")
    
    return available_cameras

def list_cameras(max_cameras=10):
    cameras = get_available_cameras(max_cameras)
    indices = [c['index'] for c in cameras]
    print(f"Camera indices: {indices}")
    
    if len(cameras) > 0:
        print("\nRecommendation:")
        print("- Test each camera to see which is which")
        print("- usually Camera 0 is built-in, but not always")
        print("- iPhone/iPad via Continuity Camera may show as Camera 0 or 1")
    
    return indices

if __name__ == '__main__':
    cameras = list_cameras()

    if len(cameras) == 0:
        print("\n⚠️  No cameras found!")
        print("Make sure your camera is not being used by another application.")
    else:
        print(f"\n✓ Found {len(cameras)} camera(s)")
        print("\nUpdate your camera selection in the web interface accordingly.")
