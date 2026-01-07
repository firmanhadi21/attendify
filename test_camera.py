#!/usr/bin/env python3
"""Quick camera test"""
import cv2
import sys

print("Testing camera access...")
print("=" * 50)

# Test different camera indices
for i in range(3):
    print(f"\nTrying Camera {i}...")
    cap = cv2.VideoCapture(i)
    
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print(f"✅ Camera {i} is WORKING!")
            print(f"   Resolution: {frame.shape[1]}x{frame.shape[0]}")
        else:
            print(f"❌ Camera {i} opened but can't read frames")
        cap.release()
    else:
        print(f"❌ Camera {i} not available")

print("\n" + "=" * 50)
print("\n🔍 Troubleshooting Tips:")
print("1. Check System Preferences → Security & Privacy → Camera")
print("2. Make sure Terminal/Python has camera permission")
print("3. Close other apps using camera (Zoom, Skype, etc.)")
print("4. Try restarting your Mac")
print("5. For macOS: Disable Continuity Camera if using iPhone")
