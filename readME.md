# Academic AI Management System

A comprehensive, agentic AI-powered academic management system built with Flask, Next.js, and advanced AI capabilities including RAG (Retrieval-Augmented Generation) for intelligent query handling.

## 🚀 Features

### Core Academic Management
- **📊 Attendance Management** - Mark, track, and analyze student attendance with policy validation
- **📝 Leave Request System** - Complete workflow for leave requests with approval/rejection
- **🎯 Event Management** - Create, register, and manage academic events with capacity control
- **📢 Notice Board** - Priority-based notice posting with role-based access control
- **📚 Resource Management** - File upload/download with access control and analytics

### AI-Powered Features
- **🤖 Multi-Agent System** - Specialized AI agents for different academic workflows
- **🧠 RAG System** - Intelligent query handling with knowledge base integration
- **📋 Policy Validation** - Automated validation against institutional policies
- **🔍 Semantic Search** - Advanced search across policies, notices, and resources

### Security & Access Control
- **🔐 Role-Based Authentication** - Student, Faculty, Coordinator roles
- **🛡️ JWT Security** - Secure token-based authentication
- **📁 File Access Control** - Role-based resource access
- **🔒 Policy Enforcement** - Automated compliance checking

## 🏗️ Architecture

### Backend Stack
- **Flask** - Web framework with Blueprint architecture
- **MongoDB** - Primary database for dynamic data
- **Redis** - Caching and session management
- **ChromaDB** - Vector database for RAG system
- **Groq** - LLM integration for AI agents
- **Sentence-Transformers** - Text embeddings for semantic search

### Frontend Stack
- **Next.js 14** - React framework with App Router
- **Tailwind CSS** - Utility-first CSS framework
- **Zustand** - State management
- **Axios** - HTTP client
- **React Hook Form** - Form handling

### AI & ML Components
- **LangChain** - AI agent framework
- **RAG Pipeline** - Knowledge retrieval and generation
- **Policy Engine** - Automated policy validation
- **Multi-Agent Orchestration** - Coordinated AI workflows

## 📊 Database Schema

### Core Collections
```javascript
// Users (extends existing CSV authentication)
{
  user_id: String,
  email: String,
  role: Enum['student', 'faculty', 'coordinator'],
  profile: Object,
  created_at: DateTime
}

// Attendance
{
  student_id: String,
  course_code: String,
  date: DateTime,
  status: Enum['present', 'absent', 'late', 'excused'],
  session_type: Enum['lecture', 'lab', 'tutorial'],
  marked_by: String
}

// Leave Requests
{
  request_id: String,
  student_id: String,
  start_date: DateTime,
  end_date: DateTime,
  reason: String,
  leave_type: Enum['medical', 'personal', 'academic'],
  status: Enum['pending', 'approved', 'rejected'],
  reviewed_by: String
}

// Events
{
  event_id: String,
  title: String,
  description: String,
  event_type: Enum['workshop', 'seminar', 'conference'],
  start_datetime: DateTime,
  max_participants: Number,
  current_registrations: Number
}

// Notices
{
  notice_id: String,
  title: String,
  content: String,
  priority: Enum['low', 'medium', 'high'],
  category: Enum['academic', 'administrative', 'event'],
  target_audience: Array[String],
  posted_by: String
}

// Resources
{
  resource_id: String,
  title: String,
  description: String,
  file_path: String,
  file_size: Number,
  access_level: Enum['public', 'students', 'faculty'],
  uploaded_by: String,
  download_count: Number
}
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- MongoDB 5.0+
- Redis 6.0+

### Installation

#### Option 1: Docker (Recommended)
```bash
# Clone the repository
git clone <repository-url>
cd AIDE

# Start all services
docker-compose up -d

# Access the application
# Backend: http://localhost:5001
# Frontend: http://localhost:3000
# MongoDB: localhost:27017
# Redis: localhost:6379
```

#### Option 2: Local Development
```bash
# Backend Setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables
cp env.example .env
# Edit .env with your configuration

# Start backend
python run.py

