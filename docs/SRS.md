# Software Requirements Specification (SRS)
# AI Recruitment Platform

**Version:** 1.0.0  
**Date:** 2026-08-06  
**Status:** Approved

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Overall Description](#2-overall-description)
3. [Functional Requirements](#3-functional-requirements)
4. [Non-Functional Requirements](#4-non-functional-requirements)
5. [System Constraints](#5-system-constraints)
6. [Use Cases](#6-use-cases)

---

## 1. Introduction

### 1.1 Purpose
This document defines the software requirements for the **AI Recruitment Platform**, a comprehensive, AI-powered hiring management system built as a single FastAPI application (Modular Monolith).

### 1.2 Scope
The platform serves recruitment agencies, HR departments, and companies of all sizes. It automates the end-to-end recruitment lifecycle: from job posting and candidate sourcing to AI-powered matching, interview scheduling, offer management, and onboarding.

### 1.3 Definitions

| Term | Definition |
|------|------------|
| ATS | Applicant Tracking System |
| RBAC | Role-Based Access Control |
| JWT | JSON Web Token |
| CV / Resume | Candidate curriculum vitae document |
| AI Matching | AI-powered candidate-to-job compatibility scoring |
| Pipeline | The ATS stage progression for a candidate application |

### 1.4 Technology Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.12+ |
| Web Framework | FastAPI |
| ORM | SQLAlchemy 2.x |
| Database | PostgreSQL 15+ |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Configuration | Pydantic Settings |
| Templates | Jinja2 |
| Frontend Enhancement | HTMX + Alpine.js |
| Styling | TailwindCSS |
| Authentication | JWT (python-jose) + Passlib (bcrypt) |
| Testing | pytest + pytest-asyncio |
| Package Manager | uv |

---

## 2. Overall Description

### 2.1 Product Perspective
A standalone, production-ready web application providing:
- Full-featured recruitment management
- AI-powered candidate matching
- Multi-tenant company isolation
- Role-based access control
- Real-time notifications

### 2.2 User Classes and Characteristics

| Role | Description | Access Level |
|------|-------------|-------------|
| **Super Admin** | Platform administrator | Full system access |
| **Company Admin** | Company-level administrator | Full company access |
| **HR Manager** | Human resources manager | Recruitment + users management |
| **Recruiter** | Handles job postings and candidates | Jobs + candidates |
| **Interviewer** | Conducts interviews, adds evaluations | Interview access only |
| **Accountant** | Billing and financial management | Billing + reports |

### 2.3 Operating Environment
- Server: Linux (Ubuntu 22.04+ / NixOS)
- Database: PostgreSQL 15+
- Browser: Modern browsers (Chrome 90+, Firefox 90+, Edge 90+, Safari 14+)
- Network: HTTPS only in production

### 2.4 Design Constraints
- Single FastAPI application (Modular Monolith — no microservices)
- No separate frontend framework (React, Vue, Angular)
- No Redis, Celery, RabbitMQ, Kafka
- Background tasks via FastAPI `BackgroundTasks` only
- All UI via Jinja2 + HTMX + Alpine.js + TailwindCSS

---

## 3. Functional Requirements

### 3.1 Authentication (Module: accounts)

| ID | Requirement |
|----|-------------|
| AUTH-001 | User login with email + password |
| AUTH-002 | JWT access token issued on login (15 min expiry) |
| AUTH-003 | JWT refresh token issued on login (7 days expiry) |
| AUTH-004 | Logout invalidates refresh token |
| AUTH-005 | Password change requires current password |
| AUTH-006 | Forgot password sends reset link via email |
| AUTH-007 | Password reset via secure token |
| AUTH-008 | Account lockout after 5 failed attempts |
| AUTH-009 | Session management with audit logging |

### 3.2 User Management (Module: users)

| ID | Requirement |
|----|-------------|
| USR-001 | Create, read, update, deactivate users |
| USR-002 | RBAC with 6 predefined roles |
| USR-003 | Role assignment per company |
| USR-004 | User profile with avatar |
| USR-005 | Permission checks on all actions |
| USR-006 | Super Admin can manage all companies |

### 3.3 Company Management (Module: companies)

| ID | Requirement |
|----|-------------|
| CMP-001 | Create and manage companies |
| CMP-002 | Company logo upload |
| CMP-003 | Branch management |
| CMP-004 | Company settings (timezone, language, etc.) |
| CMP-005 | Multi-tenant data isolation |

### 3.4 Job Management (Module: jobs)

| ID | Requirement |
|----|-------------|
| JOB-001 | Create job postings with rich description |
| JOB-002 | Define required skills, experience, salary range |
| JOB-003 | Job status: Draft, Active, Paused, Closed |
| JOB-004 | Job categories and departments |
| JOB-005 | Job expiry date |
| JOB-006 | Clone existing job postings |

### 3.5 Candidate Management (Module: candidates)

| ID | Requirement |
|----|-------------|
| CND-001 | Create and manage candidate profiles |
| CND-002 | Candidate skills, experience, education, languages |
| CND-003 | Notes and tags on candidates |
| CND-004 | Candidate search with filters |
| CND-005 | Candidate status (Active, Blacklisted, Hired) |
| CND-006 | Duplicate detection |

### 3.6 Resume Parser (Module: resume_parser)

| ID | Requirement |
|----|-------------|
| RSM-001 | Upload PDF, DOCX, or image files |
| RSM-002 | Extract: name, phone, email, skills |
| RSM-003 | Extract: work experience (company, role, dates) |
| RSM-004 | Extract: education (degree, institution, dates) |
| RSM-005 | Extract: languages with proficiency level |
| RSM-006 | Auto-populate candidate profile from parsed data |
| RSM-007 | Parsing confidence score per field |

### 3.7 AI Matching (Module: ai_matching)

| ID | Requirement |
|----|-------------|
| AI-001 | Compare candidate CV to job description |
| AI-002 | Match score (0–100%) |
| AI-003 | Candidate ranking for a job |
| AI-004 | Missing skills identification |
| AI-005 | Strengths and weaknesses analysis |
| AI-006 | Pluggable AI provider (Adapter Pattern) |
| AI-007 | Support OpenAI, Anthropic, local LLM |

### 3.8 ATS Pipeline (Module: ats)

| ID | Requirement |
|----|-------------|
| ATS-001 | Kanban-style pipeline view |
| ATS-002 | Stages: Applied → Screening → Shortlisted → Interview → Technical → HR Interview → Offer → Hired / Rejected |
| ATS-003 | Move candidates between stages |
| ATS-004 | Stage-specific actions and notes |
| ATS-005 | Pipeline history and audit trail |
| ATS-006 | Bulk actions on candidates |

### 3.9 Interviews (Module: interviews)

| ID | Requirement |
|----|-------------|
| INT-001 | Schedule interviews with date, time, location/link |
| INT-002 | Assign interviewers |
| INT-003 | Interview types: Phone, Video, In-Person, Technical |
| INT-004 | Interview evaluation form |
| INT-005 | Score and recommendation (Hire/No Hire/Consider) |
| INT-006 | Email notifications for scheduled interviews |

### 3.10 Notifications (Module: notifications)

| ID | Requirement |
|----|-------------|
| NTF-001 | Email notifications via SMTP |
| NTF-002 | WhatsApp notifications via API |
| NTF-003 | In-app notifications (bell icon) |
| NTF-004 | Background processing via FastAPI BackgroundTasks |
| NTF-005 | Notification templates (per event type) |
| NTF-006 | User notification preferences |

### 3.11 CRM (Module: crm)

| ID | Requirement |
|----|-------------|
| CRM-001 | Client company management |
| CRM-002 | Contact persons per client |
| CRM-003 | Contract management with status |
| CRM-004 | Client notes and activity timeline |

### 3.12 Billing (Module: billing)

| ID | Requirement |
|----|-------------|
| BIL-001 | Subscription plans management |
| BIL-002 | Invoice generation |
| BIL-003 | Payment recording |
| BIL-004 | Billing history per company |
| BIL-005 | PDF invoice export |

### 3.13 Dashboard (Module: dashboard)

| ID | Requirement |
|----|-------------|
| DSH-001 | Real-time statistics overview |
| DSH-002 | Active jobs count |
| DSH-003 | New candidates (daily/weekly) |
| DSH-004 | Pipeline statistics per job |
| DSH-005 | Recent activities feed |
| DSH-006 | Charts: hiring funnel, time-to-hire |

### 3.14 Reports (Module: reports)

| ID | Requirement |
|----|-------------|
| RPT-001 | Configurable report builder |
| RPT-002 | Filters: date range, job, department, recruiter |
| RPT-003 | Sortable columns |
| RPT-004 | Export to PDF |
| RPT-005 | Export to Excel (.xlsx) |
| RPT-006 | Hiring pipeline report |
| RPT-007 | Time-to-hire report |
| RPT-008 | Source effectiveness report |

### 3.15 File Storage (Module: files)

| ID | Requirement |
|----|-------------|
| FIL-001 | Upload PDF, DOCX, images |
| FIL-002 | Storage Adapter Pattern (Local / S3 / Supabase) |
| FIL-003 | File metadata in database |
| FIL-004 | Secure file access (signed URLs or auth check) |
| FIL-005 | File type and size validation |

### 3.16 Audit Logs (Module: audit)

| ID | Requirement |
|----|-------------|
| AUD-001 | Log all create/update/delete operations |
| AUD-002 | Log user login/logout/failures |
| AUD-003 | Log IP address and user agent |
| AUD-004 | Audit log viewer with filters |
| AUD-005 | Retention policy configuration |

### 3.17 Settings (Module: settings)

| ID | Requirement |
|----|-------------|
| SET-001 | Company-wide settings |
| SET-002 | Email SMTP configuration |
| SET-003 | AI provider configuration |
| SET-004 | Notification preferences |
| SET-005 | ATS pipeline customization |

---

## 4. Non-Functional Requirements

### 4.1 Performance
- Page load time: < 2 seconds (95th percentile)
- API response time: < 500ms (95th percentile)
- Support 100 concurrent users per company

### 4.2 Security
- OWASP Top 10 compliance
- All passwords hashed with bcrypt (12+ rounds)
- JWT tokens with short expiry
- SQL injection prevention (parameterized queries via SQLAlchemy)
- XSS prevention (Jinja2 auto-escaping)
- CSRF protection (for state-changing forms)
- Rate limiting on auth endpoints (5 req/min)
- Secure HTTP headers (X-Frame-Options, CSP, HSTS, etc.)
- UUID primary keys (non-enumerable)
- Soft delete for all critical data
- Input validation on all endpoints (Pydantic)

### 4.3 Reliability
- Application uptime: 99.9%
- Database backups: daily
- Graceful error handling (no stack traces in production)

### 4.4 Maintainability
- Clean code with type hints throughout
- Module structure with clear separation of concerns
- Comprehensive unit test coverage (>80%)
- OpenAPI documentation (auto-generated by FastAPI)
- Inline code documentation

### 4.5 Scalability
- Adapter Pattern for AI providers
- Adapter Pattern for file storage
- Horizontal scaling ready (stateless JWT auth)

---

## 5. System Constraints

- No Docker in the Replit environment (Docker is documented for local development)
- No Redis/Celery — background tasks via FastAPI BackgroundTasks
- Replit PostgreSQL used for development; production PostgreSQL via DATABASE_URL
- AI API keys required for AI matching features

---

## 6. Use Cases

### UC-001: Recruiter Posts a Job
**Actor:** Recruiter  
**Precondition:** User is authenticated with Recruiter role  
**Flow:**
1. Recruiter navigates to Jobs → New Job
2. Fills in job title, description, requirements, skills, salary
3. Sets expiry date and status (Draft/Active)
4. Submits the form
5. System validates and saves the job
6. Recruiter is redirected to the job detail page

### UC-002: Candidate is Matched to a Job (AI)
**Actor:** Recruiter  
**Precondition:** Candidate profile exists with uploaded CV; Job posting is active  
**Flow:**
1. Recruiter opens a job and clicks "Find Matching Candidates"
2. System calls AI provider with CV text + job description
3. AI returns match score, missing skills, strengths, weaknesses
4. System displays ranked list of candidates
5. Recruiter selects candidates to add to the pipeline

### UC-003: Resume Upload and Auto-Parse
**Actor:** Recruiter  
**Flow:**
1. Recruiter uploads a PDF/DOCX resume
2. System extracts text from document
3. AI/parser extracts structured data
4. System pre-fills candidate form with extracted data
5. Recruiter reviews and confirms

### UC-004: Interview Scheduling
**Actor:** HR Manager  
**Flow:**
1. HR selects a shortlisted candidate
2. Clicks "Schedule Interview"
3. Selects date, time, type, and interviewer(s)
4. System creates interview record
5. System sends email notification to candidate and interviewers
