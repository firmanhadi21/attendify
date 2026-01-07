# Course Schedule System - Complete Guide

## Overview

The Attendify system has been upgraded with a comprehensive course schedule management system. Attendance is now tracked based on scheduled courses, ensuring students are only marked present during their actual class times.

## Key Features

### 1. Schedule-Based Attendance
- **Smart Detection**: Only detects attendance during active course periods
- **One Attendance Per Session**: Students can only be marked present once per course session
- **Time-Aware**: System checks current time and day against course schedules
- **Enrollment Verification**: Only students enrolled in the active course are marked present

### 2. Admin Module
Complete administrative interface for managing:
- **Courses**: Create, edit, and delete courses
- **Schedules**: Set time slots and days of the week
- **Enrollments**: Manage which students are enrolled in which courses
- **Data Export**: Export attendance records to CSV

## Getting Started

### Initial Setup

1. **Initialize the Database** (Already done):
```bash
python init_admin.py
```

This creates:
- Default admin user (username: `admin`, password: `admin123`)
- Three sample courses (GIS101, CS201, MATH301)

2. **Start the Application**:
```bash
python app.py
```

3. **Access the System**:
Open http://localhost:5001

### Admin Login

1. Click on the **"Admin"** tab
2. Login with:
   - **Username**: `admin`
   - **Password**: `admin123`
3. **IMPORTANT**: Change the password after first login!

## Using the Admin Module

### Course Management

#### Adding a New Course

1. Go to **Admin → Courses**
2. Click **"Add New Course"**
3. Fill in the form:
   - **Course Code**: e.g., "GIS101"
   - **Course Name**: e.g., "Introduction to GIS"
   - **Start Time**: e.g., 06:00
   - **End Time**: e.g., 08:00
   - **Days of Week**: Check the days this course meets
4. Click **"Save Course"**

**Example Course**:
- Code: GIS101
- Name: Introduction to GIS
- Time: 06:00 - 08:00
- Days: Monday, Wednesday, Friday

#### Editing a Course

1. Find the course in the list
2. Click **"Edit"**
3. Modify the details
4. Click **"Save Course"**

#### Deleting a Course

1. Find the course in the list
2. Click **"Delete"**
3. Confirm the deletion

**Note**: Deletion is a "soft delete" - the course is marked inactive but data is preserved.

### Student Enrollment Management

#### Enrolling a Student in a Course

1. Go to **Admin → Enrollments**
2. Click **"Enroll Student in Course"**
3. Select:
   - **Student**: Choose from enrolled students
   - **Course**: Choose from active courses
4. Click **"Enroll"**

#### Viewing Enrollments

The enrollments table shows:
- Student ID
- Student Name
- Course Code
- Course Name
- Enrollment Date

#### Removing an Enrollment

1. Find the enrollment in the list
2. Click **"Remove"**
3. Confirm the removal

### Exporting Attendance Data

1. Go to **Admin → Export Data**
2. **Optional Filters**:
   - **Course**: Select a specific course or "All Courses"
   - **Start Date**: Filter from this date
   - **End Date**: Filter until this date
3. Click **"Download CSV"**

**CSV Format**:
```
Student ID, Student Name, Course Code, Course Name, Date, Time, Confidence, Status
STU001, John Doe, GIS101, Introduction to GIS, 2026-01-07, 06:15:30, 98.5%, present
```

## How Attendance Detection Works

### The Detection Flow

1. **Student Enters Classroom**: Face detected by camera in "Mark Attendance" tab
2. **Face Recognition**: System identifies the student
3. **Check Active Course**: System checks if there's a course active right now
   - Current time: 06:30 on Monday
   - Active course: GIS101 (06:00-08:00, Mon/Wed/Fri) ✓
4. **Check Enrollment**: Verifies student is enrolled in GIS101
5. **Check Duplicate**: Ensures attendance not already marked today for this course
6. **Mark Attendance**: Records attendance with course_id, timestamp, confidence

### Attendance Statuses

When a face is detected, you'll see one of these labels:

- **"Name ✓"**: Attendance successfully marked
- **"Name (Done)"**: Already marked present for this course today
- **"Name (Recent)"**: Just detected 30 seconds ago (cooldown)
- **"Name (No Class)"**: No active course right now
- **"Name (Not Enrolled)"**: Student not enrolled in the active course
- **"Unknown"**: Face not recognized

### Example Scenario

**Setup**:
- Course: GIS101 (06:00-08:00, Mon/Wed/Fri)
- Student: Alice (STU001) enrolled in GIS101
- Current: Monday, 06:30

**What Happens**:
1. Alice enters classroom at 06:30
2. Camera detects her face
3. System recognizes: "Alice (STU001)"
4. Checks: Active course is GIS101 ✓
5. Checks: Alice enrolled in GIS101 ✓
6. Checks: Not marked today ✓
7. **Result**: "Alice ✓" - Attendance marked!

**Later at 07:00**:
1. Alice detected again
2. System checks: Already marked for GIS101 today
3. **Result**: "Alice (Done)"

**At 14:00 (different time)**:
1. Alice detected
2. No active course (MATH301 is 14:00-16:00 but Alice not enrolled)
3. **Result**: "Alice (No Class)" or "Alice (Not Enrolled)"

## Database Schema

### New Tables

#### Courses
```sql
- id (primary key)
- course_code (unique, e.g., "GIS101")
- course_name (e.g., "Introduction to GIS")
- start_time (TIME, e.g., 06:00:00)
- end_time (TIME, e.g., 08:00:00)
- days_of_week (e.g., "Mon,Wed,Fri")
- is_active (boolean)
- created_at (timestamp)
```

#### CourseEnrollments
```sql
- id (primary key)
- student_id (foreign key → students.id)
- course_id (foreign key → courses.id)
- enrolled_date (timestamp)
```

