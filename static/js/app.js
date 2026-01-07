// Global variables
let enrollStream = null;
let capturedPhotoBlob = null;
let currentCourseId = null;
let currentCourseName = '';
let liveAttendanceInterval = null;

// Timezone helper - Convert UTC to UTC+7 (Jakarta/Bangkok timezone)
function formatTimeUTC7(timestamp) {
    if (!timestamp) return '-';
    const date = new Date(timestamp);
    // Add 7 hours to UTC
    const utc7Date = new Date(date.getTime() + (7 * 60 * 60 * 1000));
    return utc7Date.toLocaleTimeString('en-US', {
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

function formatDateTimeUTC7(timestamp) {
    if (!timestamp) return '-';
    const date = new Date(timestamp);
    // Add 7 hours to UTC
    const utc7Date = new Date(date.getTime() + (7 * 60 * 60 * 1000));
    return utc7Date.toLocaleString('en-US', {
        hour12: false,
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

// Tab switching
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const tabName = btn.dataset.tab;
        switchTab(tabName);
    });
});

function switchTab(tabName) {
    // Remove active class from all tabs and contents
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

    // Add active class to selected tab
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    document.getElementById(`${tabName}-tab`).classList.add('active');

    // Stop live attendance refresh when leaving reports tab
    if (liveAttendanceInterval) {
        clearInterval(liveAttendanceInterval);
        liveAttendanceInterval = null;
    }

    // Load data for specific tabs
    if (tabName === 'students') {
        loadStudents();
    } else if (tabName === 'reports') {
        loadLiveAttendance();
        // Auto-refresh every 5 seconds
        liveAttendanceInterval = setInterval(loadLiveAttendance, 5000);
    } else if (tabName === 'enroll') {
        // Auto-start webcam when entering enroll tab
        startEnrollWebcam();
    } else if (tabName === 'attendance') {
        // Load courses when entering attendance tab
        loadCoursesForAttendance();
        // Stop enrollment webcam when leaving enroll tab
        stopEnrollWebcam();
    } else {
        // Stop webcam when leaving enroll tab
        stopEnrollWebcam();
    }
}

// Attendance marking - now automatic via video stream
// No manual buttons needed - attendance is marked automatically when faces are recognized

// Student enrollment - Single step process
document.getElementById('student-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const studentId = document.getElementById('student-id').value;
    const studentName = document.getElementById('student-name').value;
    const fileInput = document.getElementById('face-upload');
    const uploadedFile = fileInput.files[0];

    // Check if photo is captured or uploaded
    if (!capturedPhotoBlob && !uploadedFile) {
        showResult('enroll-result', 'Please capture or upload a photo first!', 'error');
        return;
    }

    try {
        showResult('enroll-result', 'Enrolling student...', 'success');

        // Step 1: Create student
        const studentData = {
            student_id: studentId,
            name: studentName,
            email: null,
            phone: null
        };

        const createResponse = await fetch('/api/students', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(studentData)
        });

        const createData = await createResponse.json();

        if (!createData.success) {
            showResult('enroll-result', createData.error || 'Failed to create student', 'error');
            return;
        }

        // Step 2: Enroll face
        const formData = new FormData();
        if (capturedPhotoBlob) {
            formData.append('image', capturedPhotoBlob, 'captured_photo.jpg');
        } else if (uploadedFile) {
            formData.append('image', uploadedFile);
        }

        const enrollResponse = await fetch(`/api/students/${createData.student.id}/enroll`, {
            method: 'POST',
            body: formData
        });

        const enrollData = await enrollResponse.json();

        if (enrollData.success) {
            showResult('enroll-result', `Student "${studentName}" enrolled successfully!`, 'success');

            // Reset form
            document.getElementById('student-form').reset();
            fileInput.value = '';
            capturedPhotoBlob = null;

            // Reset camera section
            document.querySelector('.camera-section').style.display = 'block';
            document.getElementById('file-upload-section').style.display = 'none';
            document.getElementById('captured-preview').style.display = 'none';
            document.getElementById('enroll-video').style.display = 'block';
            document.getElementById('capture-photo-btn').style.display = 'inline-block';
            document.getElementById('retake-photo-btn').style.display = 'none';

            // Restart webcam for next enrollment
            startEnrollWebcam();
        } else {
            showResult('enroll-result', enrollData.error || 'Failed to enroll face', 'error');
        }
    } catch (error) {
        showResult('enroll-result', `Error: ${error.message}`, 'error');
    }
});

