# Faculty Portal - Academic Management System

## Overview

This is a comprehensive faculty-facing academic management system that loads all data from CSV, Excel, and JSON files. The system provides a complete solution for managing students, courses, attendance, leave requests, and notices without requiring a database.

## Features

### 🎯 Core Modules

1. **Student Management**
   - View all students with filtering options
   - Add new students
   - Update student information
   - Export student data

2. **Course Management**
   - Manage course information
   - Track enrollment limits
   - View course performance metrics

3. **Attendance Management**
   - Mark daily attendance
   - View attendance statistics
   - Export attendance reports
   - Track attendance trends

4. **Leave Management**
   - Review leave requests
   - Approve/reject leave applications
   - Track leave statistics
   - Export leave data

5. **Notice Board**
   - Create and manage notices
   - Categorize by priority and type
   - Track notice statistics
   - Export notice data

6. **Dashboard & Analytics**
   - Real-time statistics
   - Visual analytics
   - Recent activities
   - Performance metrics

7. **Data Export**
   - Export all modules to CSV/Excel
   - Bulk export functionality
   - Filtered exports
   - Complete data backup

### 🤖 AI Assistant
- Intelligent query handling
- Context-aware responses
- Academic policy guidance
- Multi-agent RAG system

## Data Structure

### File Organization
```
backend/data/
├── students.csv          # Student information
├── courses.csv           # Course details
├── attendance.csv        # Daily attendance records
├── leave_requests.json   # Leave applications
├── notices.json          # Notice board content
└── knowledge/            # AI knowledge base
    ├── academic_rules.json
    ├── procedures.csv
    └── tools_and_instructions.txt
```

### Data Formats

#### Students CSV
```csv
id,name,roll_number,email,course,department,phone,address,enrollment_date,status
1,Alice Johnson,CS001,alice.johnson@university.edu,CS101,Computer Science,+1-555-0101,123 Main St,2023-09-01,active
```

#### Courses CSV
```csv
id,course_code,course_name,department,instructor,credits,schedule,room,enrollment_limit,current_enrollment
1,CS101,Data Structures,Computer Science,Dr. Sarah Johnson,3,MWF 10:00-11:00,Room 101,50,45
```

#### Attendance CSV
```csv
id,student_id,student_name,roll_number,course_code,date,status,class_name,remarks,marked_by
1,1,Alice Johnson,CS001,CS101,2024-01-15,present,Data Structures,On time,Dr. Sarah Johnson
```

#### Leave Requests JSON
```json
[
  {
    "id": "1",
    "studentId": "1",
    "studentName": "Alice Johnson",
    "leaveType": "sick",
    "startDate": "2024-01-20",
    "endDate": "2024-01-22",
    "status": "pending"
  }
]
```

#### Notices JSON
```json
[
  {
    "id": "1",
    "title": "Mid-term Exam Schedule Released",
    "content": "The mid-term examination schedule...",
    "type": "announcement",
    "priority": "high",
    "targetAudience": "students"
  }
]
```

## API Endpoints

### Student Management
- `GET /api/students` - Get all students
- `GET /api/students/<id>` - Get specific student
- `POST /api/students` - Create new student
- `PUT /api/students/<id>` - Update student

### Course Management
- `GET /api/courses` - Get all courses
- `GET /api/courses/<id>` - Get specific course
- `POST /api/courses` - Create new course

### Attendance Management
- `GET /api/attendance/students` - Get students with attendance
- `POST /api/attendance/mark` - Mark attendance
- `GET /api/attendance/stats` - Get attendance statistics
- `GET /api/attendance/export` - Export attendance data

### Leave Management
- `GET /api/leave/requests` - Get all leave requests
- `POST /api/leave/request` - Create leave request
- `POST /api/leave/request/<id>/approve` - Approve leave
- `POST /api/leave/request/<id>/reject` - Reject leave
- `GET /api/leave/stats` - Get leave statistics

