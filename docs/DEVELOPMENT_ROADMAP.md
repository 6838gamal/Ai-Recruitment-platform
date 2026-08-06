# Development Roadmap
# AI Recruitment Platform

**Version:** 1.0.0  
**Date:** 2026-08-06

---

## Overview

The platform is built **Module by Module**. Each module must be fully complete (models, migrations, schemas, repositories, services, routes, templates, tests) before moving to the next.

---

## Phase 0: Foundation ✅

**Status:** Complete

- [x] Project documentation (SRS, Architecture, DB Design, ER Diagram, API Design, Security, Roadmap)
- [x] Project structure created
- [x] Core infrastructure (config, database, base classes, security, middleware)
- [x] Folder structure established

---

## Phase 1: Core Modules

### Module 1: accounts (Authentication) ✅
- [x] `users` model + Alembic migration
- [x] `refresh_tokens` + `password_reset_tokens` models
- [x] Pydantic schemas (Login, Register, PasswordChange, PasswordReset)
- [x] Repository: user CRUD, token management
- [x] Service: login, logout, forgot password, reset password
- [x] Routes: login page, logout, forgot password, reset password
- [x] Templates: login.html, forgot_password.html, reset_password.html
- [x] Unit tests

### Module 2: companies
- [ ] `companies` + `branches` models + migration
- [ ] Schemas, repository, service, routes
- [ ] Templates: company list, create, edit, detail, branches
- [ ] Logo upload integration
- [ ] Unit tests

### Module 3: users (User Profiles & RBAC)
- [ ] `user_profiles` model + migration
- [ ] RBAC permission matrix implementation
- [ ] Schemas, repository, service, routes
- [ ] Templates: user list, create, edit, profile
- [ ] Avatar upload
- [ ] Unit tests

---

## Phase 2: Recruitment Core

### Module 4: jobs
- [ ] `job_postings`, `skills`, `job_skills`, `departments` models + migration
- [ ] Schemas, repository, service, routes
- [ ] Templates: job list, create, edit, detail, skills selector
- [ ] Clone job feature
- [ ] Unit tests

### Module 5: candidates
- [ ] `candidates`, `candidate_experiences`, `candidate_education`, `candidate_languages`, `candidate_skills`, `candidate_notes` models + migration
- [ ] Schemas, repository, service, routes
- [ ] Templates: candidate list, profile, create, edit, notes
- [ ] Duplicate detection
- [ ] Unit tests

### Module 6: files
- [ ] `file_uploads` model + migration
- [ ] Storage Adapter (Local, S3, Supabase)
- [ ] File upload/download routes
- [ ] File type validation (magic bytes)
- [ ] Unit tests

### Module 7: resume_parser
- [ ] PDF/DOCX/image text extraction
- [ ] AI-powered structured data extraction
- [ ] Auto-populate candidate profile
- [ ] Upload form + result review template
- [ ] Unit tests

---

## Phase 3: AI & ATS

### Module 8: ai_matching
- [ ] `match_results` model + migration
- [ ] AI Provider Adapter (OpenAI, Anthropic, Local)
- [ ] Match single candidate to job
- [ ] Rank all candidates for a job
- [ ] Results display template
- [ ] Unit tests

### Module 9: ats
- [ ] `applications`, `application_stage_history` models + migration
- [ ] Kanban pipeline view (HTMX drag-and-drop)
- [ ] Stage transition logic + validation
- [ ] Pipeline history template
- [ ] Bulk operations
- [ ] Unit tests

### Module 10: interviews
- [ ] `interviews`, `interview_interviewers`, `interview_evaluations` models + migration
- [ ] Schedule interview flow
- [ ] Evaluation form
- [ ] Calendar view
- [ ] Email notifications integration
- [ ] Unit tests

---

## Phase 4: Communication & Intelligence

### Module 11: notifications
- [ ] `notifications` model + migration
- [ ] Email adapter (SMTP)
- [ ] WhatsApp adapter (Meta Business API)
- [ ] In-app notifications (bell icon with HTMX)
- [ ] Background task dispatching
- [ ] Notification templates per event type
- [ ] Unit tests

### Module 12: crm
- [ ] `clients`, `client_contacts`, `contracts` models + migration
- [ ] Client management CRUD
- [ ] Contract management with file attachment
- [ ] Activity timeline
- [ ] Unit tests

---

## Phase 5: Analytics & Administration

### Module 13: dashboard
- [ ] Stats aggregation queries
- [ ] Charts (hiring funnel, time-to-hire) with HTMX + Chart.js
- [ ] Activity feed
- [ ] Role-based dashboard views
- [ ] Real-time updates via HTMX polling

### Module 14: reports
- [ ] Report builder with filters
- [ ] Hiring pipeline report
- [ ] Time-to-hire report
- [ ] Source effectiveness report
- [ ] PDF export (WeasyPrint)
- [ ] Excel export (openpyxl)
- [ ] Unit tests

### Module 15: billing
- [ ] `subscription_plans`, `subscriptions`, `invoices` models + migration
- [ ] Plan management
- [ ] Invoice generation
- [ ] Payment recording
- [ ] PDF invoice export
- [ ] Unit tests

---

## Phase 6: System

### Module 16: audit
- [ ] `audit_logs` model + migration
- [ ] Audit middleware (automatic logging)
- [ ] Audit log viewer with filters
- [ ] Export audit logs
- [ ] Unit tests

### Module 17: settings
- [ ] `company_settings` model + migration
- [ ] SMTP settings + test connection
- [ ] AI provider settings
- [ ] Storage backend settings
- [ ] Unit tests

---

## Phase 7: Production Hardening

- [ ] Full integration test suite
- [ ] Load testing (locust)
- [ ] Security audit (OWASP ZAP / Bandit)
- [ ] Performance optimization (query analysis, N+1 prevention)
- [ ] Production deployment configuration (Nginx, Gunicorn/Uvicorn workers)
- [ ] Monitoring setup (health check endpoint)
- [ ] API documentation review
- [ ] User acceptance testing

---

## Estimated Timeline

| Phase | Modules | Estimated Effort |
|-------|---------|-----------------|
| Phase 0 | Foundation | Complete |
| Phase 1 | accounts, companies, users | 2-3 weeks |
| Phase 2 | jobs, candidates, files, resume_parser | 3-4 weeks |
| Phase 3 | ai_matching, ats, interviews | 3-4 weeks |
| Phase 4 | notifications, crm | 2-3 weeks |
| Phase 5 | dashboard, reports, billing | 3-4 weeks |
| Phase 6 | audit, settings | 1-2 weeks |
| Phase 7 | Hardening | 2-3 weeks |
| **Total** | | **~16-23 weeks** |

---

## Definition of Done (per Module)

A module is considered **complete** when:

1. ✅ All SQLAlchemy models created
2. ✅ Alembic migration generated and tested
3. ✅ All Pydantic schemas defined (Create, Update, Response)
4. ✅ Repository layer with all needed queries
5. ✅ Service layer with complete business logic
6. ✅ All routes implemented (HTML + HTMX + API)
7. ✅ All Jinja2 templates completed and styled
8. ✅ Unit tests written and passing (>80% coverage)
9. ✅ Module documentation updated
10. ✅ Code reviewed and merged
