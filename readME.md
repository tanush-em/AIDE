# Academic AI Management System

A comprehensive agentic AI-powered academic management system with Flask backend, Next.js frontend, and intelligent RAG capabilities.

## 🚀 Project Overview

This system provides a complete academic management solution with AI-powered agents for:
- **Attendance Management** with intelligent tracking and analytics
- **Leave Request Processing** with policy validation and automated workflows
- **Event Coordination** with registration management and capacity planning
- **Notice Board** with targeted announcements and priority management
- **Resource Management** with secure file handling and access control
- **Intelligent Query Handling** using RAG (Retrieval-Augmented Generation)

## ✨ Key Features

### 🤖 AI Agent System
- **LeaveAgent**: Handles leave requests, policy queries, and validation
- **AttendanceAgent**: Manages attendance analytics and policy compliance
- **EventAgent**: Coordinates events and registration workflows
- **QAAgent**: General question answering with RAG capabilities
- **AgentOrchestrator**: Intelligent routing and multi-agent coordination

### 🔍 RAG (Retrieval-Augmented Generation)
- **Multi-source Knowledge**: Static policies, dynamic records, vectorized knowledge base
- **Contextual Search**: Semantic search across all data sources
- **Policy Integration**: Real-time policy validation and guidance
- **Personalized Responses**: Role-based and context-aware AI responses

### 📊 Core Management Features
- **Role-based Access Control**: Student, Faculty, and Coordinator roles
- **Real-time Analytics**: Comprehensive statistics and insights
- **Policy Compliance**: Automated validation against institutional policies
- **File Management**: Secure resource upload and download system
- **Notification System**: Targeted announcements and alerts

## 🏗️ Architecture

### Backend Stack
- **Flask**: Web framework with Blueprint architecture
- **MongoDB**: Primary database for dynamic records
- **Redis**: Caching and session management
- **ChromaDB**: Vector database for knowledge base
- **Groq**: LLM client for AI agent interactions
- **Sentence-Transformers**: Text embeddings for RAG
- **Pydantic**: Data validation and serialization

### Frontend Stack
- **Next.js**: React framework with SSR capabilities
- **React**: UI components and state management
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client for API communication
- **Zustand**: Lightweight state management
- **React Query**: Server state management

### AI & ML Components
- **Langchain**: Framework for LLM applications
- **Groq API**: High-performance LLM inference
- **ChromaDB**: Vector similarity search
- **Sentence-Transformers**: Text embedding models

## 📋 Prerequisites

- Python 3.8+
- Node.js 18+
- MongoDB 5.0+
- Redis 6.0+
- Docker & Docker Compose (optional)

## 🛠️ Installation

### Option 1: Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd academic-ai-management
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Backend API: http://localhost:5000
   - Frontend: http://localhost:3000
   - MongoDB: localhost:27017
   - Redis: localhost:6379

### Option 2: Local Development

1. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

3. **Database Setup**
   ```bash
   # Start MongoDB and Redis
   mongod
   redis-server
   ```

4. **Run the application**
   ```bash
   # Backend
   cd backend
   python run.py
   
   # Frontend (in another terminal)
   cd frontend
   npm run dev
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# Database Configuration
MONGODB_URI=mongodb://localhost:27017/academic_ai
REDIS_URL=redis://localhost:6379/0

# AI Configuration
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=llama3-8b-8192

# File Storage
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216

# Email Configuration (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password

# Development
DEBUG=true
LOG_LEVEL=INFO
```

### Policy Files

The system uses static JSON policy files for:
- Leave policies (`backend/policies/leave_policies.json`)
- Attendance policies (`backend/policies/attendance_policies.json`)
- Event policies (`backend/policies/event_policies.json`)

## 🚀 Usage

### Authentication

The system preserves existing CSV-based authentication while adding JWT support:

1. **Login**: `POST /api/auth/login`
2. **Token Refresh**: `POST /api/auth/refresh`
3. **Logout**: `POST /api/auth/logout`

### AI Agent Interaction

1. **General Chat**: `POST /api/agents/chat`
2. **Specific Agent**: `POST /api/agents/chat/{agent_name}`
3. **Agent Capabilities**: `GET /api/agents/capabilities`
4. **Agent Health**: `GET /api/agents/health`

### Core Features

#### Attendance Management
- Mark attendance: `POST /api/attendance/mark`
- Bulk attendance: `POST /api/attendance/bulk-mark`
- View attendance: `GET /api/attendance/view/{student_id}`
- Attendance stats: `GET /api/attendance/stats/{student_id}`

#### Leave Management
- Create leave request: `POST /api/leaves/request`
- Approve/reject: `POST /api/leaves/approve/{request_id}`
- View requests: `GET /api/leaves/view/{student_id}`
- Leave balance: `GET /api/leaves/balance/{student_id}`

