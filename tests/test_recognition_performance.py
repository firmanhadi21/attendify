"""
Experimental evaluation script for Attendify face recognition system.
Tests recognition accuracy, latency, and robustness under varying conditions.

Usage:
    python tests/test_recognition_performance.py

Requirements:
    - Attendify database with enrolled students
    - Face images in data/student_faces/
    - PostgreSQL running
"""

import os
import sys
import time
import csv
import json
import numpy as np
import cv2
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from face_detector import FaceDetector
from face_recognizer import FaceRecognizer
from config import Config


def collect_enrollment_images():
    """Collect all enrolled student face images for testing."""
    faces_dir = Config.UPLOAD_FOLDER
    student_images = {}

    if not faces_dir.exists():
        print(f"No faces directory found at {faces_dir}")
        return student_images

    for student_dir in faces_dir.iterdir():
        if student_dir.is_dir() and student_dir.name != 'temp':
            images = list(student_dir.glob('*.jpg')) + list(student_dir.glob('*.png'))
            if images:
                student_images[student_dir.name] = images

    return student_images


def test_detection_performance(detector, student_images):
    """Test 1: Face detection rate and latency across all enrollment images."""
    print("\n" + "="*60)
    print("TEST 1: Face Detection Performance")
    print("="*60)

    results = {
        'total_images': 0,
        'faces_detected': 0,
        'no_face_detected': 0,
        'detection_times_ms': [],
        'failed_images': []
    }

    for student_id, images in student_images.items():
        for img_path in images:
            frame = cv2.imread(str(img_path))
            if frame is None:
                continue

            results['total_images'] += 1

            start = time.time()
            faces = detector.detect_faces(frame)
            elapsed_ms = (time.time() - start) * 1000

            results['detection_times_ms'].append(elapsed_ms)

            if len(faces) > 0:
                results['faces_detected'] += 1
            else:
                results['no_face_detected'] += 1
                results['failed_images'].append(str(img_path))

    if results['total_images'] > 0:
        detection_rate = results['faces_detected'] / results['total_images'] * 100
        times = results['detection_times_ms']

        print(f"  Total images tested:    {results['total_images']}")
        print(f"  Faces detected:         {results['faces_detected']}")
        print(f"  Detection rate:         {detection_rate:.1f}%")
        print(f"  Avg detection time:     {np.mean(times):.1f} ms")
        print(f"  Median detection time:  {np.median(times):.1f} ms")
        print(f"  Min detection time:     {np.min(times):.1f} ms")
        print(f"  Max detection time:     {np.max(times):.1f} ms")
        print(f"  Std detection time:     {np.std(times):.1f} ms")

        if results['failed_images']:
            print(f"\n  Failed images ({len(results['failed_images'])}):")
            for f in results['failed_images'][:5]:
                print(f"    - {f}")

    return results


