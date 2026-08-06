# API Design
# AI Recruitment Platform

**Version:** 1.0.0  
**Date:** 2026-08-06

---

## 1. Design Philosophy

The platform exposes **two types of endpoints** per module:

1. **HTML Endpoints** — return full Jinja2-rendered pages (for direct browser navigation)
2. **HTMX Partial Endpoints** — return HTML fragments for seamless partial page updates
3. **JSON API Endpoints** — return JSON for programmatic access (prefix: `/api/v1/`)

### URL Pattern
```
GET  /jobs/              → Full HTML page (job list)
GET  /jobs/htmx/table   → HTMX partial (just the table rows)
GET  /api/v1/jobs/       → JSON API response
```

---

## 2. Authentication Endpoints

### Module: `/auth`

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/auth/login` | Login page | Public |
| POST | `/auth/login` | Authenticate, issue JWT | Public |
| POST | `/auth/logout` | Revoke refresh token | Auth |
| POST | `/auth/refresh` | Refresh access token | Cookie |
| GET | `/auth/forgot-password` | Forgot password page | Public |
| POST | `/auth/forgot-password` | Send reset email | Public |
| GET | `/auth/reset-password` | Reset password page | Token |
| POST | `/auth/reset-password` | Set new password | Token |
| POST | `/auth/change-password` | Change current password | Auth |

---

## 3. User Endpoints

### Module: `/users`

| Method | Path | Description | Roles |
|--------|------|-------------|-------|
| GET | `/users/` | User list page | Admin, HR |
| GET | `/users/create` | Create user form | Admin |
| POST | `/users/` | Create user | Admin |
| GET | `/users/{id}` | User detail page | Admin, HR |
| GET | `/users/{id}/edit` | Edit user form | Admin |
| PUT | `/users/{id}` | Update user | Admin |
| DELETE | `/users/{id}` | Deactivate user | Admin |
| GET | `/users/profile` | Current user profile | Auth |
| PUT | `/users/profile` | Update profile | Auth |

### API
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/users/` | List users (JSON) |
| POST | `/api/v1/users/` | Create user (JSON) |
| GET | `/api/v1/users/{id}` | Get user (JSON) |
| PUT | `/api/v1/users/{id}` | Update user (JSON) |

---

## 4. Company Endpoints

### Module: `/companies`

| Method | Path | Description | Roles |
|--------|------|-------------|-------|
| GET | `/companies/` | Company list | Super Admin |
| GET | `/companies/create` | Create form | Super Admin |
| POST | `/companies/` | Create company | Super Admin |
| GET | `/companies/{id}` | Company detail | Admin+ |
| PUT | `/companies/{id}` | Update company | Admin+ |
| DELETE | `/companies/{id}` | Delete company | Super Admin |
| POST | `/companies/{id}/logo` | Upload logo | Admin+ |
| GET | `/companies/{id}/branches` | Branch list | Admin+ |
| POST | `/companies/{id}/branches` | Create branch | Admin+ |

---

## 5. Job Endpoints

### Module: `/jobs`

| Method | Path | Description | Roles |
|--------|------|-------------|-------|
| GET | `/jobs/` | Job list page | Auth |
| GET | `/jobs/create` | Create job form | Admin, HR, Recruiter |
| POST | `/jobs/` | Create job posting | Admin, HR, Recruiter |
| GET | `/jobs/{id}` | Job detail | Auth |
| GET | `/jobs/{id}/edit` | Edit job form | Admin, HR, Recruiter |
| PUT | `/jobs/{id}` | Update job | Admin, HR, Recruiter |
| DELETE | `/jobs/{id}` | Delete job | Admin, HR |
| POST | `/jobs/{id}/clone` | Clone job | Admin, HR, Recruiter |
| POST | `/jobs/{id}/publish` | Publish job | Admin, HR |
| POST | `/jobs/{id}/close` | Close job | Admin, HR |
| GET | `/jobs/{id}/candidates` | Candidates for job | Auth |
| GET | `/jobs/{id}/pipeline` | Kanban pipeline | Auth |

### HTMX
| Method | Path | Description |
|--------|------|-------------|
| GET | `/jobs/htmx/table` | Job table partial |
| GET | `/jobs/{id}/htmx/pipeline` | Pipeline kanban partial |

---

## 6. Candidate Endpoints

### Module: `/candidates`

| Method | Path | Description | Roles |
|--------|------|-------------|-------|
| GET | `/candidates/` | Candidate list | Auth |
| GET | `/candidates/create` | Create candidate form | HR, Recruiter |
| POST | `/candidates/` | Create candidate | HR, Recruiter |
| GET | `/candidates/{id}` | Candidate profile | Auth |
| PUT | `/candidates/{id}` | Update candidate | HR, Recruiter |
| DELETE | `/candidates/{id}` | Soft-delete candidate | HR, Admin |
| POST | `/candidates/{id}/notes` | Add note | Auth |
| DELETE | `/candidates/{id}/notes/{note_id}` | Delete note | Author, Admin |
| POST | `/candidates/{id}/apply/{job_id}` | Add to pipeline | HR, Recruiter |

---

## 7. Resume Parser Endpoints

### Module: `/resume-parser`

| Method | Path | Description | Roles |
|--------|------|-------------|-------|
| POST | `/resume-parser/upload` | Upload + parse resume | HR, Recruiter |
| GET | `/resume-parser/{id}/result` | Get parse result | HR, Recruiter |
| POST | `/resume-parser/{id}/apply` | Create candidate from result | HR, Recruiter |

