# Data Analytics SaaS Platform

A full-stack SaaS application for data analysis with file upload, processing, and analytics capabilities.

## � Project Status

**Production Readiness: 7/10** ✅

- ✅ **Backend**: Fully implemented and functional
- ✅ **Authentication**: JWT-based auth with email verification
- ✅ **File Management**: Upload, download, delete with quota tracking
- ✅ **Analytics Engine**: Pandas-based data analysis for CSV, Excel, JSON
- ✅ **Database**: SQLite (dev) / PostgreSQL (production) with Alembic migrations
- ✅ **API Documentation**: Interactive Swagger UI at `/docs`
- 🔄 **Frontend**: React 18 with Vite (ready for development)
- ⚠️ **External Services**: Stripe, OpenAI, SMTP (configuration needed)
- ⚠️ **Testing**: Test infrastructure ready (tests to be written)
- ⚠️ **Deployment**: Docker Compose configured (production setup needed)

## �🏗️ Project Structure

```
saas-platform/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── database.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   └── file.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   └── file.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py
│   │   │   └── endpoints/
│   │   │       ├── __init__.py
│   │   │       ├── auth.py
│   │   │       ├── users.py
│   │   │       ├── files.py
│   │   │       └── analytics.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── file_service.py
│   │   │   └── analytics_service.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── email.py
│   │       └── payments.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_auth.py
│   │   └── test_files.py
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   ├── requirements.txt
│   ├── .env.example
│   ├── alembic.ini
│   └── run.py
├── frontend/
│   ├── public/
│   │   ├── index.html
│   │   └── favicon.ico
│   ├── src/
│   │   ├── components/
│   │   │   ├── auth/
│   │   │   │   ├── LoginForm.jsx
│   │   │   │   ├── RegisterForm.jsx
│   │   │   │   └── AuthLayout.jsx
│   │   │   ├── dashboard/
│   │   │   │   ├── Dashboard.jsx
│   │   │   │   ├── StatsCard.jsx
│   │   │   │   └── RecentActivity.jsx
│   │   │   ├── upload/
│   │   │   │   ├── FileUpload.jsx
│   │   │   │   ├── UploadZone.jsx
│   │   │   │   └── FileList.jsx
│   │   │   ├── analytics/
│   │   │   │   ├── AnalyticsView.jsx
│   │   │   │   ├── AnalysisCard.jsx
│   │   │   │   └── DataVisualization.jsx
│   │   │   ├── settings/
│   │   │   │   ├── Settings.jsx
│   │   │   │   ├── AccountSettings.jsx
│   │   │   │   └── SubscriptionSettings.jsx
│   │   │   ├── layout/
│   │   │   │   ├── Navigation.jsx
│   │   │   │   ├── Sidebar.jsx
│   │   │   │   └── Layout.jsx
│   │   │   └── common/
│   │   │       ├── Button.jsx
│   │   │       ├── Input.jsx
│   │   │       ├── Modal.jsx
│   │   │       ├── Notification.jsx
│   │   │       └── LoadingSpinner.jsx
│   │   ├── hooks/
│   │   │   ├── useAuth.js
│   │   │   ├── useApi.js
│   │   │   └── useNotification.js
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   ├── auth.js
│   │   │   └── files.js
│   │   ├── context/
│   │   │   ├── AuthContext.jsx
│   │   │   └── NotificationContext.jsx
│   │   ├── utils/
│   │   │   ├── constants.js
│   │   │   ├── helpers.js
│   │   │   └── validators.js
│   │   ├── styles/
│   │   │   ├── index.css
│   │   │   └── tailwind.css
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── .env.example
├── docs/
│   ├── api.md
│   ├── deployment.md
│   └── architecture.md
├── docker-compose.yml
├── .gitignore
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.13** (or 3.11+)
- **Node.js 18+** (for frontend)
- **Docker Desktop** (optional, for PostgreSQL/Redis)
- **Git**

### Backend Setup (Development)

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd Data_Analytics_Saas_platform
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv

   # On Windows:
   venv\Scripts\activate

   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Environment setup**

   The `.env` file is already created with development defaults. For production, update:

   ```bash
   # Edit backend/.env with your configuration
   # Key settings to update for production:
   # - SECRET_KEY (generate a secure random key)
   # - DATABASE_URL (switch to PostgreSQL)
   # - SMTP settings (for email functionality)
   # - Stripe keys (for payments)
   # - OpenAI API key (for AI features)
   ```

5. **Database setup**

   ```bash
   # Initialize Alembic (already done)
   # Create initial migration (already done)

   # Apply migrations to create tables
   alembic upgrade head
   ```

6. **Run the development server**

   ```bash
   # From backend directory
   python -m uvicorn app.main:app --reload --port 8000

   # Or use the main.py directly
   python app/main.py
   ```

7. **Access the API**

   - **API Documentation**: http://127.0.0.1:8000/docs
   - **Alternative Docs**: http://127.0.0.1:8000/redoc
   - **Health Check**: http://127.0.0.1:8000/health
   - **Root Endpoint**: http://127.0.0.1:8000/

### Frontend Setup

1. **Navigate to frontend**

   ```bash
   cd ../frontend
   ```

2. **Install dependencies**

   ```bash
   npm install
   ```

3. **Environment setup**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

## 📋 Environment Variables

### Backend (.env)

**Current Development Configuration:**

```env
# Database Configuration
# Using SQLite for development (no PostgreSQL installation needed)
DATABASE_URL=sqlite:///./saas_db.sqlite
# For PostgreSQL (when Docker is running):
# DATABASE_URL=postgresql://postgres:password@localhost:5432/saas_db

