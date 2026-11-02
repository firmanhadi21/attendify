#!/usr/bin/env python3
"""
List all available cameras on the system
"""
import cv2
import ctypes
import json
import os
import subprocess
import sys
import time

# Cache for camera scan results
_camera_cache = {
    'cameras': None,
    'timestamp': 0
}
CACHE_TTL = 30  # seconds

def _macos_camera_names():
    """Return macOS camera names in OpenCV AVFoundation index order.

    OpenCV numbers AVFoundation devices by sorting them on uniqueID, so sorting
    system_profiler's camera list the same way maps each index to its real name.
    Returns an empty list if the names can't be read.
    """
    if sys.platform != 'darwin':
        return []
    try:
        result = subprocess.run(['system_profiler', 'SPCameraDataType', '-json'],
                                capture_output=True, text=True, timeout=10)
        devices = json.loads(result.stdout).get('SPCameraDataType', [])
    except (OSError, subprocess.SubprocessError, ValueError):
        return []

    names = []
    for device in sorted(devices, key=lambda d: d.get('spcamera_unique-id', '')):
        name = device.get('_name', 'Unknown Camera')
        model = device.get('spcamera_model-id', '')
        # Continuity Camera shows the owner's name (e.g. "Firman Hadi Camera"), so tag the device type
        for kind in ('iPhone', 'iPad'):
            if model.startswith(kind):
                name += f" ({kind})"
        names.append(name)
    return names

def get_available_cameras(max_cameras=10, force_refresh=False, active_cameras=None):
    """Test camera indices to find available cameras.

    Results are cached to avoid repeatedly opening/releasing cameras,
    which can drop iPhone Continuity Camera connections.

    Args:
        active_cameras: dict of camera_index -> VideoCapture instances that are
                        currently in use and should not be released during scanning.
    """
    global _camera_cache

    # Return cached results if still fresh
    if not force_refresh and _camera_cache['cameras'] is not None:
        if time.time() - _camera_cache['timestamp'] < CACHE_TTL:
            print(f"Using cached camera list ({len(_camera_cache['cameras'])} cameras)")
            return _camera_cache['cameras']

    if active_cameras is None:
        active_cameras = {}

    available_cameras = []

    # Try to disable authorized warning
    import os
    os.environ['OPENCV_AVFOUNDATION_SKIP_AUTH'] = '0'

    print("Scanning for available cameras...\n")
    print("=" * 60)

    for index in range(max_cameras):
        # If this camera is already active, query it directly without reopening
        if index in active_cameras and active_cameras[index] is not None and active_cameras[index].isOpened():
            cap = active_cameras[index]
            reused = True
        else:
            # Suppress stderr to hide OpenCV's noisy "out of bound" errors
            stderr_fd = sys.stderr.fileno()
            old_stderr = os.dup(stderr_fd)
            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull, stderr_fd)
            os.close(devnull)

            cap = cv2.VideoCapture(index)
            reused = False

            # Restore stderr
            os.dup2(old_stderr, stderr_fd)
            os.close(old_stderr)

        opened = cap.isOpened()

        if opened:
            # Get camera properties without reading a frame
            # Reading frames from Continuity Camera during scanning can drop the connection
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            backend = cap.getBackendName()

            camera_info = {
                'index': index,
                'name': f"Camera {index}",
                'resolution': f"{width}x{height}",
                'fps': fps,
                'backend': backend
            }

            print(f"Camera {index}:")
            print(f"  Status: Available ✓")
            print(f"  Resolution: {width}x{height}")
            print(f"  FPS: {fps}")
            print(f"  Backend: {backend}")
            print("-" * 60)

            available_cameras.append(camera_info)
            # Only release cameras we opened for scanning, not active ones
            if not reused:
                cap.release()

    # Attach real device names, but only when macOS lists exactly as many devices as
    # OpenCV exposes; otherwise indices could be mismatched, so keep generic names
    names = _macos_camera_names()
    if available_cameras and len(names) == available_cameras[-1]['index'] + 1:
        for camera_info in available_cameras:
            camera_info['name'] = f"{names[camera_info['index']]} (Camera {camera_info['index']})"

    print("=" * 60)
    print(f"\nTotal available cameras: {len(available_cameras)}")

    # Cache the results
    _camera_cache['cameras'] = available_cameras
    _camera_cache['timestamp'] = time.time()

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
