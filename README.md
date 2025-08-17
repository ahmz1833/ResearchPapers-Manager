# Research Papers Manager

A university research papers management system built with Flask, MongoDB, and Redis. The system provides efficient paper management, real-time view tracking, intelligent caching, and citation management for academic institutions.

## 🏗️ System Architecture

### Core Technologies
- **Backend**: Python 3.11+ with Flask 3.0.3
- **Database**: MongoDB 7.0 (persistent storage)
- **Cache**: Redis 7.2 (caching, view tracking, username validation)
- **Deployment**: Docker Compose with multi-container setup
- **Authentication**: Session-based with X-User-ID headers
- **Password Security**: bcrypt hashing
- **Background Tasks**: APScheduler for automated view synchronization

### Key Features
- **User Management**: Registration with unique username validation via Redis
- **Paper Upload**: Multi-metadata paper submission with citation support
- **Advanced Search**: Full-text search with MongoDB text indexes and Redis caching
- **Real-time Metrics**: Live view tracking with periodic MongoDB synchronization
- **Citation Network**: Paper citation relationships with count tracking
- **Data Seeding**: Automated generation of test data (100 users, 1000 papers)

## 📊 Database Schema

### MongoDB Collections

#### Users Collection
```javascript
{
  _id: ObjectId,
  username: String (unique, 3-20 chars, alphanumeric + underscore),
  name: String (max 100 chars),
  email: String (valid email format, max 100 chars),
  password: String (bcrypt hashed),
  department: String (max 100 chars)
}

// Indexes
db.users.createIndex({ "username": 1 }, { unique: true })
```

#### Papers Collection
```javascript
{
  _id: ObjectId,
  title: String (required, max 200 chars),
  authors: [String] (1-5 items, each max 100 chars),
  abstract: String (required, max 1000 chars),
  publication_date: Date (ISO format),
  journal_conference: String (optional, max 200 chars),
  keywords: [String] (1-5 items, each max 50 chars),
  uploaded_by: ObjectId (reference to Users),
  views: Number (default 0, synced from Redis)
}

// Indexes
db.papers.createIndex(
  { "title": "text", "abstract": "text", "keywords": "text" },
  { name: "text_papers", default_language: "english" }
)
```

#### Citations Collection
```javascript
{
  _id: ObjectId,
  paper_id: ObjectId (citing paper, reference to Papers),
  cited_paper_id: ObjectId (cited paper, reference to Papers)
}

// Indexes
db.citations.createIndex({ "cited_paper_id": 1 })
```

### Redis Data Structures

#### Username Availability Cache
```redis
# Hash table for username availability
HSET usernames <username> 1
HEXISTS usernames <username>  # Check availability
```

#### Search Results Cache
```redis
# Key format: search:<search_term>:<sort_by>:<order>
# TTL: 300 seconds (5 minutes)
SETEX search:machine_learning:publication_date:desc 300 '{"papers":[...]}'
```

#### Paper View Tracking
```redis
# Key format: paper_views:<paper_id>
INCR paper_views:507f1f77bcf86cd799439011
GET paper_views:507f1f77bcf86cd799439011
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- Git

### Installation & Running

1. **Clone the repository**
```bash
git clone <repository-url>
cd ResearchPapers-Manager
```

2. **Environment Setup**
```bash
# Copy environment template
cp .env.example .env
# Edit .env if needed (defaults work for Docker setup)
```

3. **Start with Docker Compose**
```bash
# Build and start all services
make up

# Or manually:
docker compose up --build -d
```

4. **Verify Installation**
```bash
# Check API health
curl http://localhost:8000/health/

# Check all services
docker compose ps
```

5. **Seed Test Data**
```bash
# Generate 100 users and 1000 papers with citations
make seed-data
```

### Available Commands

```bash
# Start services
make up

# Stop services
make down

# View logs
make logs

# Run tests
make test

# Seed database
make seed-data

# Clean everything
make clean

# Format code
make fmt
```

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Health Check
```http
GET /health/
```
**Response:**
```json
{
  "app": "research-papers-manager",
  "mongo": true,
  "redis": true,
  "status": "ok"
}
```

#### 2. User Registration
```http
POST /signup
Content-Type: application/json

{
  "username": "johndoe123",
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepass123",
  "department": "Computer Science"
}
```
**Response (201):**
```json
{
  "message": "User registered",
  "user_id": "507f1f77bcf86cd799439011"
}
```

#### 3. User Login
```http
POST /login
Content-Type: application/json

{
  "username": "johndoe123",
  "password": "securepass123"
}
```
**Response (200):**
```json
{
  "message": "Login successful",
  "user_id": "507f1f77bcf86cd799439011"
}
```

#### 4. Paper Upload
```http
POST /papers/
X-User-ID: 507f1f77bcf86cd799439011
Content-Type: application/json

