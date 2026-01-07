import os
import cv2
import base64
import io
from flask import Flask, render_template, request, jsonify, Response, send_from_directory, send_file
from flask_cors import CORS
from datetime import datetime
from pathlib import Path
import numpy as np
from sqlalchemy import func, or_
import pandas as pd
from werkzeug.utils import secure_filename

from config import Config
from database import init_db, get_db, Student, Attendance, Course, CourseEnrollment
from face_detector import FaceDetector
from face_recognizer import FaceRecognizer

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize face detection and recognition
face_detector = FaceDetector()
face_recognizer = FaceRecognizer()

# Global variable for video stream - for Mark Attendance tab
cameras = {}  # Dictionary to store multiple camera instances
last_detected_students = {}  # Track recently detected students to avoid duplicates
from datetime import datetime, timedelta

def get_camera(camera_index=None):
    """Get or initialize camera with specified index"""
    global cameras

    if camera_index is None:
        camera_index = Config.CAMERA_INDEX

    camera_index = int(camera_index)

    # If camera already exists and is opened, return it
    if camera_index in cameras and cameras[camera_index] is not None:
        if cameras[camera_index].isOpened():
            return cameras[camera_index]
        else:
            # Camera was closed, remove it
            cameras[camera_index].release()
            del cameras[camera_index]

    # Create new camera instance
    camera = cv2.VideoCapture(camera_index)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, Config.FRAME_WIDTH)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.FRAME_HEIGHT)

    if camera.isOpened():
        cameras[camera_index] = camera
        return camera
    else:
        return None

def get_active_course(db):
    """Get currently active course based on current time and day"""
    current_time = datetime.now()
    current_day = current_time.strftime('%a')  # Mon, Tue, Wed, etc.
    current_time_only = current_time.time()

    # Find courses that are active right now
    courses = db.query(Course).filter(
        Course.is_active == True,
        Course.start_time <= current_time_only,
        Course.end_time >= current_time_only
    ).all()

    # Filter by day of week
    for course in courses:
        if course.days_of_week and current_day in course.days_of_week:
            return course

    return None

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

@app.route('/test')
def test():
    """Test page for debugging"""
    return send_from_directory('.', 'test_courses.html')

@app.route('/api/students', methods=['GET'])
def get_students():
    """Get all students"""
    db = next(get_db())
    students = db.query(Student).filter(Student.is_active == True).all()
    return jsonify([student.to_dict() for student in students])

@app.route('/api/students', methods=['POST'])
def create_student():
    """Create a new student"""
    data = request.json
    db = next(get_db())

    try:
        student = Student(
            student_id=data['student_id'],
            name=data['name'],
            email=data.get('email'),
            phone=data.get('phone')
        )
        db.add(student)
        db.commit()
        db.refresh(student)

        return jsonify({'success': True, 'student': student.to_dict()}), 201
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/students/<int:student_id>/enroll', methods=['POST'])
def enroll_student_face(student_id):
    """Enroll student face"""
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image provided'}), 400

    db = next(get_db())
    student = db.query(Student).filter(Student.id == student_id).first()

    if not student:
        return jsonify({'success': False, 'error': 'Student not found'}), 404

    try:
        # Save uploaded image
        image_file = request.files['image']
        student_folder = Config.UPLOAD_FOLDER / student.student_id
        student_folder.mkdir(parents=True, exist_ok=True)

        image_path = student_folder / f"{student.student_id}_enrollment.jpg"
        image_file.save(str(image_path))

        # Enroll face
        success = face_recognizer.enroll_face(student.student_id, image_path)

        if success:
            student.face_encoding_path = str(image_path)
            db.commit()
            return jsonify({'success': True, 'message': 'Face enrolled successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to enroll face'}), 400

    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/students/bulk-import', methods=['POST'])