# Security
SECRET_KEY=dev-secret-key-change-in-production-12345678901234567890
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=10080

# Frontend URL
FRONTEND_URL=http://localhost:3000

# External APIs (Optional - configure when needed)
OPENAI_API_KEY=
STRIPE_SECRET_KEY=
STRIPE_PUBLISHABLE_KEY=
STRIPE_WEBHOOK_SECRET=

# Email Configuration (Optional - configure when needed)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=

# File Upload Settings
UPLOAD_FOLDER=uploads
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=["csv","xlsx","xls","json","txt"]

# Redis (Optional - for caching)
REDIS_URL=redis://localhost:6379

# CORS (JSON array format)
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]

# Feature Flags
ENABLE_ANALYTICS=true
ENABLE_PAYMENTS=false
ENABLE_EMAIL=false
```

**⚠️ Production Configuration:**

For production deployment, you MUST:

1. Generate a secure `SECRET_KEY` (use `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
2. Switch to PostgreSQL database
3. Configure SMTP settings for email functionality
4. Add Stripe keys for payment processing
5. Add OpenAI API key for AI features
6. Enable HTTPS and update CORS_ORIGINS

### Frontend (.env)

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key
```

## 🏛️ Architecture

### Backend Architecture (✅ Fully Implemented)

- **FastAPI 0.115.6** - Modern, fast async web framework
- **SQLAlchemy 2.0.36** - Database ORM with declarative models
- **Alembic 1.14.0** - Database migrations (configured and working)
- **Pydantic 2.10.5** - Data validation and settings management
- **JWT (python-jose 3.3.0)** - Token-based authentication with HS256
- **Passlib + Bcrypt** - Secure password hashing
- **Pandas 2.2.3** - Data analysis engine (Python 3.13 compatible)
- **Stripe 11.3.0** - Payment processing integration (ready)
- **OpenAI 1.58.1** - AI integration (ready)
- **aiosmtplib** - Async email sending

**Key Backend Features:**

- ✅ JWT authentication with access & refresh tokens
- ✅ Email verification & password reset flows
- ✅ File upload with validation & quota management
- ✅ Pandas-based analytics for CSV, Excel, JSON
- ✅ User subscription & usage tracking
- ✅ Soft delete pattern for files
- ✅ Background task processing
- ✅ Comprehensive error handling & logging
- ✅ CORS & security middleware
- ✅ Interactive API documentation (Swagger UI)

### Frontend Architecture (🔄 Ready for Development)

- **React 18** - UI framework with hooks
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **Axios** - HTTP client for API calls
- **Context API** - State management

## 🔐 Authentication Flow (✅ Implemented)

1. **User Registration**

   - User submits registration form (username, email, password)
   - Backend validates input and checks for duplicates
   - Password is hashed using bcrypt
   - User record created with verification token
   - Email verification sent (if ENABLE_EMAIL=true)
   - Returns user data and JWT tokens

2. **User Login**

   - User submits credentials (username/email + password)
   - Backend verifies password using bcrypt
   - JWT access token (30 min) and refresh token (7 days) issued
   - Tokens returned to client

3. **Token Usage**

   - Client stores tokens (localStorage/sessionStorage)
   - Access token included in Authorization header: `Bearer <token>`
   - Backend validates token using `get_current_user` dependency
   - Protected routes require valid token

4. **Token Refresh**

   - When access token expires, use refresh token
   - POST to `/api/v1/auth/refresh` with refresh token
   - New access token issued

5. **Email Verification** (Optional)

   - User clicks verification link from email
   - Backend validates token and marks user as verified
   - Verified users have full access

6. **Password Reset**
   - User requests password reset
   - Reset token generated and emailed
   - User submits new password with token
   - Password updated and user can login

## 📊 Features

### ✅ Implemented Core Features

- ✅ **User Authentication**

  - Registration with email verification
  - Login with JWT tokens (access + refresh)
  - Password reset flow
  - User profile management
  - Subscription status tracking

- ✅ **File Management**

  - Upload files (CSV, Excel, JSON, TXT)
  - File validation (type, size, quota)
  - List files with pagination
  - Download files
  - Soft delete with storage tracking
  - File metadata management

- ✅ **Data Analytics**

  - Automatic file analysis (background tasks)
  - CSV analysis (summary stats, missing values, data types)
  - Excel analysis (multi-sheet support)
  - JSON analysis (structure detection)
  - Analysis results storage and retrieval

- ✅ **User Management**
  - User profiles with avatar, bio, company info
  - Usage statistics (files, analyses, storage, API calls)
  - Subscription management (plan, status, dates)
  - Stripe customer integration ready
  - Storage quota enforcement

### 🔄 Ready for Integration

- 🔄 **Stripe Payments** - Integration code ready, needs API keys
- 🔄 **Email Notifications** - Email functions implemented, needs SMTP config
- 🔄 **OpenAI Integration** - Ready for AI-powered features
- 🔄 **Redis Caching** - Configuration ready, needs Redis server

### 📋 Planned Features

- � Real-time notifications (WebSocket)
- � Data visualizations (charts, graphs)
- � Team collaboration features
- � Advanced role-based access control
- 📋 API rate limiting
- � Advanced file format support
- 📋 Real-time data streaming
- 📋 Multi-tenant architecture

## 🧪 Testing

### Backend Tests (Infrastructure Ready)

```bash
cd backend

# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py
```

**Test Infrastructure:**

- ✅ pytest configured in requirements.txt
- ✅ httpx for async testing
- ⚠️ Test files need to be written

### Frontend Tests

```bash
cd frontend
npm test
```

## � API Documentation

### Interactive Documentation

Once the server is running, access:

- **Swagger UI**: http://127.0.0.1:8000/docs

  - Interactive API testing
  - Try out endpoints directly
  - View request/response schemas

- **ReDoc**: http://127.0.0.1:8000/redoc
  - Clean, readable documentation
  - Better for reference

### API Endpoints

#### Authentication (`/api/v1/auth`)

- `POST /register` - Register new user
- `POST /login` - Login and get tokens
- `POST /refresh` - Refresh access token
- `POST /verify-email` - Verify email address
- `POST /forgot-password` - Request password reset
- `POST /reset-password` - Reset password with token

#### Users (`/api/v1/users`)

- `GET /me` - Get current user profile
- `PUT /me` - Update user profile
- `GET /me/stats` - Get user statistics

#### Files (`/api/v1/files`)

- `POST /upload` - Upload file
- `GET /` - List files (with pagination)
- `GET /{file_id}` - Get file details
- `DELETE /{file_id}` - Delete file
- `GET /{file_id}/download` - Download file
- `GET /{file_id}/metadata` - Get file metadata
- `PATCH /{file_id}` - Update file metadata

#### Analytics (`/api/v1/analytics`)

- `POST /analyze/{file_id}` - Trigger file analysis
- `GET /results/{file_id}` - Get analysis results

## 🚀 Deployment

### Development (Current Setup)

```bash
# Backend (SQLite database)
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm run dev
```

### Production with Docker Compose

```bash
# Start all services (PostgreSQL, Redis, Backend, Frontend)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