def test_recognition_accuracy(recognizer, student_images):
    """Test 2: Recognition accuracy - can the system correctly identify enrolled students."""
    print("\n" + "="*60)
    print("TEST 2: Recognition Accuracy (True Positive Rate)")
    print("="*60)

    results = {
        'total_attempts': 0,
        'correct_matches': 0,
        'incorrect_matches': 0,
        'no_match': 0,
        'confidences': [],
        'distances': [],
        'recognition_times_ms': [],
        'per_student': {}
    }

    for student_id, images in student_images.items():
        student_results = {'correct': 0, 'incorrect': 0, 'no_match': 0, 'total': 0}

        for img_path in images:
            results['total_attempts'] += 1
            student_results['total'] += 1

            start = time.time()
            matched_id, confidence = recognizer.recognize_face(img_path)
            elapsed_ms = (time.time() - start) * 1000

            results['recognition_times_ms'].append(elapsed_ms)

            if matched_id == student_id:
                results['correct_matches'] += 1
                student_results['correct'] += 1
                results['confidences'].append(confidence)
            elif matched_id is not None:
                results['incorrect_matches'] += 1
                student_results['incorrect'] += 1
                print(f"  MISMATCH: {student_id} recognized as {matched_id} (conf={confidence:.3f})")
            else:
                results['no_match'] += 1
                student_results['no_match'] += 1

        results['per_student'][student_id] = student_results

    if results['total_attempts'] > 0:
        accuracy = results['correct_matches'] / results['total_attempts'] * 100
        far = results['incorrect_matches'] / results['total_attempts'] * 100
        frr = results['no_match'] / results['total_attempts'] * 100
        times = results['recognition_times_ms']

        print(f"\n  Total recognition attempts: {results['total_attempts']}")
        print(f"  Correct matches (TP):       {results['correct_matches']}")
        print(f"  Incorrect matches (FP):     {results['incorrect_matches']}")
        print(f"  No match (FN):              {results['no_match']}")
        print(f"  -----------------------------------------")
        print(f"  Recognition accuracy:       {accuracy:.1f}%")
        print(f"  False Acceptance Rate:      {far:.1f}%")
        print(f"  False Rejection Rate:       {frr:.1f}%")

        if results['confidences']:
            confs = results['confidences']
            print(f"\n  Confidence scores (correct matches):")
            print(f"    Mean:    {np.mean(confs):.3f} ({np.mean(confs)*100:.1f}%)")
            print(f"    Median:  {np.median(confs):.3f}")
            print(f"    Min:     {np.min(confs):.3f}")
            print(f"    Max:     {np.max(confs):.3f}")
            print(f"    Std:     {np.std(confs):.3f}")

        print(f"\n  Recognition latency:")
        print(f"    Mean:    {np.mean(times):.0f} ms")
        print(f"    Median:  {np.median(times):.0f} ms")
        print(f"    Min:     {np.min(times):.0f} ms")
        print(f"    Max:     {np.max(times):.0f} ms")

        print(f"\n  Per-student breakdown:")
        for sid, sr in results['per_student'].items():
            rate = sr['correct'] / sr['total'] * 100 if sr['total'] > 0 else 0
            print(f"    {sid}: {sr['correct']}/{sr['total']} correct ({rate:.0f}%)")

    return results


def test_clahe_impact(recognizer, student_images):
    """Test 3: Compare recognition with and without CLAHE preprocessing."""
    print("\n" + "="*60)
    print("TEST 3: CLAHE Preprocessing Impact")
    print("="*60)

    results = {
        'with_clahe': {'correct': 0, 'total': 0, 'confidences': []},
        'without_clahe': {'correct': 0, 'total': 0, 'confidences': []}
    }

    for student_id, images in student_images.items():
        for img_path in images:
            # Test with original image (bypassing CLAHE)
            results['without_clahe']['total'] += 1
            matched_id, confidence = recognizer.recognize_face(img_path)
            if matched_id == student_id:
                results['without_clahe']['correct'] += 1
                results['without_clahe']['confidences'].append(confidence)

            # Test with CLAHE-enhanced image
            enhanced_path = recognizer._preprocess_image(img_path)
            results['with_clahe']['total'] += 1
            matched_id2, confidence2 = recognizer.recognize_face(enhanced_path)
            if matched_id2 == student_id:
                results['with_clahe']['correct'] += 1
                results['with_clahe']['confidences'].append(confidence2)

            # Cleanup temp file
            if enhanced_path != str(img_path) and os.path.exists(enhanced_path):
                os.remove(enhanced_path)

    for label, data in results.items():
        if data['total'] > 0:
            acc = data['correct'] / data['total'] * 100
            avg_conf = np.mean(data['confidences']) if data['confidences'] else 0
            print(f"\n  {label}:")
            print(f"    Accuracy:         {acc:.1f}% ({data['correct']}/{data['total']})")
            print(f"    Avg confidence:   {avg_conf:.3f}")

    return results