#### Admins
```sql
- id (primary key)
- username (unique)
- password_hash
- full_name
- email (unique)
- created_at (timestamp)
- is_active (boolean)
```

### Updated Tables

#### Attendance (Modified)
```sql
- id (primary key)
- student_id (foreign key → students.id)
- course_id (foreign key → courses.id) ← NEW
- timestamp
- confidence
- image_path
- status
```

## API Endpoints

### Course Management

- `GET /api/courses` - List all active courses
- `POST /api/courses` - Create new course
- `PUT /api/courses/<id>` - Update course
- `DELETE /api/courses/<id>` - Delete course (soft delete)

### Enrollment Management

- `GET /api/enrollments` - List all enrollments
  - Query params: `?course_id=1` or `?student_id=1`
- `POST /api/enrollments` - Enroll student in course
- `DELETE /api/enrollments/<id>` - Remove enrollment

### Admin Authentication

- `POST /api/admin/login` - Admin login
- `POST /api/admin/create` - Create admin user

### Data Export

- `GET /api/export/attendance` - Export as CSV
  - Query params: `?course_id=1&start_date=2026-01-01&end_date=2026-01-31`

## Workflow Examples

### Complete Workflow: New Course Setup

1. **Create Course**:
   - Go to Admin → Courses
   - Add "Database Systems" (CS301)
   - Time: 10:00-12:00
   - Days: Tue, Thu

2. **Enroll Students**:
   - Go to Admin → Enrollments
   - Enroll John Doe (STU001) in CS301
   - Enroll Jane Smith (STU002) in CS301

3. **Test Attendance**:
   - Wait until Tuesday 10:00-12:00
   - Go to "Mark Attendance" tab
   - Students appear in front of camera
   - System marks: "John Doe ✓", "Jane Smith ✓"

4. **View Reports**:
   - Go to "Attendance Reports" tab
   - See attendance records with course information

5. **Export Data**:
   - Go to Admin → Export Data
   - Filter by CS301
   - Download CSV

### Typical Daily Usage

**Morning (Before Class)**:
1. Admin checks course schedule
2. Verifies students are enrolled
3. Opens "Mark Attendance" tab

**During Class (e.g., 06:00-08:00 GIS Class)**:
1. Students enter room
2. Camera automatically detects and recognizes
3. System shows: "Student Name ✓" for new attendance
4. System shows: "Student Name (Done)" for duplicates
5. Admin monitors the video feed

**After Class**:
1. Admin goes to "Attendance Reports"
2. Reviews who was marked present
3. Optionally exports to CSV

**End of Week**:
1. Admin exports all attendance data
2. Analyzes attendance patterns
3. Identifies students with low attendance

## Best Practices

### For Administrators

1. **Create Courses First**: Set up all courses before enrolling students
2. **Accurate Schedules**: Ensure start/end times match actual class times
3. **Regular Exports**: Export data weekly for backup
4. **Monitor Live**: Watch the Mark Attendance feed during class
5. **Review Daily**: Check attendance reports after each class

### For System Accuracy

1. **Good Lighting**: Ensure classroom has adequate lighting
2. **Camera Position**: Place camera where it can see faces clearly
3. **Student Photos**: Enroll students with clear, front-facing photos
4. **Network**: Ensure stable connection for continuous detection

### Security

1. **Change Default Password**: Immediately change admin password from "admin123"
2. **Limit Admin Access**: Only create admin accounts for authorized personnel
3. **Regular Backups**: Export and backup attendance data regularly
4. **Review Exports**: Check exported data for any anomalies

## Troubleshooting

### Student Not Detected During Class

**Problem**: "John Doe (No Class)" appears even during scheduled class time

**Solutions**:
1. Check current system time is correct
2. Verify course schedule in Admin → Courses
3. Ensure course days_of_week includes today
4. Check course is marked "Active"

### Student Detected But Not Enrolled

**Problem**: "Jane Smith (Not Enrolled)" appears

**Solutions**:
1. Go to Admin → Enrollments
2. Verify Jane is enrolled in the current active course
3. Enroll her if missing

### No Active Course Detected

**Problem**: All students show "(No Class)"

**Solutions**:
1. Check current time matches a course schedule
2. Verify at least one course is active now
3. Create/edit course schedules as needed

### Attendance Marked Multiple Times

**Problem**: Same student marked multiple times in one day

**Solutions**:
1. This shouldn't happen - system prevents it
2. Check database for duplicate records
3. Verify course_id is correctly linked

### Export Shows Wrong Data

**Problem**: CSV export missing records or showing incorrect course

**Solutions**:
1. Check date filters
2. Verify course filter selection
3. Ensure attendance records have course_id set

## System Requirements

- PostgreSQL database running on port 5433
- Python 3.10.18
- USB webcam for enrollment and attendance
- Modern web browser (Chrome, Firefox, Safari)

## File Structure

```
attendify/
├── app.py                    # Main application with course logic
├── database.py               # Models: Course, CourseEnrollment, Admin
├── init_admin.py            # Initialization script
├── templates/
│   └── index.html           # Admin module UI
├── static/
│   ├── css/style.css        # Admin styling
│   └── js/app.js            # Admin functionality
└── COURSE_SCHEDULE_SYSTEM.md  # This file
```

## Support

For issues or questions:
1. Check this documentation first
2. Review console logs for errors
3. Verify database connection
4. Check camera permissions

## Next Steps

1. Login to admin panel
2. Create your actual course schedules
3. Enroll all students in their courses
4. Test the attendance detection
5. Monitor and export data regularly

---

**Your course schedule-based attendance system is now fully operational!**

Access at: http://localhost:5001
Admin Login: admin / admin123 (please change!)