// Toggle between webcam and file upload
document.getElementById('toggle-upload-btn').addEventListener('click', () => {
    document.querySelector('.camera-section').style.display = 'none';
    document.getElementById('file-upload-section').style.display = 'block';
    stopEnrollWebcam();
});

document.getElementById('back-to-camera-btn').addEventListener('click', async () => {
    document.querySelector('.camera-section').style.display = 'block';
    document.getElementById('file-upload-section').style.display = 'none';
    await startEnrollWebcam();
});

// Webcam functions
async function startEnrollWebcam() {
    // Don't start if already running
    if (enrollStream) {
        return;
    }

    try {
        console.log('Requesting camera access...');
        enrollStream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 }
            }
        });

        const videoElement = document.getElementById('enroll-video');
        const placeholder = document.getElementById('camera-placeholder');

        videoElement.srcObject = enrollStream;
        console.log('Camera started successfully');

        // Hide placeholder and show video
        if (placeholder) {
            placeholder.style.display = 'none';
        }
        videoElement.style.display = 'block';
    } catch (error) {
        console.error('Camera error:', error);
        let errorMsg = 'Camera access denied. ';

        if (error.name === 'NotAllowedError') {
            errorMsg += 'Please allow camera access in your browser settings.';
        } else if (error.name === 'NotFoundError') {
            errorMsg += 'No camera found. Please connect a webcam.';
        } else if (error.name === 'NotReadableError') {
            errorMsg += 'Camera is already in use by another application.';
        } else {
            errorMsg += error.message;
        }

        showResult('enroll-result', errorMsg, 'error');

        // Update placeholder with error
        const placeholder = document.getElementById('camera-placeholder');
        if (placeholder) {
            placeholder.innerHTML = `
                <p style="margin-bottom: 20px; color: #ff6b6b;">${errorMsg}</p>
                <button type="button" id="retry-camera" class="btn btn-primary">Retry</button>
            `;
            document.getElementById('retry-camera').addEventListener('click', startEnrollWebcam);
        }
    }
}

function stopEnrollWebcam() {
    if (enrollStream) {
        console.log('Stopping camera...');
        enrollStream.getTracks().forEach(track => track.stop());
        enrollStream = null;

        const videoElement = document.getElementById('enroll-video');
        videoElement.srcObject = null;
    }
}

// Capture photo from webcam
document.getElementById('capture-photo-btn').addEventListener('click', () => {
    const video = document.getElementById('enroll-video');
    const canvas = document.getElementById('enroll-canvas');
    const preview = document.getElementById('preview-image');

    // Set canvas size to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw video frame to canvas
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert canvas to blob and show preview
    canvas.toBlob((blob) => {
        capturedPhotoBlob = blob;
        preview.src = URL.createObjectURL(blob);
        document.getElementById('captured-preview').style.display = 'block';
        document.getElementById('capture-photo-btn').style.display = 'none';
        document.getElementById('retake-photo-btn').style.display = 'inline-block';

        // Stop video stream
        stopEnrollWebcam();
        video.style.display = 'none';

        showResult('enroll-result', 'Photo captured! Fill in details and click "Enroll Student".', 'success');
    }, 'image/jpeg', 0.95);
});

// Retake photo
document.getElementById('retake-photo-btn').addEventListener('click', async () => {
    const video = document.getElementById('enroll-video');
    document.getElementById('captured-preview').style.display = 'none';
    document.getElementById('capture-photo-btn').style.display = 'inline-block';
    document.getElementById('retake-photo-btn').style.display = 'none';
    video.style.display = 'block';
    capturedPhotoBlob = null;

    // Restart webcam
    await startEnrollWebcam();
});