# Frontend Setup (in new terminal)
cd aide
npm install
npm run dev
```

### Environment Configuration
```bash
# Backend (.env)
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
MONGODB_URI=mongodb://localhost:27017/academic_ai
REDIS_URL=redis://localhost:6379/0
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=llama3-8b-8192
```

## 📚 API Documentation

### Authentication
```bash
# Login
POST /api/auth/login
{
  "email": "tmtanush@gmail.com",
  "password": "1234",
  "role": "student"
}

# Response
{
  "success": true,
  "user": {...},
  "access_token": "jwt-token",
  "refresh_token": "refresh-token"
}
```

### Attendance Management
```bash
# Mark attendance
POST /api/attendance/mark
{
  "student_id": "STU001",
  "course_code": "CS101",
  "date": "2024-01-15",
  "status": "present",
  "session_type": "lecture"
}

# View attendance
GET /api/attendance/view/STU001?course_code=CS101

# Get statistics
GET /api/attendance/stats/STU001
```

### Leave Management
```bash
# Create leave request
POST /api/leaves/request
{
  "student_id": "STU001",
  "start_date": "2024-01-20",
  "end_date": "2024-01-22",
  "reason": "Medical emergency",
  "leave_type": "medical"
}

# Approve/reject leave
POST /api/leaves/approve/LR2024011501ABCD
{
  "action": "approve",
  "remarks": "Approved with documentation"
}

# View leave balance
GET /api/leaves/balance/STU001
```

### Event Management
```bash
# Create event
POST /api/events/create
{
  "title": "AI Workshop",
  "description": "Introduction to AI",
  "event_type": "workshop",
  "start_datetime": "2024-02-01T10:00:00",
  "max_participants": 50
}

# Register for event
POST /api/events/register/EVT2024011501ABCD

# View event registrations
GET /api/events/registrations/EVT2024011501ABCD
```

### Notice Board
```bash
# Post notice
POST /api/notices/post
{
  "title": "Exam Schedule Update",
  "content": "Updated exam schedule...",
  "priority": "high",
  "category": "academic",
  "target_audience": ["students"]
}

# List notices
GET /api/notices/list?priority=high&category=academic

# Search notices
GET /api/notices/search?q=exam schedule
```

### Resource Management
```bash
# Upload resource
POST /api/resources/upload
Content-Type: multipart/form-data
{
  "file": "document.pdf",
  "title": "Course Syllabus",
  "description": "CS101 Course Syllabus",
  "category": "syllabus",
  "access_level": "students"
}

# Download resource
GET /api/resources/download/RES2024011501ABCD

# Search resources
GET /api/resources/search?q=syllabus
```

## 🤖 AI Agent System

### Available Agents
- **AttendanceAgent** - Handles attendance queries and analytics
- **LeaveAgent** - Processes leave requests and policy validation
- **EventAgent** - Manages event coordination and registration
- **NoticeAgent** - Handles notice posting and distribution
- **QAAgent** - General question answering with RAG

### Agent Interaction
```bash
# Chat with AI agent
POST /api/agents/chat
{
  "query": "What is the attendance policy for medical leave?",
  "context": {
    "user_role": "student",
    "user_id": "STU001"
  }
}

# Get agent capabilities
GET /api/agents/capabilities
```

## 🔍 RAG System

### Knowledge Base Components
- **Static Policies** - JSON-based institutional policies
- **Dynamic Records** - MongoDB collections for real-time data
- **Vector Database** - ChromaDB for semantic search

### RAG Features
- **Semantic Search** - Find relevant policies and information
- **Context Retrieval** - Get contextual information for queries
- **Policy Validation** - Automated compliance checking
- **Query Expansion** - Enhanced search capabilities

## 📈 Analytics & Reporting

### Dashboard Features
- **Real-time Statistics** - Live updates on system usage
- **Role-based Views** - Customized dashboards per user role
- **Trend Analysis** - Historical data visualization
- **Export Capabilities** - Data export in multiple formats

### Available Reports
- Attendance reports by course, student, or date range
- Leave request analytics and processing times
- Event registration and participation statistics
- Notice engagement and readership metrics
- Resource usage and download analytics

## 🔒 Security Features

### Authentication & Authorization
- **JWT Tokens** - Secure session management
- **Role-based Access Control** - Granular permissions
- **CSRF Protection** - Cross-site request forgery prevention
- **Input Validation** - Comprehensive data validation

### Data Protection
- **File Encryption** - Secure file storage
- **Access Logging** - Comprehensive audit trails
- **Data Backup** - Automated backup systems
- **Privacy Compliance** - GDPR and FERPA compliance

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -m pytest tests/
python -m pytest tests/ --cov=app --cov-report=html
```

