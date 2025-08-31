# AIDE - Academic AI Management System

A comprehensive AI-powered academic management system designed to streamline education for students, faculty, and coordinators.

## 🚀 Features

### For Students
- **Personalized Dashboard**: Track attendance, view timetables, and access study materials
- **AI Study Assistant**: Get instant help with academic questions and homework
- **Notice Board**: Stay updated with important announcements and events
- **Leave Management**: Submit and track leave requests
- **Resource Access**: Download study materials and assignments

### For Faculty
- **Teaching Dashboard**: Manage classes, track attendance, and grade assignments
- **Resource Management**: Upload and organize study materials
- **Leave Approval**: Review and approve student leave requests
- **AI Teaching Assistant**: Get help with grading and question generation
- **Performance Analytics**: View student progress and attendance reports

### For Coordinators
- **Event Management**: Create and manage academic events
- **System Administration**: Oversee academic operations
- **Report Generation**: Generate comprehensive reports
- **Notification System**: Send announcements to students and faculty
- **AI Management Assistant**: Get help with administrative tasks

## 🛠️ Technology Stack

### Backend
- **Python 3.8+** with Flask framework
- **RESTful API** architecture
- **CSV-based data storage** (for demo purposes)
- **CORS enabled** for cross-origin requests

### Frontend
- **Next.js 15** with React 19
- **Tailwind CSS 4** for styling
- **Framer Motion** for animations
- **Lucide React** for icons

## 📋 Prerequisites

Before running AIDE, make sure you have the following installed:

- **Python 3.8 or higher**
- **Node.js 18 or higher**
- **npm** (comes with Node.js)

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

#### For macOS/Linux:
```bash
./start.sh
```

#### For Windows:
```cmd
start.bat
```

### Option 2: Manual Setup

#### 1. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

#### 2. Frontend Setup
```bash
cd aide
npm install
npm run dev
```

## 🔐 Demo Credentials

### Student Login
- **Email**: tmtanush@gmail.com
- **Password**: 1234

### Faculty Login
- **Email**: justindhas@gmail.com
- **Password**: 1234

## 🌐 Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5001
- **Health Check**: http://localhost:5001/health

## 📁 Project Structure

```
AIDE/
├── backend/                 # Flask backend
│   ├── app.py              # Main Flask application
│   ├── requirements.txt    # Python dependencies
│   ├── data/              # Data files
│   │   ├── auth/          # User authentication data
│   │   └── notice/        # Notice board data
│   └── venv/              # Python virtual environment
├── aide/                   # Next.js frontend
│   ├── app/               # Next.js app directory
│   │   ├── dashboard/     # Dashboard pages
│   │   ├── login/         # Login page
│   │   └── page.js        # Home page
│   ├── components/        # React components
│   └── package.json       # Node.js dependencies
├── start.sh               # Linux/macOS startup script
├── start.bat              # Windows startup script
└── README.md              # This file
```

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/validate` - Validate user session

### Dashboard
- `GET /api/dashboard/{role}/{user_id}` - Get dashboard data

### Notices
- `GET /api/notices` - Get all notices

### Attendance
- `GET /api/attendance/student/{student_id}` - Get student attendance

### Leaves
- `GET /api/leaves/student/{student_id}` - Get student leave requests
- `POST /api/leaves` - Submit leave request

### Events
- `GET /api/events` - Get all events

### Resources
- `GET /api/resources` - Get study resources

### Health Check
- `GET /health` - System health status

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**
   - Backend: Change port in `backend/app.py` (line 197)
   - Frontend: Change port in `aide/package.json` scripts

2. **Python dependencies not found**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt` again

3. **Node.js dependencies not found**
   - Run `npm install` in the `aide` directory

4. **CORS errors**
   - Backend CORS is configured for `http://localhost:3000`
   - Ensure frontend is running on the correct port

### Logs
- Backend logs: Check terminal where `python app.py` is running
- Frontend logs: Check terminal where `npm run dev` is running

## 🔮 Future Enhancements

- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] Real-time notifications
- [ ] File upload functionality
- [ ] Advanced AI features
- [ ] Mobile app
- [ ] Multi-language support
- [ ] Advanced analytics
- [ ] Integration with external LMS

## 📝 License

This project is for educational purposes. Feel free to use and modify as needed.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For support or questions, please open an issue in the repository.

---

**AIDE** - Empowering education through AI 🚀

