#!/usr/bin/env python3
"""
Initialize admin user and sample course data
Run this script once to set up the system
"""
from database import init_db, get_db, Admin, Course, CourseEnrollment, Student
from datetime import time

def create_default_admin():
    """Create default admin user"""
    db = next(get_db())

    # Check if admin already exists
    existing = db.query(Admin).filter(Admin.username == 'admin').first()

    if existing:
        print("Admin user already exists!")
        return

    # Create admin
    admin = Admin(
        username='admin',
        full_name='Administrator',
        email='admin@attendify.com'
    )
    admin.set_password('admin123')  # Change this in production!

    db.add(admin)
    db.commit()
    print("✓ Default admin user created:")
    print("  Username: admin")
    print("  Password: admin123")
    print("  (Please change the password after first login!)")

def create_sample_courses():
    """Create sample courses"""
    db = next(get_db())

    # Check if courses already exist
    existing = db.query(Course).first()
    if existing:
        print("\nCourses already exist!")
        return

    # Sample courses
    courses_data = [
        {
            'course_code': 'GIS101',
            'course_name': 'Introduction to GIS',
            'start_time': time(6, 0),  # 06:00
            'end_time': time(8, 0),     # 08:00
            'days_of_week': 'Mon,Wed,Fri'
        },
        {
            'course_code': 'CS201',
            'course_name': 'Data Structures',
            'start_time': time(9, 0),   # 09:00
            'end_time': time(11, 0),    # 11:00
            'days_of_week': 'Tue,Thu'
        },
        {
            'course_code': 'MATH301',
            'course_name': 'Linear Algebra',
            'start_time': time(14, 0),  # 14:00
            'end_time': time(16, 0),    # 16:00
            'days_of_week': 'Mon,Wed,Fri'
        }
    ]

    for course_data in courses_data:
        course = Course(**course_data)
        db.add(course)

    db.commit()
    print("\n✓ Sample courses created:")
    for course_data in courses_data:
        print(f"  - {course_data['course_code']}: {course_data['course_name']}")
        print(f"    Time: {course_data['start_time']} - {course_data['end_time']}")
        print(f"    Days: {course_data['days_of_week']}")

def main():
    print("Initializing Attendify Database...")
    print("=" * 50)

    # Initialize database tables
    init_db()
    print("✓ Database tables created\n")

    # Create default admin
    create_default_admin()

    # Create sample courses
    create_sample_courses()

    print("\n" + "=" * 50)
    print("Setup complete!")
    print("\nNext steps:")
    print("1. Run: python app.py")
    print("2. Open: http://localhost:5001")
    print("3. Go to Admin tab and login with:")
    print("   Username: admin")
    print("   Password: admin123")
    print("4. Create courses and enroll students")
    print("=" * 50)

if __name__ == '__main__':
    main()