{
  "title": "Advanced Machine Learning Techniques",
  "authors": ["Dr. Jane Smith", "Prof. John Doe"],
  "abstract": "This paper explores novel approaches...",
  "publication_date": "2024-01-15",
  "journal_conference": "IEEE Computer Vision",
  "keywords": ["machine learning", "AI", "computer vision"],
  "citations": ["507f1f77bcf86cd799439012"]
}
```
**Response (201):**
```json
{
  "message": "Paper uploaded",
  "paper_id": "507f1f77bcf86cd799439013"
}
```

#### 5. Paper Search
```http
GET /papers/?search=machine learning&sort_by=publication_date&order=desc
```
**Response (200):**
```json
{
  "papers": [
    {
      "id": "507f1f77bcf86cd799439013",
      "title": "Advanced Machine Learning Techniques",
      "authors": ["Dr. Jane Smith", "Prof. John Doe"],
      "publication_date": "2024-01-15",
      "journal_conference": "IEEE Computer Vision",
      "keywords": ["machine learning", "AI", "computer vision"]
    }
  ]
}
```

#### 6. Paper Details
```http
GET /papers/507f1f77bcf86cd799439013
```
**Response (200):**
```json
{
  "id": "507f1f77bcf86cd799439013",
  "title": "Advanced Machine Learning Techniques",
  "authors": ["Dr. Jane Smith", "Prof. John Doe"],
  "abstract": "This paper explores novel approaches...",
  "publication_date": "2024-01-15",
  "journal_conference": "IEEE Computer Vision",
  "keywords": ["machine learning", "AI", "computer vision"],
  "citation_count": 5,
  "views": 127
}
```

#### 7. Admin Endpoints
```http
# View sync status
GET /admin/sync-status

# Manual sync trigger
POST /admin/sync-now
```

### Error Responses

```json
// 400 Bad Request
{
  "error": "Validation failed",
  "details": ["Title is required", "Password must be at least 8 characters"]
}

// 401 Unauthorized
{
  "error": "X-User-ID header is required"
}

// 409 Conflict
{
  "error": "Username is already taken"
}

// 404 Not Found
{
  "error": "Paper not found"
}
```

## 🔄 Background Tasks

### View Synchronization
- **Frequency**: Every 10 minutes (configurable via `VIEWS_SYNC_INTERVAL_MIN`)
- **Process**: 
  1. Retrieves all `paper_views:*` keys from Redis
  2. Updates MongoDB papers with view counts using `$inc` operation
  3. Resets Redis counters to 0
  4. Logs sync statistics

### Cache Management
- **Search Cache**: 5-minute TTL, invalidated on new paper uploads
- **Username Cache**: Persistent hash table for registration validation
- **View Tracking**: Real-time Redis counters with periodic MongoDB sync

## 🧪 Testing

### Comprehensive Test Suite

The project includes a complete test suite (`scripts/test_complete.py`) covering:

- **Health & Connectivity**: API availability and service health
- **Authentication**: Registration, login, validation, duplicate handling
- **Paper Management**: Upload, search, validation, citations
- **Admin Functions**: Sync status and manual synchronization
- **Cache & Integration**: Search caching, view tracking, cache invalidation
- **Error Handling**: Invalid inputs, authentication failures, not found cases

### Running Tests
```bash
# Run full test suite
make test

# Run tests manually
python scripts/test_complete.py

# Test with seeded data
make seed-data && make test
```

### Test Coverage
- ✅ User registration with unique username validation
- ✅ User login with credential verification
- ✅ Paper upload with metadata validation
- ✅ Full-text search with caching
- ✅ Paper details with view tracking
- ✅ Citation relationship management
- ✅ Real-time view counting
- ✅ Background synchronization
- ✅ Admin monitoring endpoints
- ✅ Error handling and validation

## 🔧 Development

### Project Structure
```
app/
├── api/          # REST API endpoints
│   ├── auth.py   # Authentication routes
│   ├── papers.py # Paper management routes
│   ├── admin.py  # Admin monitoring routes
│   └── health.py # Health check route
├── models/       # Data models
│   ├── user.py   # User model with MongoDB operations
│   └── paper.py  # Paper model with search and citations
├── services/     # Business logic services
│   └── view_sync.py # View synchronization service
├── utils/        # Utility functions
│   ├── auth.py   # Authentication helpers
│   ├── cache.py  # Redis caching service
│   ├── validation.py # Input validation
│   ├── paper_validation.py # Paper-specific validation
│   └── password.py # Password hashing utilities
├── config.py     # Configuration management
├── extensions.py # Database connections
├── factory.py    # Flask app factory
└── scheduler.py  # Background task scheduler

scripts/
├── test_complete.py # Comprehensive test suite
├── seed_data.py     # Database seeding script
├── test_cache.py    # Cache-specific tests (legacy)
└── test_papers.py   # Paper-specific tests (legacy)

posting-collection/  # API testing collection for tools like Posting
├── auth/           # Authentication test requests
├── papers/         # Paper management test requests
└── admin/          # Admin endpoint test requests
```

### Local Development Setup

1. **Create virtual environment**
```bash
make venv
source .venv/bin/activate
```

2. **Install dependencies**
```bash
pip install -e .
```

3. **Start services locally**
```bash
# Start MongoDB and Redis with Docker
docker compose up mongo redis -d

# Run Flask app locally
python wsgi.py
```

### Configuration

Environment variables (`.env`):
```bash
# Application
FLASK_ENV=development
APP_NAME=research-papers-manager
PORT=8000

# Database
MONGODB_URI=mongodb://mongo:27017
MONGODB_DB=research_db

# Redis
REDIS_URL=redis://redis:6379/0

# Background Tasks
ENABLE_SCHEDULER=true
VIEWS_SYNC_INTERVAL_MIN=10
```

## 🔗 API Testing

The project includes a `posting-collection/` directory with API test files for [Posting](https://posting.sh) Client. These files provide ready-to-use API requests for testing all endpoints.

-----

*Made by AmirHossein MohammadZadeh 402106434 for DB Exercise 5*