**Docker Services:**

- PostgreSQL (port 5432)
- Redis (port 6379)
- Backend API (port 8000)
- Frontend (port 3000)
- Nginx (ports 80, 443) - production profile
- Worker (Celery) - production profile
- Prometheus (port 9090) - monitoring profile
- Grafana (port 3001) - monitoring profile

### Manual Production Deployment

1. **Set up production database**

   ```bash
   # PostgreSQL
   createdb saas_db
   ```

2. **Configure environment variables**

   ```bash
   # Update backend/.env with production values
   # - Generate secure SECRET_KEY
   # - Set DATABASE_URL to PostgreSQL
   # - Configure SMTP settings
   # - Add Stripe API keys
   # - Add OpenAI API key
   ```

3. **Run database migrations**

   ```bash
   cd backend
   alembic upgrade head
   ```

4. **Build frontend**

   ```bash
   cd frontend
   npm run build
   ```

5. **Deploy backend**

   ```bash
   # Using gunicorn with uvicorn workers
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

6. **Serve frontend**
   - Use Nginx to serve static files from `frontend/dist`
   - Configure reverse proxy to backend API

## 📈 Monitoring

### Health & Metrics Endpoints

- **Health Check**: `GET /health`

  ```json
  {
    "status": "healthy",
    "timestamp": 1234567890.123,
    "version": "1.0.0"
  }
  ```

- **Metrics**: `GET /metrics`
  ```json
  {
    "uptime": 1234567890.123,
    "database": "connected",
    "status": "operational"
  }
  ```

### Logging

- **Log Location**: `backend/logs/app.log`
- **Log Format**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- **Log Levels**: INFO, WARNING, ERROR
- **Console Output**: Enabled for development

### Database

- **Development**: SQLite (`backend/saas_db.sqlite`)
- **Production**: PostgreSQL (configured in docker-compose.yml)
- **Migrations**: Alembic (`backend/alembic/versions/`)

## 🔧 Development

### Adding New Endpoints

1. **Create endpoint file** in `backend/app/api/endpoints/`

   ```python
   from fastapi import APIRouter, Depends
   from app.api.deps import get_current_user

   router = APIRouter()

   @router.get("/my-endpoint")
   async def my_endpoint(current_user = Depends(get_current_user)):
       return {"message": "Hello"}
   ```

2. **Add to main router** in `backend/app/main.py`

   ```python
   from app.api.endpoints import my_module
   app.include_router(my_module.router, prefix="/api/v1/my-module", tags=["my-module"])
   ```

3. **Create corresponding frontend service** in `frontend/src/services/`

### Database Changes

1. **Modify models** in `backend/app/models/`

   ```python
   from sqlalchemy import Column, Integer, String
   from app.core.database import Base

   class MyModel(Base):
       __tablename__ = "my_table"
       id = Column(Integer, primary_key=True, index=True)
       name = Column(String, nullable=False)
   ```

2. **Generate migration**

   ```bash
   cd backend
   alembic revision --autogenerate -m "Add my_table"
   ```

3. **Review migration** in `backend/alembic/versions/`

4. **Apply migration**

   ```bash
   alembic upgrade head
   ```

5. **Rollback if needed**
   ```bash
   alembic downgrade -1
   ```

### Project Structure Best Practices

- **Models** (`app/models/`) - Database models (SQLAlchemy)
- **Schemas** (`app/schemas/`) - Pydantic models for validation
- **Services** (`app/services/`) - Business logic
- **Endpoints** (`app/api/endpoints/`) - API routes
- **Dependencies** (`app/api/deps.py`) - Reusable dependencies
- **Utils** (`app/utils/`) - Helper functions
- **Core** (`app/core/`) - Configuration, security, database

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
   - Follow the existing code style
   - Add tests for new features
   - Update documentation as needed
4. **Commit your changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```
5. **Push to your branch**
   ```bash
   git push origin feature/amazing-feature
   ```