### Frontend Testing
```bash
cd aide
npm test
npm run test:coverage
```

### API Testing
```bash
# Using curl
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"tmtanush@gmail.com","password":"1234","role":"student"}'

# Using Postman
# Import the provided Postman collection
```

## 📊 Monitoring & Logging

### Application Monitoring
- **Health Checks** - System health monitoring
- **Performance Metrics** - Response time tracking
- **Error Tracking** - Comprehensive error logging
- **Usage Analytics** - User behavior analysis

### Log Management
- **Structured Logging** - JSON-formatted logs
- **Log Levels** - Configurable logging levels
- **Log Rotation** - Automated log management
- **Centralized Logging** - Unified log collection

## 🚀 Deployment

### Production Deployment
```bash
# Using Docker
docker-compose -f docker-compose.prod.yml up -d

# Using Kubernetes
kubectl apply -f k8s/

# Using AWS
aws ecs create-service --cluster academic-ai --service-name backend
```

### Environment Variables
```bash
# Production settings
FLASK_ENV=production
DEBUG=False
LOG_LEVEL=WARNING
MONGODB_URI=mongodb://prod-mongo:27017/academic_ai
REDIS_URL=redis://prod-redis:6379/0
```

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Code Standards
- **Python** - PEP 8 compliance
- **JavaScript** - ESLint configuration
- **Documentation** - Comprehensive docstrings
- **Testing** - Minimum 80% coverage

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help
- **Documentation** - Comprehensive guides and tutorials
- **Issues** - GitHub issues for bug reports
- **Discussions** - Community discussions and Q&A
- **Email Support** - Direct support for enterprise users

### Community
- **Discord Server** - Real-time community support
- **GitHub Discussions** - Technical discussions
- **Blog** - Latest updates and tutorials
- **Newsletter** - Monthly updates and tips

## 🗺️ Roadmap

### ✅ Completed Phases
- **Phase 1: Foundation** - Authentication, database setup, basic architecture
- **Phase 2: RAG & Knowledge Base** - AI agents, policy management, vector database
- **Phase 3: Core Features** - Complete CRUD operations for all modules

### 🔄 Current Phase
- **Phase 4: AI Agents** - Advanced agent implementation and Groq integration

### 📋 Upcoming Phases
- **Phase 5: Advanced Features** - Real-time notifications, mobile app, analytics
- **Phase 6: Enterprise Features** - Multi-tenant support, advanced security
- **Phase 7: AI Enhancement** - Advanced RAG, multi-modal AI, predictive analytics

## 🏆 Features Summary

| Feature | Status | Description |
|---------|--------|-------------|
| Authentication | ✅ Complete | JWT-based with role management |
| Attendance | ✅ Complete | Full CRUD with analytics |
| Leave Management | ✅ Complete | End-to-end workflow |
| Event Management | ✅ Complete | Creation, registration, analytics |
| Notice Board | ✅ Complete | Priority-based with search |
| Resource Management | ✅ Complete | File upload/download with access control |
| AI Agents | 🔄 In Progress | Specialized agents for workflows |
| RAG System | ✅ Complete | Knowledge base and semantic search |
| Policy Engine | ✅ Complete | Automated validation |
| Analytics | ✅ Complete | Comprehensive reporting |
| Security | ✅ Complete | Role-based access control |
| Testing | ✅ Complete | Unit and integration tests |

## 🎯 Use Cases

### For Students
- View attendance records and statistics
- Submit and track leave requests
- Register for academic events
- Access course resources and notices
- Get AI-powered assistance for queries

### For Faculty
- Mark and manage student attendance
- Approve/reject leave requests
- Create and manage events
- Post notices and announcements
- Upload and manage course resources

### For Coordinators
- Oversee all academic activities
- Generate comprehensive reports
- Manage institutional policies
- Coordinate multi-department events
- Monitor system analytics

---

**Built with ❤️ for modern academic institutions**

