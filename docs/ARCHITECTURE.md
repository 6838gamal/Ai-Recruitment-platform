# System Architecture
# AI Recruitment Platform

**Version:** 1.0.0  
**Date:** 2026-08-06

---

## 1. Architectural Style: Modular Monolith

The AI Recruitment Platform uses a **Modular Monolith** architecture:

- **One deployable unit** — a single FastAPI application process
- **Internal module boundaries** — each business domain is a self-contained module
- **No inter-process communication** — modules call each other's services directly
- **Shared database** — all modules share one PostgreSQL database with clear schema ownership

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Recruitment Platform                   │
│                     (Single Process)                         │
│                                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ accounts │ │  users   │ │companies │ │   jobs   │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │candidates│ │  resume  │ │   ats    │ │interviews│       │
│  └──────────┘ │  parser  │ └──────────┘ └──────────┘       │
│               └──────────┘                                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ai_match  │ │  notif.  │ │   crm    │ │ billing  │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │dashboard │ │ reports  │ │  files   │ │  audit   │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│  ┌──────────┐                                                │
│  │ settings │                                                │
│  └──────────┘                                                │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                  Core Infrastructure                 │    │
│  │  Security │ RBAC │ Base Models │ Database │ Config  │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
            │
            │ SQLAlchemy 2.x
            ▼
    ┌───────────────┐
    │  PostgreSQL   │
    └───────────────┘
```

---

## 2. Request Lifecycle

```
Browser / HTMX Request
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│                      FastAPI App                         │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │              Middleware Stack                    │    │
│  │  1. SecurityHeadersMiddleware                   │    │
│  │  2. RateLimitMiddleware (slowapi)                │    │
│  │  3. AuditMiddleware (log requests)              │    │
│  │  4. SessionMiddleware (Starlette)               │    │
│  └────────────────────┬────────────────────────────┘    │
│                       ▼                                  │
│  ┌─────────────────────────────────────────────────┐    │
│  │              Router (routes.py)                  │    │
│  │  /auth/...   /users/...   /jobs/...   etc.      │    │
│  └────────────────────┬────────────────────────────┘    │
│                       ▼                                  │
│  ┌─────────────────────────────────────────────────┐    │
│  │           Dependencies (dependencies.py)         │    │
│  │  get_db_session │ get_current_user │ check_perm  │    │
│  └────────────────────┬────────────────────────────┘    │
│                       ▼                                  │
│  ┌─────────────────────────────────────────────────┐    │
│  │              Service Layer                       │    │
│  │  Business logic, validation, orchestration      │    │
│  └────────────────────┬────────────────────────────┘    │
│                       ▼                                  │
│  ┌─────────────────────────────────────────────────┐    │
│  │            Repository Layer                      │    │
│  │  Database queries via SQLAlchemy ORM            │    │
│  └────────────────────┬────────────────────────────┘    │
│                       ▼                                  │
│  ┌─────────────────────────────────────────────────┐    │
│  │         Response (HTML or JSON)                  │    │
│  │  Jinja2 template (HTML) or Pydantic schema (JSON)│    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Module Structure

Every module follows the same internal structure:

```
app/modules/<module_name>/
├── __init__.py          # Module initialization, exports router
├── models.py            # SQLAlchemy ORM models
├── schemas.py           # Pydantic v2 schemas (request/response)
├── repositories.py      # Database access layer (CRUD)
├── services.py          # Business logic
├── routes.py            # FastAPI router (HTML + API endpoints)
├── validators.py        # Custom validation logic
├── permissions.py       # Module-specific permission checks
├── templates/           # Jinja2 templates for this module
│   ├── list.html
│   ├── detail.html
│   ├── create.html
│   └── edit.html
└── tests/
    ├── __init__.py
    └── test_<module>.py
```

---

## 4. Layer Responsibilities

### 4.1 Routes Layer (`routes.py`)
- Define URL patterns and HTTP methods
- Call dependencies (auth, permissions, db session)
- Delegate to service layer
- Return HTML template response or JSON response
- Handle HTMX partial renders vs. full-page renders

### 4.2 Service Layer (`services.py`)
- Business logic and orchestration
- Calls repositories for data access
- Calls other module services as needed
- Raises domain-specific exceptions
- Triggers background tasks

### 4.3 Repository Layer (`repositories.py`)
- All database queries
- Uses SQLAlchemy ORM
- No business logic
- Returns SQLAlchemy model instances
- Implements pagination, filtering, sorting

