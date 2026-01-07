#!/usr/bin/env python3
"""
Check if attendance records exist in database
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Attendance, Student, Course
from config import Config

# Create database connection
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
db = Session()

print("=" * 60)
print("Checking Attendance Records")
print("=" * 60)

# Count total attendance records
total_records = db.query(Attendance).count()
print(f"\nTotal attendance records: {total_records}")

if total_records > 0:
    print("\nRecent attendance records:")
    print("-" * 60)

    records = db.query(Attendance).order_by(Attendance.timestamp.desc()).limit(10).all()

    for record in records:
        student = db.query(Student).filter(Student.id == record.student_id).first()
        course = None
        if record.course_id:
            course = db.query(Course).filter(Course.id == record.course_id).first()

        print(f"ID: {record.id}")
        print(f"  Student: {student.name if student else 'Unknown'} ({student.student_id if student else 'N/A'})")
        if course:
            print(f"  Course: {course.course_code} - {course.course_name}")
        else:
            print(f"  Course: None (course_id={record.course_id})")
        print(f"  Time: {record.timestamp}")
        print(f"  Confidence: {record.confidence}")
        print(f"  Status: {record.status}")
        print("-" * 60)
else:
    print("\n⚠️  No attendance records found in database!")
    print("\nPossible reasons:")
    print("1. No students have been detected yet")
    print("2. Face detection hasn't run")
    print("3. No course session has been started")

# Check students count
student_count = db.query(Student).count()
print(f"\nTotal enrolled students: {student_count}")

# Check courses count
course_count = db.query(Course).count()
print(f"Total courses: {course_count}")

db.close()
print("\n" + "=" * 60)
