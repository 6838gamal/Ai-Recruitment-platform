# AI Recruitment Platform

An AI-powered recruitment and HR management platform — FastAPI modular monolith with 17 internal modules.

## How to run

The app is configured as a workflow: **Start application** → `python run.py`

It starts on port 5000. The Replit preview pane shows the running app.

## Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12 / FastAPI |
| Database | PostgreSQL (SQLAlchemy 2.x + Alembic migrations) |
| Frontend | Jinja2 templates + HTMX + Alpine.js + Tailwind CSS CDN |
| Auth | JWT (cookies) via python-jose + passlib |
| AI | OpenAI / Anthropic adapter (configurable via `AI_PROVIDER` env var) |
| File storage | Local disk (S3/Supabase adapters stubbed) |

## Architecture

Modular monolith — one FastAPI process with 17 independent modules under `app/modules/`:

`accounts` · `users` · `companies` · `jobs` · `candidates` · `resume_parser` · `ai_matching` · `ats` · `interviews` · `notifications` · `crm` · `billing` · `reports` · `dashboard` · `files` · `audit` · `settings`

Each module owns: `models.py`, `schemas.py`, `repositories.py`, `services.py`, `routes.py`, templates, and tests.

## Database migrations

```bash
# Create a new migration after changing models
alembic revision --autogenerate -m "description"

# Apply all pending migrations
alembic upgrade head

# Roll back one migration
alembic downgrade -1
```

## Module completion status

| Module | Status |
|---|---|
| accounts | ✅ Complete — login, logout, password reset, JWT |
| users | 🔨 Partial — list + profile routes, service layer |
| dashboard | 🔨 Partial — stats aggregation |
| companies | 🏗️ Scaffold |
| jobs | 🏗️ Scaffold |
| candidates | 🏗️ Scaffold |
| resume_parser | 🏗️ Scaffold — basic PDF/DOCX text extraction |
| ai_matching | 🏗️ Scaffold — adapter factory, NotImplemented |
| ats | 🏗️ Scaffold |
| interviews | 🏗️ Scaffold |
| notifications | 🏗️ Scaffold |
| crm | 🏗️ Scaffold |
| billing | 🏗️ Scaffold |
| reports | 🏗️ Scaffold |
| files | 🏗️ Partial — local storage working, S3 stubbed |
| audit | 🏗️ Partial — logging middleware wired |
| settings | 🏗️ Scaffold |

## Key configuration (environment variables)

All configured via Replit Secrets / env vars. See `.env.example` for the full list.

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | PostgreSQL connection (auto-provided by Replit) |
| `SECRET_KEY` | JWT signing key |
| `AI_PROVIDER` | `openai` \| `anthropic` \| `local` |
| `AI_API_KEY` | API key for the chosen AI provider |
| `SMTP_*` | Email settings for password reset |
| `STORAGE_BACKEND` | `local` \| `s3` \| `supabase` |

## Documentation

Full design docs are in `docs/`:
- `ARCHITECTURE.md` — module structure, patterns, dependency graph
- `DATABASE_DESIGN.md` — schema, indexes, naming conventions
- `DEVELOPMENT_ROADMAP.md` — per-module implementation checklist
- `API_DESIGN.md` — API conventions
- `SECURITY_DESIGN.md` — auth, RBAC, rate limiting

## User preferences

- Keep existing modular structure; do not restructure without asking
- Follow patterns established in the `accounts` module as the reference implementation
- Use Alembic for all schema changes; never auto-create tables at startup
- Template calls must use Starlette 0.41+ API: `TemplateResponse(request, "template.html", context_dict)` — request is the first arg, NOT inside the context dict