// Load students
async function loadStudents() {
    try {
        const response = await fetch('/api/students');
        const students = await response.json();

        const container = document.getElementById('students-list');
        container.innerHTML = '';

        if (students.length === 0) {
            container.innerHTML = '<p>No students enrolled yet.</p>';
            return;
        }

        students.forEach(student => {
            const card = document.createElement('div');
            card.className = 'student-card';
            card.innerHTML = `
                <h3>${student.name}</h3>
                <p><strong>ID:</strong> ${student.student_id}</p>
                <p><strong>Email:</strong> ${student.email || 'N/A'}</p>
                <p><strong>Phone:</strong> ${student.phone || 'N/A'}</p>
                <p><strong>Status:</strong> ${student.is_active ? 'Active' : 'Inactive'}</p>
            `;
            container.appendChild(card);
        });
    } catch (error) {
        console.error('Error loading students:', error);
    }
}

// Load live attendance for current course
async function loadLiveAttendance() {
    try {
        const container = document.getElementById('attendance-list');
        const infoContainer = document.getElementById('live-course-info');

        if (!container) {
            console.error('Attendance list container not found!');
            return;
        }

        // Check if a course session has been started
        if (!currentCourseId) {
            container.innerHTML = '<p style="text-align: center; padding: 40px; color: #666; font-size: 16px;">No active course session. Please select a course in the <strong>Mark Attendance</strong> tab.</p>';
            infoContainer.innerHTML = '<p style="margin: 0; color: #666;">Select a course session in the Mark Attendance tab to view live attendance</p>';
            return;
        }

        // Fetch live attendance data
        console.log('Fetching live attendance for course:', currentCourseId);
        const response = await fetch(`/api/attendance/live?course_id=${currentCourseId}`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Live attendance data received:', data);

        if (!data.success) {
            throw new Error(data.error || 'Failed to load attendance');
        }

        // Update course info
        infoContainer.innerHTML = `
            <p style="margin: 0;">
                <strong>Course:</strong> ${data.course_code} - ${data.course_name} |
                <strong>Last Updated:</strong> ${formatTimeUTC7(new Date().toISOString())} (UTC+7) |
                <strong>Total Students:</strong> ${data.students.length} |
                <strong>Present:</strong> <span style="color: #28a745;">${data.students.filter(s => s.status === 'present').length}</span> |
                <strong>Absent:</strong> <span style="color: #dc3545;">${data.students.filter(s => s.status === 'absent').length}</span>
            </p>
        `;

        if (data.students.length === 0) {
            container.innerHTML = '<p style="text-align: center; padding: 40px; color: #666; font-size: 16px;">No students enrolled in this course.</p>';
            return;
        }

        // Build the table
        const table = document.createElement('table');
        table.innerHTML = `
            <thead>
                <tr>
                    <th>Student Name</th>
                    <th>Student ID</th>
                    <th>Status</th>
                    <th>Marked At</th>
                    <th>Confidence</th>
                </tr>
            </thead>
            <tbody>
                ${data.students.map(student => `
                    <tr>
                        <td class="${student.status === 'absent' ? 'absent-student' : 'present-student'}">${student.student_name}</td>
                        <td>${student.student_id}</td>
                        <td>
                            <span class="${student.status === 'absent' ? 'absent-student' : 'present-student'}">
                                ${student.status === 'present' ? '✓ Present' : '✗ Absent'}
                            </span>
                        </td>
                        <td>${formatTimeUTC7(student.marked_at)}</td>
                        <td>${student.confidence || '-'}</td>
                    </tr>
                `).join('')}
            </tbody>
        `;

        container.innerHTML = '';
        container.appendChild(table);
        console.log('Live attendance table rendered successfully');
    } catch (error) {
        console.error('Error loading live attendance:', error);
        const container = document.getElementById('attendance-list');
        if (container) {
            container.innerHTML = `<p style="color: red; text-align: center; padding: 20px;">Error loading live attendance: ${error.message}</p>`;
        }
    }
}

// Note: Live attendance now auto-refreshes every 5 seconds
// Old date filter functionality removed as this is now a live view

// Utility functions
function showResult(elementId, message, type) {
    const resultBox = document.getElementById(elementId);
    resultBox.textContent = message;
    resultBox.className = `result-box ${type}`;
}

function base64ToBlob(base64, contentType) {
    const byteCharacters = atob(base64);
    const byteArrays = [];

    for (let offset = 0; offset < byteCharacters.length; offset += 512) {
        const slice = byteCharacters.slice(offset, offset + 512);
        const byteNumbers = new Array(slice.length);

        for (let i = 0; i < slice.length; i++) {
            byteNumbers[i] = slice.charCodeAt(i);
        }

        const byteArray = new Uint8Array(byteNumbers);
        byteArrays.push(byteArray);
    }

    return new Blob(byteArrays, { type: contentType });
}

// Manual start camera button
document.getElementById('manual-start-camera')?.addEventListener('click', startEnrollWebcam);

// Camera and Course Session selection for Mark Attendance tab
let currentCamera = 1; // Default to Mac built-in camera

// Load courses for attendance session
async function loadCoursesForAttendance() {
    try {
        console.log('Loading courses for attendance...');
        const select = document.getElementById('course-session-select');

        if (!select) {
            console.error('Course select element not found!');
            return;
        }

        const response = await fetch('/api/courses');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const courses = await response.json();
        console.log('Courses loaded:', courses.length);

        select.innerHTML = '<option value="">-- Select Course Session --</option>';

        courses.forEach(course => {
            const option = document.createElement('option');
            option.value = course.id;
            option.textContent = `${course.course_code} - ${course.course_name} (${course.start_time} - ${course.end_time})`;
            option.dataset.courseName = `${course.course_code} - ${course.course_name}`;
            select.appendChild(option);
        });

        console.log('Course dropdown populated successfully');
    } catch (error) {
        console.error('Error loading courses:', error);
        const select = document.getElementById('course-session-select');
        if (select) {
            select.innerHTML = '<option value="">Error loading courses</option>';
        }
    }
}

// Start attendance session with selected camera and course
document.getElementById('apply-settings-btn')?.addEventListener('click', () => {
    const selectedCamera = document.getElementById('camera-select').value;
    const selectedCourse = document.getElementById('course-session-select').value;
    const courseSelect = document.getElementById('course-session-select');
    const selectedOption = courseSelect.options[courseSelect.selectedIndex];

    if (!selectedCourse) {
        showResult('attendance-result', 'Please select a course session!', 'error');
        return;
    }

    currentCamera = selectedCamera;
    currentCourseId = selectedCourse;
    currentCourseName = selectedOption.dataset.courseName;

    // Update video feed URL with camera and course parameters
    const videoFeed = document.getElementById('video-feed');
    const timestamp = new Date().getTime();
    videoFeed.src = `/api/video_feed?camera=${selectedCamera}&course_id=${selectedCourse}&t=${timestamp}`;

    // Show session info
    document.getElementById('active-course-name').textContent = currentCourseName;
    const cameraName = selectedCamera === '0' ? 'Logitech USB Webcam' : 'Mac Built-in (FaceTime HD)';
    document.getElementById('active-camera-name').textContent = cameraName;
    document.getElementById('session-info').style.display = 'block';

    showResult('attendance-result', `Attendance session started for ${currentCourseName}`, 'success');

    // Clear the result after 3 seconds
    setTimeout(() => {
        document.getElementById('attendance-result').style.display = 'none';
    }, 3000);
});

// Initialize - Load courses and handle tab-specific initialization
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing...');

    // Always load courses on page load
    loadCoursesForAttendance();

    // Check which tab is active
    const activeTab = document.querySelector('.tab-content.active');
    if (activeTab && activeTab.id === 'enroll-tab') {
        // Start camera if on enroll tab
        setTimeout(() => {
            console.log('Page loaded on enroll tab, starting camera...');
            startEnrollWebcam();
        }, 500);
    }
});

