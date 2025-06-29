# Data Analytics SaaS Platform

A full-stack SaaS application for data analysis with file upload, processing, and analytics capabilities.

## 🏗️ Project Structure

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

- Python 3.8+
- Node.js 16+
- PostgreSQL or SQL Server
- Git

### Backend Setup

1. **Clone and navigate to backend**

   ```bash
   git clone <repository-url>
   cd saas-platform/backend
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Database setup**

   ```bash
   alembic upgrade head
   ```

6. **Run the server**
   ```bash
   python run.py
   ```

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

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/saas_db
# Or for SQL Server:
# DATABASE_URL=mssql+pyodbc://user:password@server.database.windows.net:1433/database?driver=ODBC+Driver+17+for+SQL+Server

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External APIs
OPENAI_API_KEY=your-openai-api-key
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# File Storage
UPLOAD_FOLDER=uploads
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=csv,xlsx,xls,json

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Frontend (.env)

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key
```

## 🏛️ Architecture

### Backend Architecture

- **FastAPI** - Modern, fast web framework
- **SQLAlchemy** - Database ORM
- **Alembic** - Database migrations
- **Pydantic** - Data validation
- **JWT** - Authentication
- **Stripe** - Payment processing
- **Pandas** - Data analysis

### Frontend Architecture

- **React 18** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **React Router** - Navigation
- **Axios** - HTTP client
- **Context API** - State management

## 🔐 Authentication Flow

1. User registers/logs in
2. Backend validates credentials
3. JWT token issued
4. Token stored in localStorage
5. Token included in API requests
6. Backend validates token for protected routes

## 📊 Features

### Core Features

- ✅ User authentication (register/login/logout)
- ✅ File upload (CSV, Excel, JSON)
- ✅ Data analysis and processing
- ✅ Analytics dashboard
- ✅ User management
- ✅ Subscription handling

### Advanced Features

- 🔄 Real-time notifications
- 📈 Data visualizations
- 💳 Stripe integration
- 📧 Email notifications
- 🔒 Role-based access
- 📱 Responsive design

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/
```

### Frontend Tests

```bash
cd frontend
npm test
```

## 🚀 Deployment

### Using Docker Compose

```bash
docker-compose up -d
```

### Manual Deployment

1. Set up production database
2. Configure environment variables
3. Build frontend: `npm run build`
4. Deploy backend to your server
5. Serve frontend static files

## 📈 Monitoring

- Health check endpoint: `GET /health`
- Metrics endpoint: `GET /metrics`
- Logs location: `logs/app.log`

## 🔧 Development

### Adding New Endpoints

1. Create endpoint in `backend/app/api/endpoints/`
2. Add to router in `backend/app/api/__init__.py`
3. Create corresponding frontend service

### Database Changes

1. Modify models in `backend/app/models/`
2. Generate migration: `alembic revision --autogenerate -m "description"`
3. Apply migration: `alembic upgrade head`

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- 📧 Email: support@yourcompany.com
- 📖 Documentation: `/docs`
- 🐛 Issues: GitHub Issues
- 💬 Discord: [Your Discord Server]

## 🗺️ Roadmap

- [ ] Mobile app (React Native)
- [ ] Advanced analytics (ML models)
- [ ] Team collaboration features
- [ ] API rate limiting
- [ ] Advanced file formats support
- [ ] Real-time data streaming
- [ ] Multi-tenant architecture