---

## 8. AI Matching Endpoints

### Module: `/ai-matching`

| Method | Path | Description | Roles |
|--------|------|-------------|-------|
| POST | `/ai-matching/match` | Match single candidate to job | HR, Recruiter |
| POST | `/ai-matching/rank` | Rank all candidates for a job | HR, Recruiter |
| GET | `/ai-matching/results/{job_id}` | Get match results for job | Auth |

---

## 9. ATS Endpoints

### Module: `/ats`

| Method | Path | Description | Roles |
|--------|------|-------------|-------|
| GET | `/ats/{job_id}` | Pipeline kanban page | Auth |
| PUT | `/ats/applications/{id}/stage` | Move to stage | HR, Recruiter |
| PUT | `/ats/applications/{id}/reject` | Reject application | HR, Recruiter |
| GET | `/ats/applications/{id}/history` | Stage history | Auth |
| POST | `/ats/applications/bulk` | Bulk stage update | HR, Admin |

### HTMX
| Method | Path | Description |
|--------|------|-------------|
| GET | `/ats/{job_id}/htmx/board` | Kanban board partial |
| PUT | `/ats/applications/{id}/htmx/move` | Move card (HTMX) |

---

## 10. Interview Endpoints

### Module: `/interviews`

| Method | Path | Description | Roles |
|--------|------|-------------|-------|
| GET | `/interviews/` | Interview list | Auth |
| POST | `/interviews/` | Schedule interview | HR, Recruiter |
| GET | `/interviews/{id}` | Interview detail | Auth |
| PUT | `/interviews/{id}` | Update interview | HR, Recruiter |
| DELETE | `/interviews/{id}` | Cancel interview | HR, Recruiter |
| POST | `/interviews/{id}/evaluate` | Submit evaluation | Interviewer |
| GET | `/interviews/{id}/evaluations` | View evaluations | HR, Admin |

---

## 11. Dashboard Endpoints

### Module: `/dashboard`

| Method | Path | Description | Roles |
|--------|------|-------------|-------|
| GET | `/dashboard/` | Dashboard home | Auth |
| GET | `/dashboard/htmx/stats` | Stats cards partial | Auth |
| GET | `/dashboard/htmx/activity` | Activity feed partial | Auth |
| GET | `/dashboard/htmx/pipeline-chart` | Pipeline chart partial | Auth |
| GET | `/api/v1/dashboard/stats` | Stats JSON | Auth |

---

## 12. Reports Endpoints

### Module: `/reports`

| Method | Path | Description | Roles |
|--------|------|-------------|-------|
| GET | `/reports/` | Reports home | Admin, HR, Accountant |
| GET | `/reports/hiring-pipeline` | Hiring pipeline report | Admin, HR |
| GET | `/reports/time-to-hire` | Time-to-hire report | Admin, HR |
| GET | `/reports/source-effectiveness` | Source report | Admin, HR |
| GET | `/reports/export/pdf` | Export report as PDF | Admin, HR |
| GET | `/reports/export/excel` | Export report as Excel | Admin, HR |

---

## 13. Notifications Endpoints

### Module: `/notifications`

| Method | Path | Description | Roles |
|--------|------|-------------|-------|
| GET | `/notifications/` | Notification list | Auth |
| PUT | `/notifications/{id}/read` | Mark as read | Auth |
| PUT | `/notifications/read-all` | Mark all as read | Auth |
| GET | `/notifications/htmx/bell` | Notification bell partial | Auth |
| GET | `/api/v1/notifications/unread-count` | Unread count JSON | Auth |

---

## 14. Files Endpoints

### Module: `/files`

| Method | Path | Description | Roles |
|--------|------|-------------|-------|
| POST | `/files/upload` | Upload file | Auth |
| GET | `/files/{id}` | Download / view file | Auth |
| DELETE | `/files/{id}` | Delete file | Auth + Owner |

---

## 15. Settings Endpoints

### Module: `/settings`

| Method | Path | Description | Roles |
|--------|------|-------------|-------|
| GET | `/settings/` | Settings page | Admin |
| PUT | `/settings/general` | Update general settings | Admin |
| PUT | `/settings/email` | Update email settings | Admin |
| PUT | `/settings/ai` | Update AI settings | Admin |
| PUT | `/settings/storage` | Update storage settings | Admin |
| POST | `/settings/email/test` | Test email config | Admin |

---

## 16. Standard Request/Response Format

### Success Response (JSON)
```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "page": 1,
    "per_page": 25,
    "total": 150,
    "total_pages": 6
  }
}
```

### Error Response (JSON)
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      { "field": "email", "message": "Invalid email format" }
    ]
  }
}
```

### Pagination Query Parameters
```
?page=1&per_page=25&sort=created_at&order=desc&search=keyword
```

---

## 17. HTMX Conventions

HTMX requests include the `HX-Request: true` header. Routes detect this and return partial HTML instead of full pages:

```python
@router.get("/jobs/")
async def job_list(request: Request):
    jobs = await job_service.list_jobs(...)
    template = "jobs/partials/table.html" if request.headers.get("HX-Request") else "jobs/list.html"
    return templates.TemplateResponse(template, {"request": request, "jobs": jobs})
```