// ========== ADMIN MODULE ==========

let adminLoggedIn = false;

// Admin login
document.getElementById('admin-login-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = document.getElementById('admin-username').value;
    const password = document.getElementById('admin-password').value;

    try {
        const response = await fetch('/api/admin/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (data.success) {
            adminLoggedIn = true;
            document.getElementById('admin-login').style.display = 'none';
            document.getElementById('admin-dashboard').style.display = 'block';
            showResult('login-result', '', 'success');

            // Load initial data
            loadCourses();
            loadEnrollments();
            loadStudentsForEnrollment();
            loadCoursesForEnrollment();
            loadCoursesForExport();
        } else {
            showResult('login-result', data.error || 'Login failed', 'error');
        }
    } catch (error) {
        showResult('login-result', `Error: ${error.message}`, 'error');
    }
});

// Admin logout
document.getElementById('admin-logout-btn').addEventListener('click', () => {
    adminLoggedIn = false;
    document.getElementById('admin-login').style.display = 'block';
    document.getElementById('admin-dashboard').style.display = 'none';
    document.getElementById('admin-login-form').reset();
    document.getElementById('admin-username').value = '';
    document.getElementById('admin-password').value = '';
});

// Admin sub-tab switching
document.querySelectorAll('.admin-tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const tabName = btn.dataset.adminTab;

        // Remove active class from all buttons and contents
        document.querySelectorAll('.admin-tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.admin-tab-content').forEach(content => content.classList.remove('active'));

        // Add active class to selected tab
        btn.classList.add('active');
        document.getElementById(`admin-${tabName}`).classList.add('active');
        
        // Load courses for import dropdown when import tab is opened
        if (tabName === 'import') {
            loadCoursesForImport();
        }
    });
});

