# 🚀 Akahalu Portfolio

> A production-grade full-stack portfolio platform built with **FastAPI**, **Next.js**, and **PostgreSQL** for showcasing software engineering projects, technical expertise, professional experience, and personal brand content.

---

## 📌 Project Status

![Version](https://img.shields.io/badge/version-v1.0.0-blue)
![Backend](https://img.shields.io/badge/backend-complete-brightgreen)
![Frontend](https://img.shields.io/badge/frontend-in%20progress-yellow)
![Python](https://img.shields.io/badge/python-3.13%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-production%20API-009688)
![Tests](https://img.shields.io/badge/tests-379%20passed-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)

**Current release:** `v1.0.0 — Web Platform`

**Backend status:** Complete and tested
**Frontend status:** In development
**Future release:** `v2.0.0 — Mobile Applications`

---

## 📖 Overview

Akahalu Portfolio is a scalable portfolio and content management platform designed to present software engineering work through a modern public website and a secure administrative dashboard.

The application combines:

* A public developer portfolio
* A portfolio content management system
* Secure authentication and account management
* Role-Based Access Control
* Project, technology, media, and experience management
* Contact inquiry management
* Public and administrative REST APIs
* A future mobile application ecosystem

The project follows modern software engineering practices with a strong focus on:

* Clean architecture
* Security
* Maintainability
* Testability
* Type safety
* Modular design
* Database integrity
* Cloud-ready deployment

---

# 🏷 Version Strategy

## Version 1.0.0 — Web Platform

Version 1 delivers the complete web-based portfolio platform.

It includes:

* FastAPI backend
* PostgreSQL database
* Next.js public website
* Administrative dashboard
* Portfolio content management
* Secure authentication
* Role-Based Access Control
* Public portfolio API
* Contact inquiry system
* Project and experience management
* Responsive desktop and mobile web design

### Version 1 objectives

* Present a professional software engineering portfolio
* Manage portfolio content without directly editing source code
* Provide secure administrative access
* Support projects, technologies, categories, media, links, and experience
* Provide public contact functionality
* Establish a reusable backend for future applications

---

## Version 2.0.0 — Mobile Applications

Version 2 will extend the platform into native mobile applications while reusing the existing FastAPI backend.

Planned applications:

* Android application
* iOS application

Planned capabilities:

* Mobile portfolio browsing
* Mobile administrative access
* Push notifications
* Offline content access
* Biometric authentication
* Resume sharing
* QR-code portfolio sharing
* Deep linking
* Project and experience synchronization
* Mobile contact notifications
* App Store release
* Google Play release

The Version 2 mobile applications will consume the same REST APIs built for Version 1.

---

# ✨ Core Features

## Public Portfolio

* Public profile presentation
* Professional biography
* Skills and technologies
* Featured projects
* Complete project listing
* Project detail pages
* Professional experience timeline
* Featured experience records
* Project category filtering
* Technology filtering
* Search and pagination
* Contact inquiry form
* Resume and professional links
* Responsive user interface
* SEO-ready page structure

---

## Portfolio Administration

* Secure administrator login
* Profile management
* Project management
* Project category management
* Project technology management
* Project media management
* Project link management
* Experience management
* Contact inquiry management
* User administration
* Role and permission management
* Session management
* Soft deletion and restoration
* Public visibility controls
* Featured content controls
* Search, sorting, filtering, and pagination

---

## Authentication and Security

* JWT access tokens
* Refresh-token rotation
* Secure password hashing with Argon2
* Login session tracking
* Session revocation
* Logout from current session
* Logout from all sessions
* Email verification support
* Password-reset support
* Failed-login tracking
* Temporary account lockout
* Role-Based Access Control
* Permission-based authorization
* Superuser authorization bypass
* Account lifecycle management
* Refresh-token revocation
* Structured authentication errors

---

## Portfolio Content Management

The backend provides dedicated modules for:

* Portfolio profile
* Project categories
* Project technologies
* Projects
* Project links
* Project media
* Professional experience
* Contact inquiries

Each module follows a layered architecture:

```text
API Endpoints
    ↓
Pydantic Schemas
    ↓
Service Layer
    ↓
Repository Layer
    ↓
SQLAlchemy Models
    ↓
PostgreSQL Database
```

---

# 🧩 Backend Modules

## Identity and Access Management

* Users
* Roles
* Permissions
* User-role assignments
* Role-permission assignments
* Superuser support
* Administrative user management

## Authentication

* Login
* Current-user retrieval
* Token refresh
* Logout
* Logout from all sessions
* Session tracking
* Refresh-token lifecycle
* Login-attempt tracking

## Account Lifecycle

* Email verification
* Password reset
* Account activation
* Account deactivation
* Token expiration
* Token consumption
* Security event handling

## Portfolio Profile

* Public profile retrieval
* Administrative profile management
* Public/private visibility
* Soft deletion
* Profile restoration

## Project Categories

* Create
* Read
* Update
* Activate or deactivate
* Search
* Sort
* Paginate
* Soft delete
* Restore
* Assigned-project deletion protection

## Project Technologies

* Language classification
* Framework classification
* Library classification
* Database classification
* Cloud classification
* DevOps classification
* Testing classification
* Tool and service classification
* Icon support
* Official URL support
* Brand colour support
* Search and filtering
* Soft deletion and restoration

## Projects

* Project creation
* Project updates
* Project publication lifecycle
* Public/private visibility
* Featured project support
* Category assignment
* Technology assignment
* Project status management
* Slug-based public access
* Search and pagination
* Soft deletion and restoration

## Project Links

* GitHub repository links
* Live demo links
* Documentation links
* External website links
* App Store links
* Google Play links
* Link ordering
* Visibility management

## Project Media

* Cover images
* Screenshots
* Gallery media
* Video references
* Captions
* Alternative text
* Display ordering
* Primary-media selection
* Media visibility management

## Professional Experience

* Employment records
* Contract records
* Internship records
* Freelance records
* Onsite, remote, and hybrid work modes
* Start and end dates
* Current-position support
* Responsibilities
* Achievements
* Company information
* Public visibility
* Featured experience support
* Search, filtering, and pagination
* Soft deletion and restoration

## Contact Inquiries

* Public inquiry submission
* Administrative inquiry management
* Duplicate-submission protection
* Honeypot spam protection
* User-agent handling
* Privacy-preserving IP hashing
* Generic anti-enumeration responses
* Search and status management

---

# 🛠 Technology Stack

## Backend

* Python 3.13+
* FastAPI
* SQLAlchemy 2.0
* Alembic
* PostgreSQL
* Psycopg
* Pydantic
* Pydantic Settings
* Redis
* JWT
* Argon2 password hashing
* Uvicorn
* HTTPX
* Structlog
* Tenacity

## Frontend

* Next.js
* React
* TypeScript
* Tailwind CSS
* shadcn/ui
* TanStack Query
* React Hook Form
* Zod
* Axios
* Framer Motion
* Lucide Icons
* next-themes

## Testing and Quality

* pytest
* pytest-asyncio
* pytest-cov
* Ruff
* MyPy
* Pre-commit

## Infrastructure

* Docker
* Docker Compose
* PostgreSQL
* Redis
* Nginx
* GitHub Actions
* Git

---

# 🏗 Architecture

The project is structured as a modular full-stack application.

```text
Next.js Web Application
        ↓
FastAPI REST API
        ↓
Service Layer
        ↓
Repository Layer
        ↓
SQLAlchemy ORM
        ↓
PostgreSQL Database
```

Supporting services:

```text
Redis
Authentication Sessions
Refresh Tokens
Background-ready Infrastructure
Docker Development Environment
Nginx Reverse Proxy
```

---

# 📂 Project Structure

```text
akahalu-portfolio-starter/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── security/
│   │   ├── services/
│   │   └── main.py
│   │
│   ├── migrations/
│   ├── scripts/
│   ├── tests/
│   ├── alembic.ini
│   ├── pyproject.toml
│   └── uv.lock
│
├── frontend/
│   └── Next.js application
│
├── infrastructure/
│   ├── docker/
│   ├── nginx/
│   └── postgres/
│
├── docs/
│   ├── api/
│   ├── architecture/
│   ├── database/
│   ├── deployment/
│   └── security/
│
├── scripts/
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

# 🔌 API Overview

The API is versioned under:

```text
/api/v1
```

## Root endpoint

```http
GET /
```

Example response:

```json
{
  "message": "Akahalu Portfolio API",
  "status": "running",
  "documentation": "/docs",
  "health": "/api/v1/health"
}
```

---

## API Documentation

Swagger UI:

```text
http://localhost:8000/docs
```

ReDoc:

```text
http://localhost:8000/redoc
```

OpenAPI schema:

```text
http://localhost:8000/openapi.json
```

---

## Public Portfolio Endpoints

```http
GET /api/v1/portfolio/profile
GET /api/v1/portfolio/categories
GET /api/v1/portfolio/categories/{slug}
GET /api/v1/portfolio/technologies
GET /api/v1/portfolio/technologies/{slug}
GET /api/v1/portfolio/projects
GET /api/v1/portfolio/projects/featured
GET /api/v1/portfolio/projects/{slug}
GET /api/v1/portfolio/experiences
GET /api/v1/portfolio/experiences/featured
GET /api/v1/portfolio/experiences/{slug}
POST /api/v1/contact/inquiries
```

---

## Authentication Endpoints

```http
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
POST /api/v1/auth/logout-all
GET  /api/v1/auth/me
```

---

## Administrative API Areas

The administrative API includes protected endpoints for:

```text
Users
Roles
Permissions
Portfolio Profile
Projects
Project Categories
Project Technologies
Project Links
Project Media
Professional Experiences
Contact Inquiries
Sessions
Account Lifecycle
```

Administrative access is controlled using roles and fine-grained permissions.

---

# 🚀 Getting Started

## Prerequisites

Install the following tools before running the project:

* Git
* Docker Desktop
* Python 3.13+
* uv
* Node.js
* npm, pnpm, or yarn

---

## Clone the Repository

```bash
git clone https://github.com/cakahal-johnson/Akahalu-Portfolio.git
```

```bash
cd Akahalu-Portfolio
```

---

# 🐳 Start Supporting Services

Start PostgreSQL, Redis, and other configured services:

```bash
docker compose up -d
```

Inspect running containers:

```bash
docker compose ps
```

Stop services:

```bash
docker compose down
```

---

# ⚙️ Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Install dependencies:

```bash
uv sync
```

Create the backend environment file:

```bash
copy .env.example .env
```

On macOS or Linux:

```bash
cp .env.example .env
```

Update the environment variables before running the application.

---

## Apply Database Migrations

```bash
uv run alembic upgrade head
```

Inspect migration history:

```bash
uv run alembic history
```

Inspect the current revision:

```bash
uv run alembic current
```

---

## Run the Backend

```bash
uv run uvicorn app.main:app --reload
```

The backend will be available at:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

Health endpoint:

```text
http://localhost:8000/api/v1/health
```

---

# 🌐 Frontend Setup

The Next.js frontend is part of Version 1 and is currently under development.

When initialized, it will run from:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Run the development server:

```bash
npm run dev
```

The frontend will be available at:

```text
http://localhost:3000
```

---

# 🔐 Environment Variables

The backend uses Pydantic Settings and reads environment variables from:

```text
backend/.env
```

Core variables include:

```env
APP_NAME="Akahalu Portfolio API"
APP_VERSION="1.0.0"
ENVIRONMENT="local"
DEBUG=false

API_V1_PREFIX="/api/v1"

BACKEND_HOST="127.0.0.1"
BACKEND_PORT=8000

ALLOWED_ORIGINS=["http://localhost:3000"]

DATABASE_URL="postgresql+psycopg://portfolio_user:portfolio_password@127.0.0.1:5432/portfolio_db"
TEST_DATABASE_URL=""

DATABASE_ECHO=false
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_POOL_TIMEOUT=30

REDIS_URL="redis://:portfolio_redis_password@127.0.0.1:6379/0"

JWT_SECRET_KEY="replace-with-a-secure-random-secret"
JWT_ALGORITHM="HS256"
JWT_ISSUER="akahalu-portfolio-api"
JWT_AUDIENCE="akahalu-portfolio-web"

CONTACT_HASH_SECRET_KEY="replace-with-a-secure-contact-hash-secret"
CONTACT_DUPLICATE_WINDOW_MINUTES=15
CONTACT_USER_AGENT_MAX_LENGTH=500

ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30

EMAIL_VERIFICATION_EXPIRE_HOURS=24
PASSWORD_RESET_EXPIRE_MINUTES=60

MAXIMUM_FAILED_LOGIN_ATTEMPTS=5
ACCOUNT_LOCKOUT_MINUTES=15
```

Never commit production secrets to source control.

---

# 🧪 Testing

Run the complete backend test suite:

```bash
uv run pytest -q
```

Current validated result:

```text
379 passed
```

Run a specific integration test:

```bash
uv run pytest tests/integration/test_admin_portfolio_projects_api.py -q
```

Run tests with coverage:

```bash
uv run pytest --cov=app --cov-report=term-missing
```

---

# ✅ Code Quality

## Ruff formatting

```bash
uv run ruff format .
```

## Ruff linting

```bash
uv run ruff check .
```

## MyPy type checking

```bash
uv run mypy app tests
```

Current validated result:

```text
Success: no issues found in 143 source files
```

---

# 🗃 Database Migrations

Create a new migration:

```bash
uv run alembic revision --autogenerate -m "describe migration"
```

Apply all migrations:

```bash
uv run alembic upgrade head
```

Downgrade one migration:

```bash
uv run alembic downgrade -1
```

Inspect migration history:

```bash
uv run alembic history
```

---

# 🔒 Security Principles

The project follows several important security practices:

* Passwords are never stored in plain text
* Refresh tokens are managed separately from access tokens
* Login attempts are tracked
* Account lockout is enforced after repeated failures
* Permissions are checked at protected endpoints
* Sensitive administrative actions require explicit authorization
* Deleted portfolio records are hidden from public endpoints
* Public contact submissions use duplicate and honeypot protection
* Client IP data can be privacy-preservingly hashed
* Authentication errors use structured responses
* Database constraints protect important lifecycle rules
* Public/private and featured-state rules are enforced in the service layer
* Production secrets are loaded from environment variables

---

# 📋 Current Roadmap

## Version 1.0.0 — Web Platform

### Backend

* [x] FastAPI application foundation
* [x] Versioned REST API
* [x] PostgreSQL integration
* [x] Async SQLAlchemy
* [x] Alembic migrations
* [x] JWT authentication
* [x] Refresh tokens
* [x] Session management
* [x] Login-attempt tracking
* [x] Account lifecycle
* [x] Email verification support
* [x] Password-reset support
* [x] Role-Based Access Control
* [x] Permission-based authorization
* [x] Administrative user management
* [x] Portfolio profile
* [x] Project categories
* [x] Project technologies
* [x] Project management
* [x] Project links
* [x] Project media metadata
* [x] Professional experience management
* [x] Public portfolio API
* [x] Contact inquiry API
* [x] Administrative contact management
* [x] Automated integration tests
* [x] Static type checking
* [x] Linting and formatting
* [x] Docker-based supporting services

### Frontend

* [ ] Initialize Next.js application
* [ ] Configure TypeScript
* [ ] Configure Tailwind CSS
* [ ] Configure shadcn/ui
* [ ] Create frontend API client
* [ ] Add TanStack Query
* [ ] Add authentication state management
* [ ] Build public navigation
* [ ] Build home page
* [ ] Build about page
* [ ] Build experience page
* [ ] Build projects page
* [ ] Build project detail page
* [ ] Build contact page
* [ ] Build admin login
* [ ] Build protected admin layout
* [ ] Build admin dashboard
* [ ] Build profile management
* [ ] Build project management
* [ ] Build category management
* [ ] Build technology management
* [ ] Build experience management
* [ ] Build media management
* [ ] Build link management
* [ ] Build contact inquiry management
* [ ] Build user and RBAC management
* [ ] Add responsive design
* [ ] Add dark mode
* [ ] Add accessibility improvements
* [ ] Add SEO metadata
* [ ] Add sitemap
* [ ] Add loading and error states

### Production Readiness

* [ ] Add backend CI pipeline
* [ ] Add frontend CI pipeline
* [ ] Create production Docker images
* [ ] Configure Nginx
* [ ] Configure HTTPS
* [ ] Configure production PostgreSQL
* [ ] Configure production Redis
* [ ] Add production email provider
* [ ] Finalize media-storage strategy
* [ ] Add rate limiting
* [ ] Add structured production logging
* [ ] Add monitoring and error tracking
* [ ] Add database backups
* [ ] Deploy Version 1

---

## Version 2.0.0 — Mobile Applications

* [ ] Define mobile application architecture
* [ ] Create shared mobile design system
* [ ] Build Android application
* [ ] Build iOS application
* [ ] Integrate mobile authentication
* [ ] Add biometric authentication
* [ ] Add offline portfolio access
* [ ] Add push notifications
* [ ] Add deep linking
* [ ] Add QR-code portfolio sharing
* [ ] Add resume sharing
* [ ] Add mobile project browsing
* [ ] Add mobile experience browsing
* [ ] Add selected mobile admin features
* [ ] Publish Android application
* [ ] Publish iOS application

---

# 📚 Documentation

Project documentation will be maintained under:

```text
docs/
```

Planned documentation includes:

* System architecture
* Backend architecture
* Frontend architecture
* API reference
* Database design
* Authentication flow
* Authorization and RBAC
* Security practices
* Local development
* Testing guide
* Deployment guide
* Production operations
* Mobile architecture

---

# 🧭 Development Workflow

Recommended workflow:

```bash
git checkout feature/account-lifecycle
```

Create or update code.

Format:

```bash
uv run ruff format .
```

Lint:

```bash
uv run ruff check .
```

Type-check:

```bash
uv run mypy app tests
```

Test:

```bash
uv run pytest -q
```

Review changes:

```bash
git diff
```

Stage changes:

```bash
git add .
```

Commit:

```bash
git commit -m "type(scope): describe change"
```

Push:

```bash
git push origin feature/account-lifecycle
```

---

# 🤝 Contribution Guidelines

This is currently a personal portfolio project, but contributions and technical feedback are welcome.

Before submitting changes:

* Follow the existing architecture
* Keep API, schema, service, repository, and model responsibilities separate
* Add tests for new behavior
* Run Ruff
* Run MyPy
* Run pytest
* Avoid committing secrets
* Use clear commit messages
* Document important architectural changes

---

# 👨‍💻 Author

## Akahalu Johnson

**Software Engineer | Backend Developer | Full-Stack Developer**

GitHub:

https://github.com/cakahal-johnson

Repository:

https://github.com/cakahal-johnson/Akahalu-Portfolio

---

# 📄 License

This project is licensed under the MIT License.

See the `LICENSE` file for more information.

---

# 🌟 Project Vision

Akahalu Portfolio is intended to become more than a static personal website.

Version 1 establishes a secure and scalable web platform for presenting and managing professional work.

Version 2 will extend the same platform into Android and iOS applications, creating a unified portfolio ecosystem powered by one reusable backend.

The long-term goal is to demonstrate practical experience in:

* Backend engineering
* Frontend engineering
* Mobile development
* API design
* Authentication and authorization
* Database architecture
* DevOps
* Cloud deployment
* Automated testing
* Secure software development
