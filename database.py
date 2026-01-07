from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()

class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    student_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True)
    phone = Column(String(20))
    face_encoding_path = Column(String(255))  # Path to stored face encoding
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    attendance_records = relationship('Attendance', back_populates='student')
    course_enrollments = relationship('CourseEnrollment', back_populates='student')

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }

class Attendance(Base):
    __tablename__ = 'attendance'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=True)  # Can be null for legacy records
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    confidence = Column(String(10))  # Recognition confidence score
    image_path = Column(String(255))  # Path to captured image
    status = Column(String(20), default='present')  # present, late, etc.
    week_number = Column(Integer, nullable=True)  # Week 1-14

    # Relationships
    student = relationship('Student', back_populates='attendance_records')
    course = relationship('Course', back_populates='attendance_records')

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student.student_id if self.student else None,
            'student_name': self.student.name if self.student else None,
            'course_code': self.course.course_code if self.course else None,
            'course_name': self.course.course_name if self.course else None,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'confidence': self.confidence,
            'status': self.status,
            'week_number': self.week_number
        }

class Course(Base):
    __tablename__ = 'courses'

    id = Column(Integer, primary_key=True)
    course_code = Column(String(50), unique=True, nullable=False)
    course_name = Column(String(200), nullable=False)
    start_time = Column(Time, nullable=False)  # e.g., 06:00:00
    end_time = Column(Time, nullable=False)    # e.g., 08:00:00
    days_of_week = Column(String(50))  # e.g., "Mon,Wed,Fri" or "Mon,Tue,Wed,Thu,Fri"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    enrollments = relationship('CourseEnrollment', back_populates='course')
    attendance_records = relationship('Attendance', back_populates='course')

    def to_dict(self):
        return {
            'id': self.id,
            'course_code': self.course_code,
            'course_name': self.course_name,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'days_of_week': self.days_of_week,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class CourseEnrollment(Base):
    __tablename__ = 'course_enrollments'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    enrolled_date = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student = relationship('Student', back_populates='course_enrollments')
    course = relationship('Course', back_populates='enrollments')

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student.student_id if self.student else None,
            'student_name': self.student.name if self.student else None,
            'course_id': self.course_id,
            'course_code': self.course.course_code if self.course else None,
            'course_name': self.course.course_name if self.course else None,
            'enrolled_date': self.enrolled_date.isoformat() if self.enrolled_date else None
        }

class Admin(Base):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    email = Column(String(100), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }

# Database setup
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=Config.DEBUG)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