def test_lighting_robustness(detector, recognizer, student_images):
    """Test 4: Robustness under simulated lighting variations."""
    print("\n" + "="*60)
    print("TEST 4: Lighting Condition Robustness")
    print("="*60)

    conditions = {
        'original': lambda img: img,
        'bright (+50)': lambda img: cv2.convertScaleAbs(img, alpha=1.0, beta=50),
        'bright (+100)': lambda img: cv2.convertScaleAbs(img, alpha=1.0, beta=100),
        'dark (-50)': lambda img: cv2.convertScaleAbs(img, alpha=1.0, beta=-50),
        'dark (-100)': lambda img: cv2.convertScaleAbs(img, alpha=1.0, beta=-100),
        'low contrast': lambda img: cv2.convertScaleAbs(img, alpha=0.5, beta=0),
        'high contrast': lambda img: cv2.convertScaleAbs(img, alpha=1.5, beta=0),
        'gaussian noise': lambda img: np.clip(img.astype(np.float32) + np.random.normal(0, 25, img.shape), 0, 255).astype(np.uint8),
    }

    results = {}
    temp_dir = Config.UPLOAD_FOLDER / 'temp'
    temp_dir.mkdir(parents=True, exist_ok=True)

    for condition_name, transform_fn in conditions.items():
        correct = 0
        total = 0
        detected = 0
        confidences = []

        for student_id, images in student_images.items():
            for img_path in images:
                img = cv2.imread(str(img_path))
                if img is None:
                    continue

                # Apply lighting transformation
                transformed = transform_fn(img.copy())

                # Save transformed image temporarily
                temp_path = temp_dir / f"test_{condition_name.replace(' ', '_')}_{datetime.now().timestamp()}.jpg"
                cv2.imwrite(str(temp_path), transformed)

                total += 1

                # Test detection
                faces = detector.detect_faces(transformed)
                if len(faces) > 0:
                    detected += 1

                # Test recognition
                matched_id, confidence = recognizer.recognize_face(temp_path)
                if matched_id == student_id:
                    correct += 1
                    confidences.append(confidence)

                # Cleanup
                if temp_path.exists():
                    os.remove(str(temp_path))

        if total > 0:
            results[condition_name] = {
                'total': total,
                'detected': detected,
                'correct': correct,
                'detection_rate': detected / total * 100,
                'recognition_rate': correct / total * 100,
                'avg_confidence': np.mean(confidences) if confidences else 0
            }

    print(f"\n  {'Condition':<20} {'Det.Rate':>10} {'Rec.Rate':>10} {'Avg.Conf':>10} {'N':>5}")
    print(f"  {'-'*55}")
    for cond, data in results.items():
        print(f"  {cond:<20} {data['detection_rate']:>9.1f}% {data['recognition_rate']:>9.1f}% {data['avg_confidence']:>9.3f} {data['total']:>5}")

    return results


def test_threshold_sensitivity(recognizer, student_images):
    """Test 5: Impact of different recognition thresholds on accuracy."""
    print("\n" + "="*60)
    print("TEST 5: Threshold Sensitivity Analysis")
    print("="*60)

    thresholds = [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]
    original_threshold = recognizer.threshold

    results = {}

    # First, collect all raw distances
    all_matches = []  # (student_id, matched_id, distance)

    for student_id, images in student_images.items():
        for img_path in images:
            # Get the raw embedding and compute distances manually
            try:
                from deepface import DeepFace
                embedding_objs = DeepFace.represent(
                    img_path=str(img_path),
                    model_name=recognizer.model_name,
                    enforce_detection=False,
                    detector_backend='opencv'
                )
                if not embedding_objs:
                    continue

                input_emb = np.array(embedding_objs[0]["embedding"])

                best_match = None
                best_distance = float('inf')

                for sid, data in recognizer.face_database.items():
                    stored_embeddings = data.get('embeddings', [data['embedding']])
                    for stored_emb in stored_embeddings:
                        dist = recognizer._cosine_distance(input_emb, np.array(stored_emb))
                        if dist < best_distance:
                            best_distance = dist
                            best_match = sid

                all_matches.append((student_id, best_match, best_distance))
            except Exception as e:
                continue

    print(f"\n  Collected {len(all_matches)} match attempts")
    print(f"\n  {'Threshold':>10} {'Accuracy':>10} {'FAR':>10} {'FRR':>10} {'F1':>10}")
    print(f"  {'-'*50}")

    for threshold in thresholds:
        tp = fp = fn = tn = 0

        for true_id, matched_id, distance in all_matches:
            if distance < threshold:
                # System says match
                if matched_id == true_id:
                    tp += 1
                else:
                    fp += 1
            else:
                # System says no match
                fn += 1  # Missed the true identity

        total = tp + fp + fn
        accuracy = tp / total * 100 if total > 0 else 0
        far = fp / (fp + tn + 1) * 100  # +1 to avoid division by zero
        frr = fn / (tp + fn) * 100 if (tp + fn) > 0 else 0

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

        results[threshold] = {
            'tp': tp, 'fp': fp, 'fn': fn,
            'accuracy': accuracy, 'far': far, 'frr': frr, 'f1': f1
        }

        print(f"  {threshold:>10.2f} {accuracy:>9.1f}% {far:>9.1f}% {frr:>9.1f}% {f1:>9.3f}")

    # Restore original threshold
    recognizer.threshold = original_threshold

    return results