6. **Open a Pull Request**
   - Describe your changes
   - Reference any related issues
   - Wait for review

### Contribution Guidelines

- Write clear, descriptive commit messages
- Follow PEP 8 for Python code
- Use ESLint/Prettier for JavaScript code
- Add tests for new features
- Update README.md if needed
- Keep pull requests focused on a single feature/fix

## 🗺️ Roadmap

### Phase 1: Core Completion (Current)

- [x] Backend API implementation
- [x] Authentication & authorization
- [x] File upload & management
- [x] Data analytics engine
- [x] Database migrations
- [ ] Comprehensive test suite
- [ ] Frontend implementation
- [ ] End-to-end testing

### Phase 2: External Integrations

- [ ] Stripe payment integration (code ready)
- [ ] Email notifications (code ready)
- [ ] OpenAI integration for AI features
- [ ] Redis caching implementation
- [ ] S3/Cloud storage for files

### Phase 3: Advanced Features

- [ ] Real-time notifications (WebSocket)
- [ ] Data visualizations (charts, graphs)
- [ ] Team collaboration features
- [ ] Advanced role-based access control
- [ ] API rate limiting
- [ ] Advanced file formats (Parquet, Avro)
- [ ] Real-time data streaming
- [ ] Scheduled analytics jobs

### Phase 4: Scale & Performance

- [ ] Multi-tenant architecture
- [ ] Horizontal scaling
- [ ] CDN integration
- [ ] Advanced caching strategies
- [ ] Performance monitoring
- [ ] Load balancing

### Phase 5: Mobile & Extensions

- [ ] Mobile app (React Native)
- [ ] Browser extensions
- [ ] Desktop app (Electron)
- [ ] Public API with rate limiting
- [ ] Webhook support

## 📊 Implementation Status

### ✅ Completed (100%)

- Core security module (password hashing, JWT)
- User model with full profile & subscription tracking
- Authentication dependencies & middleware
- Authentication service
- File upload & management endpoints
- Analytics endpoints with pandas integration
- Email utility functions
- Database configuration & migrations
- Environment configuration
- API documentation

### 🔄 In Progress (0%)

- Frontend React application
- Comprehensive test suite

### ⚠️ Pending Configuration

- External service API keys (Stripe, OpenAI, SMTP)
- Production database setup (PostgreSQL)
- Redis server setup
- Production deployment

## 🎓 Learning Resources

### Backend (FastAPI)

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Alembic Migrations](https://alembic.sqlalchemy.org/)
- [Pydantic Validation](https://docs.pydantic.dev/)

### Frontend (React)

- [React Documentation](https://react.dev/)
- [Vite Guide](https://vitejs.dev/guide/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [React Router](https://reactrouter.com/)

### DevOps

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [PostgreSQL Guide](https://www.postgresql.org/docs/)

## 🔍 Troubleshooting

### Common Issues

**1. Import errors when running the server**

```bash
# Make sure you're in the backend directory
cd backend
# Activate virtual environment
source ../venv/bin/activate  # macOS/Linux
..\venv\Scripts\activate     # Windows
```

**2. Database migration errors**

```bash
# Reset migrations (development only)
rm -rf alembic/versions/*
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

**3. CORS errors from frontend**

```bash
# Check CORS_ORIGINS in backend/.env
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

**4. File upload fails**

```bash
# Ensure uploads directory exists
mkdir -p backend/uploads
# Check MAX_FILE_SIZE in .env
```

**5. Email not sending**

```bash
# Email is disabled by default
# Set ENABLE_EMAIL=true and configure SMTP settings in .env
```

## 📞 Support & Contact

- **Documentation**: Available at `/docs` when server is running
- **Issues**: GitHub Issues for bug reports
- **Questions**: GitHub Discussions for questions
- **Email**: support@yourcompany.com (configure in production)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with ❤️ using FastAPI, React, and modern web technologies**

**Current Version**: 1.0.0
**Last Updated**: December 2025
**Status**: Development Ready ✅