#### Event Management
- Create event: `POST /api/events/create`
- Register for event: `POST /api/events/register/{event_id}`
- List events: `GET /api/events/list`
- Event details: `GET /api/events/{event_id}`

#### Notice Board
- Post notice: `POST /api/notices/post`
- List notices: `GET /api/notices/list`
- Update notice: `PUT /api/notices/update/{notice_id}`
- Search notices: `GET /api/notices/search`

#### Resource Management
- Upload resource: `POST /api/resources/upload`
- Download resource: `GET /api/resources/download/{resource_id}`
- List resources: `GET /api/resources/list`
- Search resources: `GET /api/resources/search`

## 🤖 AI Agent System

### Agent Types

1. **LeaveAgent**
   - Leave policy queries
   - Request validation
   - Balance calculation
   - Approval recommendations

2. **AttendanceAgent**
   - Attendance analytics
   - Policy compliance
   - Statistics generation
   - Alert management

3. **EventAgent**
   - Event creation guidance
   - Registration management
   - Capacity planning
   - Coordination assistance

4. **QAAgent**
   - General academic queries
   - Policy explanations
   - Procedural guidance
   - Knowledge base search

### RAG System

The RAG system provides:
- **Multi-source Retrieval**: Policies, records, knowledge base
- **Contextual Understanding**: Role-based and query-specific context
- **Policy Integration**: Real-time validation and guidance
- **Personalized Responses**: User-specific and role-aware answers

## 📊 Database Schema

### Collections

1. **users**: User profiles and authentication
2. **attendance**: Attendance records and statistics
3. **leave_requests**: Leave applications and approvals
4. **events**: Event details and registrations
5. **notices**: Announcements and notifications
6. **resources**: File metadata and access control

### Key Fields

- **Role-based Access**: `role` field controls permissions
- **Audit Trail**: `created_at`, `updated_at`, `created_by`
- **Soft Deletes**: `is_deleted` flag for data retention
- **Status Tracking**: Various status fields for workflow management

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -m pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm test
```

### API Testing
```bash
# Using curl or Postman
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "student@example.com", "password": "password"}'
```

## 📈 Monitoring

### Logs
- Application logs: `logs/app.log`
- Error tracking: Centralized error logging
- Performance monitoring: Request/response timing

### Health Checks
- API health: `GET /health`
- Agent health: `GET /api/agents/health`
- Database connectivity: Automatic connection testing

## 🔒 Security

### Authentication & Authorization
- JWT-based session management
- Role-based access control
- Password hashing with bcrypt
- CSRF protection

### Data Protection
- Input validation with Pydantic
- SQL injection prevention
- File upload security
- Secure filename handling

### API Security
- Rate limiting
- Request validation
- Error message sanitization
- CORS configuration

## 🚀 Deployment

### Production Setup
1. Set `FLASK_ENV=production`
2. Configure production databases
3. Set up reverse proxy (nginx)
4. Configure SSL certificates
5. Set up monitoring and logging

### Docker Deployment
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the API reference

## 🗺️ Roadmap

### ✅ Phase 1: Foundation (Complete)
- [x] Project structure setup
- [x] Basic Flask application
- [x] MongoDB integration
- [x] Authentication system
- [x] Basic API endpoints

### ✅ Phase 2: Core Infrastructure (Complete)
- [x] RAG system implementation
- [x] Policy management
- [x] Knowledge base setup
- [x] Agent framework foundation
- [x] Docker configuration

### ✅ Phase 3: Core Features (Complete)
- [x] Attendance management
- [x] Leave request system
- [x] Event management
- [x] Notice board
- [x] Resource management
- [x] Role-based access control
- [x] Policy validation

### ✅ Phase 4: AI Agents (Complete)
- [x] Specialized agent implementation
- [x] Groq LLM integration
- [x] Advanced RAG features
- [x] Multi-agent orchestration
- [x] Agent API endpoints
- [x] Intelligent query routing

### 🔄 Phase 5: Advanced Features (In Progress)
- [ ] Real-time notifications
- [ ] Advanced analytics dashboard
- [ ] Mobile app support
- [ ] Third-party integrations
- [ ] Performance optimization
- [ ] Advanced security features

### 📋 Phase 6: Enterprise Features (Planned)
- [ ] Multi-tenant support
- [ ] Advanced reporting
- [ ] Workflow automation
- [ ] Integration APIs
- [ ] Advanced monitoring
- [ ] Backup and recovery

### 🚀 Phase 7: AI Enhancement (Planned)
- [ ] Advanced RAG capabilities
- [ ] Multi-modal AI support
- [ ] Predictive analytics
- [ ] Natural language processing
- [ ] Machine learning models
- [ ] AI-powered insights

---

**Current Status**: Phase 4 (AI Agents) completed. Moving to Phase 5 (Advanced Features).