def test_embedding_count_impact(recognizer, student_images):
    """Test 6: Impact of number of stored embeddings on recognition accuracy."""
    print("\n" + "="*60)
    print("TEST 6: Multi-Embedding Impact Analysis")
    print("="*60)

    results = {}

    for student_id, data in recognizer.face_database.items():
        embeddings = data.get('embeddings', [data['embedding']])
        results[student_id] = {
            'num_embeddings': len(embeddings),
        }

    print(f"\n  Enrolled students: {len(results)}")
    embedding_counts = [v['num_embeddings'] for v in results.values()]
    if embedding_counts:
        print(f"  Total embeddings:  {sum(embedding_counts)}")
        print(f"  Avg per student:   {np.mean(embedding_counts):.1f}")
        print(f"  Min per student:   {min(embedding_counts)}")
        print(f"  Max per student:   {max(embedding_counts)}")

    print(f"\n  Distribution:")
    for count in sorted(set(embedding_counts)):
        num_students = embedding_counts.count(count)
        print(f"    {count} embedding(s): {num_students} student(s)")

    return results


def generate_summary_report(all_results, output_path):
    """Generate a CSV summary report of all test results."""
    print("\n" + "="*60)
    print("GENERATING SUMMARY REPORT")
    print("="*60)

    report = {
        'test_date': datetime.now().isoformat(),
        'model': 'Facenet512',
        'threshold': Config.FACE_RECOGNITION_THRESHOLD,
        'detector': 'Haar Cascade (OpenCV)',
    }

    # Detection results
    if 'detection' in all_results:
        det = all_results['detection']
        report['detection_rate'] = f"{det['faces_detected']/det['total_images']*100:.1f}%" if det['total_images'] > 0 else 'N/A'
        report['avg_detection_time_ms'] = f"{np.mean(det['detection_times_ms']):.1f}" if det['detection_times_ms'] else 'N/A'

    # Recognition results
    if 'recognition' in all_results:
        rec = all_results['recognition']
        if rec['total_attempts'] > 0:
            report['recognition_accuracy'] = f"{rec['correct_matches']/rec['total_attempts']*100:.1f}%"
            report['false_acceptance_rate'] = f"{rec['incorrect_matches']/rec['total_attempts']*100:.1f}%"
            report['false_rejection_rate'] = f"{rec['no_match']/rec['total_attempts']*100:.1f}%"
            report['avg_recognition_time_ms'] = f"{np.mean(rec['recognition_times_ms']):.0f}"
            if rec['confidences']:
                report['avg_confidence'] = f"{np.mean(rec['confidences']):.3f}"

    # Save report
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"  Report saved to: {output_path}")

    # Print summary
    print(f"\n  SUMMARY:")
    for key, value in report.items():
        print(f"    {key}: {value}")

    return report


def main():
    print("="*60)
    print("ATTENDIFY - Face Recognition Performance Evaluation")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Model: Facenet512 via DeepFace")
    print(f"Detector: OpenCV Haar Cascade")
    print(f"Threshold: {Config.FACE_RECOGNITION_THRESHOLD}")
    print("="*60)

    # Initialize components
    print("\nInitializing face detector...")
    detector = FaceDetector()

    print("Initializing face recognizer...")
    recognizer = FaceRecognizer()

    print(f"Enrolled students in database: {len(recognizer.face_database)}")

    # Collect test images
    student_images = collect_enrollment_images()
    total_images = sum(len(imgs) for imgs in student_images.values())
    print(f"Found {len(student_images)} students with {total_images} images")

    if not student_images:
        print("\nERROR: No student images found. Please enroll students first.")
        return

    # Run all tests
    all_results = {}

    all_results['detection'] = test_detection_performance(detector, student_images)
    all_results['recognition'] = test_recognition_accuracy(recognizer, student_images)
    all_results['clahe'] = test_clahe_impact(recognizer, student_images)
    all_results['lighting'] = test_lighting_robustness(detector, recognizer, student_images)
    all_results['threshold'] = test_threshold_sensitivity(recognizer, student_images)
    all_results['embeddings'] = test_embedding_count_impact(recognizer, student_images)

    # Generate report
    output_dir = Path('tests/results')
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    generate_summary_report(all_results, report_path)

    print("\n" + "="*60)
    print("ALL TESTS COMPLETE")
    print("="*60)


if __name__ == '__main__':
    main()