def bulk_import_students():
    """Bulk import students from Excel file"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    
    file = request.files['file']
    if not file.filename:
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        return jsonify({'success': False, 'error': 'Invalid file format. Please upload Excel file (.xlsx or .xls)'}), 400
    
    # Get optional course_id for auto-enrollment
    course_id = request.form.get('course_id')
    
    try:
        # Read Excel file
        df = pd.read_excel(file)
        
        # Validate required columns
        required_cols = ['Student ID', 'Full Name']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            return jsonify({
                'success': False, 
                'error': f'Missing required columns: {", ".join(missing_cols)}'
            }), 400
        
        db = next(get_db())
        
        # Validate course if provided
        course = None
        if course_id:
            course = db.query(Course).filter(Course.id == int(course_id)).first()
            if not course:
                return jsonify({'success': False, 'error': 'Invalid course selected'}), 400
        
        imported = 0
        enrolled = 0
        errors = []
        skipped = 0
        
        for index, row in df.iterrows():
            try:
                # Skip empty rows
                if pd.isna(row['Student ID']) or pd.isna(row['Full Name']):
                    skipped += 1
                    continue
                
                student_id = str(row['Student ID']).strip()
                name = str(row['Full Name']).strip()
                
                # Check if student already exists
                existing = db.query(Student).filter(
                    Student.student_id == student_id
                ).first()
                
                if existing:
                    errors.append(f"Row {index + 2}: Student ID '{student_id}' already exists")
                    # Still try to enroll if course is selected and not already enrolled
                    if course:
                        existing_enrollment = db.query(CourseEnrollment).filter(
                            CourseEnrollment.student_id == existing.id,
                            CourseEnrollment.course_id == course.id
                        ).first()
                        if not existing_enrollment:
                            enrollment = CourseEnrollment(
                                student_id=existing.id,
                                course_id=course.id
                            )
                            db.add(enrollment)
                            enrolled += 1
                    continue
                
                # Create new student
                student = Student(
                    student_id=student_id,
                    name=name,
                    email=str(row.get('Email', '')) if not pd.isna(row.get('Email')) else '',
                    phone=str(row.get('Phone', '')) if not pd.isna(row.get('Phone')) else ''
                )
                db.add(student)
                db.flush()  # Get the student ID
                imported += 1
                
                # Auto-enroll in course if selected
                if course:
                    enrollment = CourseEnrollment(
                        student_id=student.id,
                        course_id=course.id
                    )
                    db.add(enrollment)
                    enrolled += 1
                
            except Exception as e:
                errors.append(f"Row {index + 2}: {str(e)}")
        
        db.commit()
        
        message = f'Successfully imported {imported} students'
        if enrolled > 0:
            message += f' and enrolled {enrolled} in {course.course_code}'
        if skipped > 0:
            message += f', skipped {skipped} empty rows'
        
        return jsonify({
            'success': True,
            'imported': imported,
            'enrolled': enrolled,
            'skipped': skipped,
            'errors': errors,
            'message': message
        })
        
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'error': f'Failed to process file: {str(e)}'}), 400

@app.route('/api/students/export-template', methods=['GET'])
def export_template():
    """Download Excel template for bulk import"""
    try:
        # Create sample DataFrame
        df = pd.DataFrame({
            'Student ID': ['STU001', 'STU002', 'STU003'],
            'Full Name': ['John Doe', 'Jane Smith', 'Mike Johnson'],
            'Email': ['john@university.edu', 'jane@university.edu', 'mike@university.edu'],
            'Phone': ['+1234567890', '+1234567891', '+1234567892']
        })
        
        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Students')
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Students']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='student_import_template.xlsx'
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/students/search', methods=['GET'])
def search_students():
    """Search students by name or ID with optional filters"""
    query = request.args.get('q', '').strip()
    course_id = request.args.get('course_id')
    no_photo = request.args.get('no_photo') == 'true'
    
    db = next(get_db())
    students_query = db.query(Student).filter(Student.is_active == True)
    
    # Filter by search query
    if query:
        students_query = students_query.filter(
            or_(
                Student.name.ilike(f'%{query}%'),
                Student.student_id.ilike(f'%{query}%')
            )
        )
    
    # Filter by course enrollment
    if course_id:
        students_query = students_query.join(CourseEnrollment).filter(
            CourseEnrollment.course_id == int(course_id),
            CourseEnrollment.is_active == True
        )
    
    # Filter students without face photos
    if no_photo:
        students_query = students_query.filter(Student.face_encoding_path == None)
    
    students = students_query.all()
    
    result = []
    for s in students:
        # Get enrolled courses for this student
        enrollments = db.query(CourseEnrollment).filter(
            CourseEnrollment.student_id == s.id,
            CourseEnrollment.is_active == True
        ).all()
        
        courses = []
        for enrollment in enrollments:
            course = db.query(Course).filter(Course.id == enrollment.course_id).first()
            if course:
                courses.append({
                    'id': course.id,
                    'code': course.course_code,
                    'name': course.course_name
                })
        
        result.append({
            'id': s.id,
            'student_id': s.student_id,
            'name': s.name,
            'email': s.email or '',
            'phone': s.phone or '',
            'has_photo': s.face_encoding_path is not None,
            'courses': courses
        })
    
    return jsonify({
        'success': True,
        'students': result,
        'count': len(result)
    })

@app.route('/api/attendance', methods=['GET'])

def get_attendance():
    """Get attendance records"""
    db = next(get_db())
    date = request.args.get('date')

    query = db.query(Attendance)

    if date:
        try:
            date_obj = datetime.fromisoformat(date)
            query = query.filter(Attendance.timestamp >= date_obj)
        except ValueError:
            pass

    records = query.order_by(Attendance.timestamp.desc()).limit(100).all()
    return jsonify([record.to_dict() for record in records])

@app.route('/api/attendance/live', methods=['GET'])
def get_live_attendance():
    """Get live attendance for a specific course"""
    db = next(get_db())
    course_id = request.args.get('course_id')

    if not course_id:
        return jsonify({'success': False, 'error': 'Course ID is required'}), 400

    try:
        # Get the course
        course = db.query(Course).filter(Course.id == int(course_id)).first()
        if not course:
            return jsonify({'success': False, 'error': 'Course not found'}), 404

        # Get all students enrolled in this course
        enrollments = db.query(CourseEnrollment).filter(
            CourseEnrollment.course_id == int(course_id)
        ).all()

        # Get today's date
        today = datetime.now().date()

        # Build the response with attendance status
        students_status = []
        for enrollment in enrollments:
            student = db.query(Student).filter(Student.id == enrollment.student_id).first()
            if not student:
                continue

            # Check if student has attendance marked today for this course
            attendance_today = db.query(Attendance).filter(
                Attendance.student_id == student.id,
                Attendance.course_id == int(course_id),
                func.date(Attendance.timestamp) == today
            ).first()

            students_status.append({
                'student_id': student.student_id,
                'student_name': student.name,
                'status': 'present' if attendance_today else 'absent',
                'marked_at': attendance_today.timestamp.isoformat() if attendance_today else None,
                'confidence': attendance_today.confidence if attendance_today else None
            })

        return jsonify({
            'success': True,
            'course_code': course.course_code,
            'course_name': course.course_name,
            'students': students_status
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/attendance/mark', methods=['POST'])
def mark_attendance():
    """Mark attendance from uploaded image"""
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image provided'}), 400

    try:
        # Save temporary image
        image_file = request.files['image']
        temp_path = Config.UPLOAD_FOLDER / 'temp' / f"temp_{datetime.now().timestamp()}.jpg"
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        image_file.save(str(temp_path))

        # Read image
        frame = cv2.imread(str(temp_path))

        # Detect faces
        faces = face_detector.detect_faces(frame)

        if not faces:
            return jsonify({'success': False, 'error': 'No faces detected'}), 400

        db = next(get_db())
        marked_students = []

        # Process each detected face
        for i, bbox in enumerate(faces):
            # Extract face
            face_img = face_detector.extract_face(frame, bbox)
            face_path = Config.UPLOAD_FOLDER / 'temp' / f"face_{datetime.now().timestamp()}_{i}.jpg"
            cv2.imwrite(str(face_path), face_img)

            # Recognize face
            student_id, confidence = face_recognizer.recognize_face(face_path)

            if student_id:
                # Get student from database
                student = db.query(Student).filter(Student.student_id == student_id).first()

                if student:
                    # Check if already marked today
                    today = datetime.now().date()
                    existing = db.query(Attendance).filter(
                        Attendance.student_id == student.id,
                        Attendance.timestamp >= datetime.combine(today, datetime.min.time())
                    ).first()

                    if not existing:
                        # Mark attendance
                        attendance = Attendance(
                            student_id=student.id,
                            confidence=f"{confidence:.2%}",
                            image_path=str(face_path)
                        )
                        db.add(attendance)
                        marked_students.append({
                            'name': student.name,
                            'student_id': student.student_id,
                            'confidence': f"{confidence:.2%}"
                        })

        db.commit()

        return jsonify({
            'success': True,
            'marked_students': marked_students,
            'total_faces': len(faces)
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

def generate_frames(camera_index=None, course_id=None):
    """Generate video frames for live stream with automatic face detection"""
    global last_detected_students
    cam = get_camera(camera_index)

    if cam is None:
        # Return error frame if camera not available
        error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(error_frame, f'Camera {camera_index} not available', (50, 240),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        ret, buffer = cv2.imencode('.jpg', error_frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        return

    frame_count = 0

    while True:
        success, frame = cam.read()
        if not success:
            break

        # Process every 10th frame for face recognition (performance optimization)
        if frame_count % 10 == 0:
            # Detect faces
            faces = face_detector.detect_faces(frame)

            # Try to recognize each face
            labels = []
            for bbox in faces:
                # Extract and save face temporarily
                face_img = face_detector.extract_face(frame, bbox)
                if face_img.size == 0:
                    labels.append("Unknown")
                    continue

                # Save temporarily for recognition
                temp_path = Config.UPLOAD_FOLDER / 'temp' / f"detect_{datetime.now().timestamp()}.jpg"
                temp_path.parent.mkdir(parents=True, exist_ok=True)
                cv2.imwrite(str(temp_path), face_img)

                # Recognize
                student_id, confidence = face_recognizer.recognize_face(temp_path)
                print(f"Face recognition result: student_id={student_id}, confidence={confidence}")

                if student_id:
                    # Check if already detected recently (within 30 seconds)
                    current_time = datetime.now()
                    if student_id in last_detected_students:
                        last_seen = last_detected_students[student_id]
                        if (current_time - last_seen).seconds < 30:
                            labels.append(f"{student_id} (Recent)")
                            continue

                    # Mark attendance automatically with course schedule check
                    try:
                        db = next(get_db())
                        student = db.query(Student).filter(Student.student_id == student_id).first()
                        print(f"Database lookup: student_id={student_id}, student_found={student is not None}")

                        if student:
                            print(f"Student found: {student.name} (ID: {student.student_id})")
                            # Use provided course_id or auto-detect based on time
                            if course_id:
                                # Use selected course from UI
                                active_course = db.query(Course).filter(Course.id == int(course_id)).first()
                            else:
                                # Auto-detect based on current time (legacy behavior)
                                active_course = get_active_course(db)

                            if not active_course:
                                # No active course selected or detected
                                labels.append(f"{student.name} (No Session)")
                                last_detected_students[student_id] = current_time
                                continue

                            # Check if student is enrolled in this course
                            enrollment = db.query(CourseEnrollment).filter(
                                CourseEnrollment.student_id == student.id,
                                CourseEnrollment.course_id == active_course.id
                            ).first()

                            if not enrollment:
                                # Student not enrolled in this course
                                labels.append(f"{student.name} (Not Enrolled)")
                                last_detected_students[student_id] = current_time
                                continue

                            # Check if already marked for THIS COURSE today
                            today = current_time.date()
                            existing = db.query(Attendance).filter(
                                Attendance.student_id == student.id,
                                Attendance.course_id == active_course.id,
                                Attendance.timestamp >= datetime.combine(today, datetime.min.time())
                            ).first()

                            if not existing:
                                # Mark attendance for this specific course
                                attendance = Attendance(
                                    student_id=student.id,
                                    course_id=active_course.id,
                                    confidence=f"{confidence:.2%}",
                                    image_path=str(temp_path)
                                )
                                db.add(attendance)
                                db.commit()

                                # Update last detected time
                                last_detected_students[student_id] = current_time
                                labels.append(f"{student.name} ✓")
                                print(f"✓ Attendance marked: {student.name} for {active_course.course_code} ({confidence:.2%})")
                            else:
                                labels.append(f"{student.name} (Done)")
                                last_detected_students[student_id] = current_time
                        else:
                            labels.append("Unknown")
                    except Exception as e:
                        print(f"Error marking attendance: {e}")
                        labels.append("Error")
                else:
                    labels.append("Unknown")

            # Draw bounding boxes with labels
            frame = face_detector.draw_faces(frame, faces, labels)
        else:
            # Just detect and draw boxes (no recognition)
            faces = face_detector.detect_faces(frame)
            frame = face_detector.draw_faces(frame, faces)

        frame_count += 1

        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Course Management API Endpoints
@app.route('/api/courses', methods=['GET'])
def get_courses():
    """Get all courses"""
    db = next(get_db())
    courses = db.query(Course).filter(Course.is_active == True).all()
    return jsonify([course.to_dict() for course in courses])

@app.route('/api/courses', methods=['POST'])
def create_course():
    """Create a new course"""
    data = request.json
    db = next(get_db())

    try:
        from datetime import time
        # Parse time strings (e.g., "06:00" or "06:00:00")
        start_parts = data['start_time'].split(':')
        end_parts = data['end_time'].split(':')

        start_time = time(int(start_parts[0]), int(start_parts[1]))
        end_time = time(int(end_parts[0]), int(end_parts[1]))

        course = Course(
            course_code=data['course_code'],
            course_name=data['course_name'],
            start_time=start_time,
            end_time=end_time,
            days_of_week=data.get('days_of_week', '')  # e.g., "Mon,Wed,Fri"
        )
        db.add(course)
        db.commit()
        db.refresh(course)

        return jsonify({'success': True, 'course': course.to_dict()}), 201
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/courses/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    """Update a course"""
    data = request.json
    db = next(get_db())

    try:
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            return jsonify({'success': False, 'error': 'Course not found'}), 404

        from datetime import time
        if 'start_time' in data:
            start_parts = data['start_time'].split(':')
            course.start_time = time(int(start_parts[0]), int(start_parts[1]))

        if 'end_time' in data:
            end_parts = data['end_time'].split(':')
            course.end_time = time(int(end_parts[0]), int(end_parts[1]))

        if 'course_code' in data:
            course.course_code = data['course_code']
        if 'course_name' in data:
            course.course_name = data['course_name']
        if 'days_of_week' in data:
            course.days_of_week = data['days_of_week']
        if 'is_active' in data:
            course.is_active = data['is_active']

        db.commit()
        return jsonify({'success': True, 'course': course.to_dict()})
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/courses/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    """Delete a course (soft delete)"""
    db = next(get_db())

    try:
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            return jsonify({'success': False, 'error': 'Course not found'}), 404

        course.is_active = False
        db.commit()
        return jsonify({'success': True, 'message': 'Course deleted successfully'})
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

# Course Enrollment API Endpoints
@app.route('/api/enrollments', methods=['GET'])
def get_enrollments():
    """Get all course enrollments"""
    db = next(get_db())
    course_id = request.args.get('course_id')
    student_id = request.args.get('student_id')

    query = db.query(CourseEnrollment)

    if course_id:
        query = query.filter(CourseEnrollment.course_id == course_id)
    if student_id:
        # student_id here is the internal database ID, not student_id string
        query = query.filter(CourseEnrollment.student_id == student_id)

    enrollments = query.all()
    return jsonify([enrollment.to_dict() for enrollment in enrollments])

@app.route('/api/enrollments', methods=['POST'])
def create_enrollment():
    """Enroll a student in a course"""
    data = request.json
    db = next(get_db())

    try:
        # Check if already enrolled
        existing = db.query(CourseEnrollment).filter(
            CourseEnrollment.student_id == data['student_id'],
            CourseEnrollment.course_id == data['course_id']
        ).first()

        if existing:
            return jsonify({'success': False, 'error': 'Student already enrolled in this course'}), 400

        enrollment = CourseEnrollment(
            student_id=data['student_id'],
            course_id=data['course_id']
        )
        db.add(enrollment)
        db.commit()
        db.refresh(enrollment)

        return jsonify({'success': True, 'enrollment': enrollment.to_dict()}), 201
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/enrollments/<int:enrollment_id>', methods=['DELETE'])
def delete_enrollment(enrollment_id):
    """Remove a student from a course"""
    db = next(get_db())

    try:
        enrollment = db.query(CourseEnrollment).filter(CourseEnrollment.id == enrollment_id).first()
        if not enrollment:
            return jsonify({'success': False, 'error': 'Enrollment not found'}), 404

        db.delete(enrollment)
        db.commit()
        return jsonify({'success': True, 'message': 'Enrollment deleted successfully'})
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

# Admin Authentication Endpoints
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Admin login"""
    from database import Admin
    data = request.json
    db = next(get_db())

    try:
        admin = db.query(Admin).filter(Admin.username == data['username']).first()

        if not admin or not admin.check_password(data['password']):
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

        if not admin.is_active:
            return jsonify({'success': False, 'error': 'Account is inactive'}), 401

        # In a production app, you would generate a JWT token here
        # For now, we'll just return success with admin info
        return jsonify({
            'success': True,
            'admin': admin.to_dict(),
            'message': 'Login successful'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/admin/create', methods=['POST'])
def create_admin():
    """Create a new admin (should be protected in production)"""
    from database import Admin
    data = request.json
    db = next(get_db())

    try:
        admin = Admin(
            username=data['username'],
            full_name=data.get('full_name'),
            email=data.get('email')
        )
        admin.set_password(data['password'])

        db.add(admin)
        db.commit()
        db.refresh(admin)

        return jsonify({'success': True, 'admin': admin.to_dict()}), 201
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

# Data Export Endpoint
@app.route('/api/export/attendance', methods=['GET'])
def export_attendance():
    """Export attendance data as CSV"""
    import csv
    from io import StringIO
    from flask import make_response

    db = next(get_db())
    course_id = request.args.get('course_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = db.query(Attendance)

    if course_id:
        query = query.filter(Attendance.course_id == course_id)
    if start_date:
        query = query.filter(Attendance.timestamp >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Attendance.timestamp <= datetime.fromisoformat(end_date))

    records = query.order_by(Attendance.timestamp.desc()).all()

    # Create CSV
    output = StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(['Student ID', 'Student Name', 'Course Code', 'Course Name',
                     'Date', 'Time', 'Confidence', 'Status'])

    # Write data
    for record in records:
        writer.writerow([
            record.student.student_id if record.student else 'N/A',
            record.student.name if record.student else 'N/A',
            record.course.course_code if record.course else 'N/A',
            record.course.course_name if record.course else 'N/A',
            record.timestamp.strftime('%Y-%m-%d') if record.timestamp else 'N/A',
            record.timestamp.strftime('%H:%M:%S') if record.timestamp else 'N/A',
            record.confidence,
            record.status
        ])

    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=attendance_export.csv'

    return response

@app.route('/api/video_feed')
def video_feed():
    """Video streaming route with automatic attendance marking"""
    camera_index = request.args.get('camera', default=Config.CAMERA_INDEX, type=int)
    course_id = request.args.get('course_id', default=None, type=int)
    return Response(generate_frames(camera_index, course_id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # Initialize database
    init_db()

    # Run Flask app
    app.run(host='0.0.0.0', port=5001, debug=Config.DEBUG)