### 4.4 Model Layer (`models.py`)
- SQLAlchemy 2.x mapped class definitions
- All models inherit from `Base` (SQLAlchemy) and `TimestampMixin`
- UUID primary keys
- Soft delete via `deleted_at` field
- Clear foreign key relationships

### 4.5 Schema Layer (`schemas.py`)
- Pydantic v2 models for request/response
- Input validation
- Separate schemas: `Create`, `Update`, `Response`, `List`
- No ORM objects exposed directly to routes

---

## 5. Core Infrastructure

### 5.1 Configuration (`app/config.py`)
- Pydantic Settings with environment variable loading
- `.env` file support
- Secrets never hardcoded

### 5.2 Database (`app/database.py`)
- SQLAlchemy engine configuration
- Session factory
- `get_db()` dependency for FastAPI

### 5.3 Security (`app/core/security.py`)
- JWT token creation and verification
- Password hashing (bcrypt via passlib)
- Token blacklist for logout

### 5.4 RBAC (`app/core/permissions.py`)
- Role hierarchy definition
- Permission decorators for routes
- `require_role()`, `require_permission()` helpers

### 5.5 Base Models (`app/core/base/`)
- `BaseModel`: UUID PK, timestamps, soft delete
- `BaseRepository`: generic CRUD methods
- `BaseService`: service scaffolding
- `BaseSchema`: Pydantic base configuration

---

## 6. Adapter Patterns

### 6.1 AI Provider Adapter

```
AIProviderInterface (Abstract)
    │
    ├── OpenAIAdapter
    ├── AnthropicAdapter
    └── LocalLLMAdapter (Ollama)
```

Configure via `AI_PROVIDER` environment variable.

### 6.2 File Storage Adapter

```
StorageInterface (Abstract)
    │
    ├── LocalStorageAdapter  (default, stores in ./uploads/)
    ├── S3StorageAdapter     (Amazon S3)
    └── SupabaseStorageAdapter
```

Configure via `STORAGE_BACKEND` environment variable.

### 6.3 Notification Adapter

```
NotificationInterface (Abstract)
    │
    ├── EmailAdapter    (SMTP via smtplib/aiosmtplib)
    ├── WhatsAppAdapter (Meta Business API)
    └── InAppAdapter    (database-stored notifications)
```

---

## 7. Frontend Architecture

The frontend is **server-rendered** with progressive enhancement:

```
Jinja2 (base template, layout, full pages)
    +
HTMX (partial page updates, form submissions, lazy loading)
    +
Alpine.js (client-side state, dropdowns, modals, toggles)
    +
TailwindCSS (utility-first styling)
```

### Template Hierarchy
```
base.html
├── auth/
│   ├── login.html
│   └── forgot_password.html
├── dashboard/
│   └── index.html
├── users/
│   ├── list.html
│   └── detail.html
├── jobs/
│   ├── list.html
│   └── kanban.html
└── partials/  (HTMX targets)
    ├── navbar.html
    ├── sidebar.html
    ├── table.html
    └── pagination.html
```

---

## 8. Deployment Architecture

```
Internet
    │
    ▼ HTTPS (443)
┌──────────────┐
│  Reverse     │  (Nginx / Caddy)
│  Proxy       │
└──────┬───────┘
       │ HTTP (5000)
       ▼
┌──────────────┐
│  FastAPI App │  (uvicorn, multiple workers)
│  Port 5000   │
└──────┬───────┘
       │ SQLAlchemy
       ▼
┌──────────────┐
│  PostgreSQL  │
│  Port 5432   │
└──────────────┘
```

---

## 9. Module Dependencies

```
accounts ──────────────────────► (no deps)
users   ──────────────────────► accounts
companies ────────────────────► users
jobs    ──────────────────────► companies, users
candidates ───────────────────► companies
resume_parser ────────────────► candidates, files
ai_matching ──────────────────► candidates, jobs
ats     ──────────────────────► candidates, jobs
interviews ───────────────────► ats, users
notifications ────────────────► users (async, low coupling)
crm     ──────────────────────► companies, users
billing ──────────────────────► companies
reports ──────────────────────► all modules (read-only)
dashboard ────────────────────► all modules (read-only)
files   ──────────────────────► (no deps)
audit   ──────────────────────► (no deps, logs everything)
settings ─────────────────────► companies
```