// ===== COURSE MANAGEMENT =====

let editingCourseId = null;

document.getElementById('add-course-btn').addEventListener('click', () => {
    editingCourseId = null;
    document.getElementById('course-form-title').textContent = 'Add New Course';
    document.getElementById('course-form').reset();
    document.getElementById('course-id').value = '';
    document.getElementById('course-form-section').style.display = 'block';
});

document.getElementById('cancel-course-btn').addEventListener('click', () => {
    document.getElementById('course-form-section').style.display = 'none';
    document.getElementById('course-form').reset();
    editingCourseId = null;
});

document.getElementById('course-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const courseCode = document.getElementById('course-code').value;
    const courseName = document.getElementById('course-name').value;
    const startTime = document.getElementById('start-time').value;
    const endTime = document.getElementById('end-time').value;

    // Get selected days
    const selectedDays = Array.from(document.querySelectorAll('input[name="days"]:checked'))
        .map(cb => cb.value)
        .join(',');

    const courseData = {
        course_code: courseCode,
        course_name: courseName,
        start_time: startTime,
        end_time: endTime,
        days_of_week: selectedDays
    };

    try {
        let response;
        if (editingCourseId) {
            // Update existing course
            response = await fetch(`/api/courses/${editingCourseId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(courseData)
            });
        } else {
            // Create new course
            response = await fetch('/api/courses', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(courseData)
            });
        }

        const data = await response.json();

        if (data.success) {
            showResult('course-form-result', editingCourseId ? 'Course updated!' : 'Course created!', 'success');
            document.getElementById('course-form').reset();
            document.getElementById('course-form-section').style.display = 'none';
            loadCourses();
            loadCoursesForEnrollment();
            loadCoursesForExport();
            editingCourseId = null;
        } else {
            showResult('course-form-result', data.error || 'Operation failed', 'error');
        }
    } catch (error) {
        showResult('course-form-result', `Error: ${error.message}`, 'error');
    }
});

async function loadCourses() {
    try {
        const response = await fetch('/api/courses');
        const courses = await response.json();

        const container = document.getElementById('courses-list');
        container.innerHTML = '';

        if (courses.length === 0) {
            container.innerHTML = '<p>No courses created yet.</p>';
            return;
        }

        courses.forEach(course => {
            const card = document.createElement('div');
            card.className = 'student-card';
            card.innerHTML = `
                <h3>${course.course_name}</h3>
                <p><strong>Code:</strong> ${course.course_code}</p>
                <p><strong>Time:</strong> ${course.start_time} - ${course.end_time}</p>
                <p><strong>Days:</strong> ${course.days_of_week || 'N/A'}</p>
                <p><strong>Status:</strong> ${course.is_active ? 'Active' : 'Inactive'}</p>
                <div style="margin-top: 10px;">
                    <button class="btn btn-secondary" onclick="editCourse(${course.id})">Edit</button>
                    <button class="btn btn-secondary" onclick="deleteCourse(${course.id})">Delete</button>
                </div>
            `;
            container.appendChild(card);
        });
    } catch (error) {
        console.error('Error loading courses:', error);
    }
}

window.editCourse = async function(courseId) {
    try {
        const response = await fetch('/api/courses');
        const courses = await response.json();
        const course = courses.find(c => c.id === courseId);

        if (course) {
            editingCourseId = courseId;
            document.getElementById('course-form-title').textContent = 'Edit Course';
            document.getElementById('course-id').value = courseId;
            document.getElementById('course-code').value = course.course_code;
            document.getElementById('course-name').value = course.course_name;
            document.getElementById('start-time').value = course.start_time;
            document.getElementById('end-time').value = course.end_time;

            // Set checkboxes
            document.querySelectorAll('input[name="days"]').forEach(cb => {
                cb.checked = course.days_of_week && course.days_of_week.includes(cb.value);
            });

            document.getElementById('course-form-section').style.display = 'block';
        }
    } catch (error) {
        console.error('Error loading course for edit:', error);
    }
};

window.deleteCourse = async function(courseId) {
    if (!confirm('Are you sure you want to delete this course?')) return;

    try {
        const response = await fetch(`/api/courses/${courseId}`, { method: 'DELETE' });
        const data = await response.json();

        if (data.success) {
            loadCourses();
            loadCoursesForEnrollment();
            loadCoursesForExport();
        } else {
            alert(data.error || 'Failed to delete course');
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
};

// ===== ENROLLMENT MANAGEMENT =====

document.getElementById('add-enrollment-btn').addEventListener('click', () => {
    document.getElementById('enrollment-form').reset();
    document.getElementById('enrollment-form-section').style.display = 'block';
    loadStudentsForEnrollment();
    loadCoursesForEnrollment();
});

document.getElementById('cancel-enrollment-btn').addEventListener('click', () => {
    document.getElementById('enrollment-form-section').style.display = 'none';
    document.getElementById('enrollment-form').reset();
});

document.getElementById('enrollment-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const studentId = document.getElementById('enroll-student-select').value;
    const courseId = document.getElementById('enroll-course-select').value;

    try {
        const response = await fetch('/api/enrollments', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                student_id: parseInt(studentId),
                course_id: parseInt(courseId)
            })
        });

        const data = await response.json();

        if (data.success) {
            showResult('enrollment-form-result', 'Student enrolled successfully!', 'success');
            document.getElementById('enrollment-form').reset();
            document.getElementById('enrollment-form-section').style.display = 'none';
            loadEnrollments();
        } else {
            showResult('enrollment-form-result', data.error || 'Enrollment failed', 'error');
        }
    } catch (error) {
        showResult('enrollment-form-result', `Error: ${error.message}`, 'error');
    }
});

async function loadStudentsForEnrollment() {
    try {
        const response = await fetch('/api/students');
        const students = await response.json();

        const select = document.getElementById('enroll-student-select');
        select.innerHTML = '<option value="">-- Select Student --</option>';

        students.forEach(student => {
            const option = document.createElement('option');
            option.value = student.id;
            option.textContent = `${student.name} (${student.student_id})`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading students:', error);
    }
}

async function loadCoursesForEnrollment() {
    try {
        const response = await fetch('/api/courses');
        const courses = await response.json();

        const select = document.getElementById('enroll-course-select');
        select.innerHTML = '<option value="">-- Select Course --</option>';

        courses.forEach(course => {
            const option = document.createElement('option');
            option.value = course.id;
            option.textContent = `${course.course_name} (${course.course_code})`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading courses:', error);
    }
}

async function loadEnrollments() {
    try {
        const response = await fetch('/api/enrollments');
        const enrollments = await response.json();

        const container = document.getElementById('enrollments-list');
        container.innerHTML = '';

        if (enrollments.length === 0) {
            container.innerHTML = '<p>No enrollments found.</p>';
            return;
        }

        const table = document.createElement('table');
        table.innerHTML = `
            <thead>
                <tr>
                    <th>Student ID</th>
                    <th>Student Name</th>
                    <th>Course Code</th>
                    <th>Course Name</th>
                    <th>Enrolled Date</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                ${enrollments.map(enrollment => `
                    <tr>
                        <td>${enrollment.student_id || 'N/A'}</td>
                        <td>${enrollment.student_name || 'N/A'}</td>
                        <td>${enrollment.course_code || 'N/A'}</td>
                        <td>${enrollment.course_name || 'N/A'}</td>
                        <td>${new Date(enrollment.enrolled_date).toLocaleDateString()}</td>
                        <td>
                            <button class="btn btn-secondary" onclick="deleteEnrollment(${enrollment.id})">Remove</button>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        `;

        container.appendChild(table);
    } catch (error) {
        console.error('Error loading enrollments:', error);
    }
}

window.deleteEnrollment = async function(enrollmentId) {
    if (!confirm('Are you sure you want to remove this enrollment?')) return;

    try {
        const response = await fetch(`/api/enrollments/${enrollmentId}`, { method: 'DELETE' });
        const data = await response.json();

        if (data.success) {
            loadEnrollments();
        } else {
            alert(data.error || 'Failed to remove enrollment');
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
};

// ===== EXPORT DATA =====

async function loadCoursesForExport() {
    try {
        const response = await fetch('/api/courses');
        const courses = await response.json();

        const select = document.getElementById('export-course-filter');
        select.innerHTML = '<option value="">All Courses</option>';

        courses.forEach(course => {
            const option = document.createElement('option');
            option.value = course.id;
            option.textContent = `${course.course_name} (${course.course_code})`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading courses for export:', error);
    }
}

document.getElementById('export-btn').addEventListener('click', () => {
    const courseId = document.getElementById('export-course-filter').value;
    const startDate = document.getElementById('export-start-date').value;
    const endDate = document.getElementById('export-end-date').value;

    let url = '/api/export/attendance?';
    if (courseId) url += `course_id=${courseId}&`;
    if (startDate) url += `start_date=${startDate}&`;
    if (endDate) url += `end_date=${endDate}&`;

    // Download the CSV
    window.location.href = url;
});

// ===== STUDENT LOOKUP =====

async function loadCoursesForLookup() {
    try {
        const response = await fetch('/api/courses');
        const courses = await response.json();

        const select = document.getElementById('course-filter');
        select.innerHTML = '<option value="">All Students</option>';

        courses.forEach(course => {
            const option = document.createElement('option');
            option.value = course.id;
            option.textContent = `${course.course_name} (${course.course_code})`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading courses:', error);
    }
}

async function loadCoursesForImport() {
    try {
        const response = await fetch('/api/courses');
        const courses = await response.json();

        const select = document.getElementById('import-course-select');
        select.innerHTML = '<option value="">-- Select a course to auto-enroll students --</option>';

        courses.forEach(course => {
            const option = document.createElement('option');
            option.value = course.id;
            option.textContent = `${course.course_code} - ${course.course_name}`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading courses for import:', error);
    }
}

document.getElementById('lookup-student-btn').addEventListener('click', () => {
    document.getElementById('student-lookup-modal').style.display = 'block';
    loadCoursesForLookup();
    searchStudents(); // Load all students by default
});

function closeStudentLookup() {
    document.getElementById('student-lookup-modal').style.display = 'none';
}

document.getElementById('search-students-btn').addEventListener('click', searchStudents);
document.getElementById('student-search').addEventListener('keyup', (e) => {
    if (e.key === 'Enter') {
        searchStudents();
    }
});

async function searchStudents() {
    const query = document.getElementById('student-search').value;
    const courseId = document.getElementById('course-filter').value;
    const noPhoto = document.getElementById('no-photo-filter').checked;

    let url = '/api/students/search?';
    if (query) url += `q=${encodeURIComponent(query)}&`;
    if (courseId) url += `course_id=${courseId}&`;
    if (noPhoto) url += 'no_photo=true&';

    try {
        const response = await fetch(url);
        const data = await response.json();

        displayStudentResults(data.students);
    } catch (error) {
        console.error('Error searching students:', error);
        alert('Error searching students');
    }
}

function displayStudentResults(students) {
    const resultsDiv = document.getElementById('student-results');

    if (students.length === 0) {
        resultsDiv.innerHTML = '<p style="text-align: center; color: #666;">No students found</p>';
        return;
    }

    let html = '<table style="width: 100%; border-collapse: collapse;">';
    html += '<thead><tr style="background: #f5f5f5;">';
    html += '<th style="padding: 10px; border: 1px solid #ddd;">Student ID</th>';
    html += '<th style="padding: 10px; border: 1px solid #ddd;">Name</th>';
    html += '<th style="padding: 10px; border: 1px solid #ddd;">Courses</th>';
    html += '<th style="padding: 10px; border: 1px solid #ddd;">Photo Status</th>';
    html += '<th style="padding: 10px; border: 1px solid #ddd;">Action</th>';
    html += '</tr></thead><tbody>';

    students.forEach(student => {
        const coursesText = student.courses.length > 0 
            ? student.courses.map(c => c.code).join(', ') 
            : 'Not enrolled';
        const photoStatus = student.has_photo 
            ? '<span style="color: green;">✅ Enrolled</span>' 
            : '<span style="color: red;">❌ No photo</span>';

        html += '<tr>';
        html += `<td style="padding: 10px; border: 1px solid #ddd;">${student.student_id}</td>`;
        html += `<td style="padding: 10px; border: 1px solid #ddd;">${student.name}</td>`;
        html += `<td style="padding: 10px; border: 1px solid #ddd; font-size: 12px;">${coursesText}</td>`;
        html += `<td style="padding: 10px; border: 1px solid #ddd; text-align: center;">${photoStatus}</td>`;
        html += `<td style="padding: 10px; border: 1px solid #ddd; text-align: center;">`;
        html += `<button class="btn btn-primary" style="padding: 5px 15px; font-size: 14px;" onclick='selectStudent(${JSON.stringify(student)})'>Select</button>`;
        html += '</td></tr>';
    });

    html += '</tbody></table>';
    resultsDiv.innerHTML = html;
}

function selectStudent(student) {
    // Auto-fill the enrollment form
    document.getElementById('student-id').value = student.student_id;
    document.getElementById('student-name').value = student.name;

    // Close modal
    closeStudentLookup();

    // Show success message
    const resultDiv = document.getElementById('enroll-result');
    resultDiv.innerHTML = `<div class="success">Selected: ${student.name} (${student.student_id}). Now capture or upload their face photo.</div>`;
    resultDiv.style.display = 'block';

    // Scroll to form
    document.getElementById('student-form').scrollIntoView({ behavior: 'smooth' });
}

// ===== BULK IMPORT =====

document.getElementById('excel-upload').addEventListener('change', (e) => {
    const file = e.target.files[0];
    const btn = document.getElementById('import-excel-btn');
    if (file) {
        btn.disabled = false;
        btn.textContent = `Import ${file.name}`;
    } else {
        btn.disabled = true;
        btn.textContent = 'Import Students';
    }
});

document.getElementById('download-template-btn').addEventListener('click', () => {
    window.location.href = '/api/students/export-template';
});

document.getElementById('import-excel-btn').addEventListener('click', async () => {
    const fileInput = document.getElementById('excel-upload');
    const file = fileInput.files[0];

    if (!file) {
        alert('Please select an Excel file');
        return;
    }

    const courseSelect = document.getElementById('import-course-select');
    const courseId = courseSelect.value;

    const formData = new FormData();
    formData.append('file', file);
    if (courseId) {
        formData.append('course_id', courseId);
    }

    const resultDiv = document.getElementById('import-result');
    resultDiv.innerHTML = '<div class="info">Importing students... Please wait.</div>';
    resultDiv.style.display = 'block';

    try {
        const response = await fetch('/api/students/bulk-import', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            let message = `<div class="success"><strong>Import Successful!</strong><br>`;
            message += `✅ Imported: ${data.imported} students<br>`;
            if (data.enrolled > 0) {
                message += `📚 Enrolled: ${data.enrolled} students in course<br>`;
            }
            if (data.skipped > 0) {
                message += `⏭️ Skipped: ${data.skipped} empty rows<br>`;
            }
            if (data.errors.length > 0) {
                message += `<br><strong>Errors:</strong><br>`;
                message += `<ul style="text-align: left; margin: 10px 0;">`;
                data.errors.forEach(error => {
                    message += `<li>${error}</li>`;
                });
                message += '</ul>';
            }
            message += '</div>';
            resultDiv.innerHTML = message;

            // Reset file input
            fileInput.value = '';
            document.getElementById('import-excel-btn').disabled = true;
            document.getElementById('import-excel-btn').textContent = 'Import Students';

            // Refresh students list if on students tab
            loadStudents();
        } else {
            resultDiv.innerHTML = `<div class="error">Import failed: ${data.error}</div>`;
        }
    } catch (error) {
        console.error('Error importing:', error);
        resultDiv.innerHTML = `<div class="error">Error importing students: ${error.message}</div>`;
    }
});

