# AI Recruitment Platform

An AI-powered recruitment and HR management platform built with FastAPI.

## Stack

- **Backend**: Python 3.12 / FastAPI
- **Database**: PostgreSQL (SQLAlchemy + Alembic)
- **Frontend**: Server-rendered Jinja2 + HTMX + Alpine.js + Tailwind CSS
- **AI**: OpenAI / Anthropic (configurable)

## Running

```bash
python run.py
```

The app will be available at `http://localhost:5000`.

## Modules

17 internal modules: accounts, users, companies, jobs, candidates, resume_parser, ai_matching, ats, interviews, notifications, crm, billing, reports, dashboard, files, audit, settings.

## Configuration

Copy `.env.example` to `.env` and fill in your values.
