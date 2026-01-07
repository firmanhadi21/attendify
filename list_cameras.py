#!/usr/bin/env python3
"""
List all available cameras on the system
"""
import cv2

def list_cameras(max_cameras=10):
    """Test camera indices to find available cameras"""
    available_cameras = []

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

                print(f"Camera {index}:")
                print(f"  Status: Available ✓")
                print(f"  Resolution: {width}x{height}")
                print(f"  FPS: {fps}")

                # Try to get camera name (macOS specific)
                backend = cap.getBackendName()
                print(f"  Backend: {backend}")
                print("-" * 60)

                available_cameras.append(index)
            cap.release()
        else:
            print(f"Camera {index}: Not available")

    print("=" * 60)
    print(f"\nTotal available cameras: {len(available_cameras)}")
    print(f"Camera indices: {available_cameras}")

    if len(available_cameras) > 0:
        print("\nRecommendation:")
        print("- Test each camera to see which is which")
        print("- Usually Camera 0 is built-in, but not always")
        print("- iPhone/iPad via Continuity Camera may show as Camera 0 or 1")
        print("\nTo identify your cameras:")
        print("1. Disconnect iPhone if connected")
        print("2. Run this script again to see which cameras remain")
        print("3. The remaining Camera 0 is likely your Mac's built-in camera")

    return available_cameras

if __name__ == '__main__':
    cameras = list_cameras()

    if len(cameras) == 0:
        print("\n⚠️  No cameras found!")
        print("Make sure your camera is not being used by another application.")
    else:
        print(f"\n✓ Found {len(cameras)} camera(s)")
        print("\nUpdate your camera selection in the web interface accordingly.")
