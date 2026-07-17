# 🚀 Akahalu Portfolio

> A modern, production-grade portfolio platform built with **FastAPI**, **Next.js**, and **PostgreSQL**, showcasing software engineering projects, technical expertise, and professional experience.

---

## 📖 Overview

Akahalu Portfolio is designed as a scalable full-stack web application that combines a personal portfolio with a content management system (CMS). It follows modern software engineering practices, emphasizing clean architecture, security, maintainability, and cloud-ready deployment.

---

## ✨ Features

- Personal portfolio showcase
- Project management
- Blog & article publishing
- Skills and experience management
- Contact form with email integration
- Resume download
- Role-Based Access Control (RBAC)
- Authentication & authorization
- RESTful API
- Dockerized development environment
- Automated database migrations
- Production-ready architecture

---

# 🛠 Technology Stack

## Backend

- Python 3.13+
- FastAPI
- SQLAlchemy 2.0
- Alembic
- PostgreSQL
- Redis
- Pydantic
- JWT Authentication

## Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS
- shadcn/ui

## Infrastructure

- Docker
- Docker Compose
- Nginx
- GitHub Actions
- Git

---

# 📂 Project Structure

```text
akahalu-portfolio-starter/
│
├── backend/              # FastAPI backend
├── frontend/             # Next.js frontend
├── infrastructure/       # Docker, Nginx, deployment
├── docs/                 # Architecture & documentation
├── docker-compose.yml
└── README.md
```

---

# 🚀 Getting Started

## Clone the repository

```bash
git clone https://github.com/cakahal-johnson/Akahalu-Portfolio.git
```

```bash
cd Akahalu-Portfolio
```

---

## Start Docker

```bash
docker compose up -d
```

---

## Backend

```bash
cd backend
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

API:

```
http://localhost:8000
```

Swagger UI:

```
http://localhost:8000/docs
```

---

# 🧪 Testing

```bash
uv run pytest
```

---

# 📌 Roadmap

- [x] Backend foundation
- [x] Database models
- [x] Alembic migrations
- [x] Authentication (JWT)
- [ ] RBAC
- [ ] Portfolio API
- [ ] CMS
- [ ] Media Management
- [ ] Blog Module
- [ ] Contact API
- [ ] Next.js Frontend
- [ ] Admin Dashboard
- [ ] CI/CD Pipeline
- [ ] Production Deployment

---

# 📚 Documentation

Project documentation will include:

- System Architecture
- API Reference
- Database Design
- Authentication
- Security
- Deployment Guide
- Development Guide

---

# 👨‍💻 Author

**Akahalu Johnson**

Software Engineer | Backend Developer | Full-Stack Developer

GitHub:
https://github.com/cakahal-johnson

---

# 📄 License

This project is licensed under the MIT License.