### Notice Board
- `GET /api/notices` - Get all notices
- `POST /api/notices` - Create notice
- `PUT /api/notices/<id>` - Update notice
- `DELETE /api/notices/<id>` - Delete notice
- `GET /api/notices/stats` - Get notice statistics

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/analytics` - Get analytics data
- `GET /api/dashboard/quick-actions` - Get quick actions

### Data Export
- `GET /api/export/attendance` - Export attendance data
- `GET /api/export/students` - Export students data
- `GET /api/export/courses` - Export courses data
- `GET /api/export/leaves` - Export leave data
- `GET /api/export/notices` - Export notices data
- `GET /api/export/all` - Export all data as ZIP

### AI Assistant
- `POST /api/rag/chat` - Chat with AI assistant
- `GET /api/rag/status` - Get RAG system status
- `GET /api/rag/history/<session_id>` - Get chat history

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 18+
- pip and npm

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment file:**
   ```bash
   cp env.example .env
   ```

5. **Add your Groq API key:**
   ```bash
   echo "GROQ_API_KEY=your_groq_api_key_here" >> .env
   ```

6. **Start the backend:**
   ```bash
   python app.py
   ```

The backend will be available at `http://localhost:5001`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:3000`

## Usage Guide

### Adding Students
1. Go to the Students section
2. Click "Add New Student"
3. Fill in the required information
4. Save to add to the CSV file

### Marking Attendance
1. Navigate to Attendance section
2. Select the course and date
3. Mark each student's attendance status
4. Save to update the CSV file

### Managing Leave Requests
1. Go to Leave Management
2. Review pending requests
3. Approve or reject with remarks
4. Updates are saved to JSON file

### Creating Notices
1. Access Notice Board
2. Click "Create Notice"
3. Fill in title, content, and priority
4. Save to JSON file

### Exporting Data
1. Go to any module
2. Click "Export" button
3. Choose format (CSV/Excel)
4. Apply filters if needed
5. Download the file

## Data Management

### Adding New Data
- **Students**: Add rows to `students.csv`
- **Courses**: Add rows to `courses.csv`
- **Attendance**: Add rows to `attendance.csv`
- **Leaves**: Add objects to `leave_requests.json`
- **Notices**: Add objects to `notices.json`

### Data Validation
- All APIs validate required fields
- Duplicate roll numbers are prevented
- Date formats are validated
- File integrity is maintained

### Backup Strategy
- Regular exports using the export APIs
- Complete data backup via `/api/export/all`
- Version control for data files
- Automated backup scripts (optional)

## Customization

### Adding New Fields
1. Update the CSV/JSON structure
2. Modify the API endpoints
3. Update the frontend components
4. Test data loading and saving

### Adding New Modules
1. Create new CSV/JSON files
2. Add data loader functions
3. Create API endpoints
4. Update dashboard analytics
5. Add frontend components

## Troubleshooting

### Common Issues

1. **Data not loading:**
   - Check file paths in `data/` directory
   - Verify CSV/JSON format
   - Check file permissions

2. **Export not working:**
   - Ensure pandas and openpyxl are installed
   - Check temporary file permissions
   - Verify data exists

3. **AI Assistant not responding:**
   - Verify Groq API key is set
   - Check internet connection
   - Review RAG system logs

### Logs
- Backend logs: `logs/server.log`
- Error logs: `logs/errors.log`
- Console output for real-time debugging

## Security Considerations

- All data is stored locally in files
- No external database dependencies
- File-based access control
- Regular data validation
- Secure file handling

## Performance

- Fast CSV/JSON loading with pandas
- Efficient data caching
- Optimized API responses
- Minimal memory footprint
- Scalable file-based architecture

## Support

For issues or questions:
1. Check the logs for error details
2. Verify data file formats
3. Test API endpoints individually
4. Review the troubleshooting section

## License

This project is open source and available under the MIT License.
