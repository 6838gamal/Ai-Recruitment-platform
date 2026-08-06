# Security Design
# AI Recruitment Platform

**Version:** 1.0.0  
**Date:** 2026-08-06  
**Standard:** OWASP Top 10 (2021)

---

## 1. Authentication

### 1.1 Password Policy
- Minimum 8 characters
- At least 1 uppercase, 1 lowercase, 1 digit, 1 special character
- Hashed with **bcrypt** (12 rounds) via `passlib`
- Never stored or logged in plaintext

### 1.2 JWT Strategy
```
Access Token:  15 minutes expiry — stored in httpOnly cookie or memory
Refresh Token: 7 days expiry   — stored in httpOnly cookie, hashed in DB

Token payload:
{
  "sub": "<user_uuid>",
  "company_id": "<company_uuid>",
  "role": "recruiter",
  "exp": <unix_timestamp>
}
```

### 1.3 Refresh Token Rotation
- On every refresh: old token is revoked, new token issued
- Token hash (SHA-256) stored in `refresh_tokens` table
- Refresh token reuse = all user sessions invalidated (token theft detection)

### 1.4 Account Lockout
- 5 consecutive failed login attempts → account locked for 15 minutes
- `failed_attempts` and `locked_until` tracked in `users` table
- Lockout status checked before password verification

### 1.5 Password Reset
- Reset token is a cryptographically random 32-byte string
- Stored as SHA-256 hash in `password_reset_tokens` table
- Expires in 1 hour
- One-time use (`is_used = TRUE` after use)

---

## 2. Authorization (RBAC)

### 2.1 Role Hierarchy

```
Super Admin
    └── Company Admin
            └── HR Manager
                    ├── Recruiter
                    │       └── (Interviewer)
                    └── Accountant
```

### 2.2 Permission Matrix

| Permission | Super Admin | Company Admin | HR | Recruiter | Interviewer | Accountant |
|-----------|-------------|---------------|-----|-----------|-------------|------------|
| Manage companies | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Manage users | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Manage jobs | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Manage candidates | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| View candidates | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Conduct interviews | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Manage billing | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ |
| View reports | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ |
| Manage settings | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| View audit logs | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |

### 2.3 Implementation
```python
# Dependency injection pattern
@router.get("/jobs")
async def list_jobs(
    current_user: UserProfile = Depends(require_role(["company_admin", "hr", "recruiter"]))
):
    ...
```

---

## 3. OWASP Top 10 Mitigations

### A01 – Broken Access Control
- ✅ Every route has explicit role/permission check
- ✅ `company_id` filter on every multi-tenant query
- ✅ UUID primary keys (non-enumerable)
- ✅ Soft delete prevents accidental data exposure

### A02 – Cryptographic Failures
- ✅ bcrypt with 12 rounds for passwords
- ✅ SHA-256 for token hashing
- ✅ HTTPS enforced in production (HSTS header)
- ✅ Sensitive config via environment variables only

### A03 – Injection
- ✅ SQLAlchemy ORM parameterized queries (no raw SQL with user input)
- ✅ Pydantic v2 validates all input before it reaches the service layer
- ✅ Jinja2 auto-escaping enabled (XSS prevention)

### A04 – Insecure Design
- ✅ Threat modeling documented
- ✅ Principle of least privilege (RBAC)
- ✅ Defense in depth (middleware + service + db level checks)

### A05 – Security Misconfiguration
- ✅ `DEBUG=False` in production (via settings)
- ✅ Secure HTTP headers middleware
- ✅ No default credentials
- ✅ Error responses never include stack traces in production

### A06 – Vulnerable Components
- ✅ Dependencies pinned in `pyproject.toml`
- ✅ Regular `uv audit` / `pip audit` in CI/CD

### A07 – Authentication Failures
- ✅ Account lockout (5 attempts)
- ✅ Short-lived JWT access tokens (15 min)
- ✅ Refresh token rotation + theft detection
- ✅ Rate limiting on `/auth/login` (5 req/min per IP)

### A08 – Software and Data Integrity Failures
- ✅ File type validation (MIME type + magic bytes)
- ✅ File size limits enforced
- ✅ Input sanitization via Pydantic

### A09 – Security Logging and Monitoring
- ✅ Audit log for all auth events (login, logout, failure, lockout)
- ✅ Audit log for all data changes
- ✅ IP address and User-Agent logged

### A10 – Server-Side Request Forgery (SSRF)
- ✅ External HTTP calls only to pre-approved domains (AI providers, email)
- ✅ No user-controlled URLs fetched by server

---

## 4. HTTP Security Headers

```python
# Applied via SecurityHeadersMiddleware
{
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' cdn.tailwindcss.com unpkg.com; "
        "style-src 'self' 'unsafe-inline' cdn.tailwindcss.com; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:;"
    ),
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
}
```

---

## 5. Rate Limiting

```python
# Using slowapi (Starlette-compatible Limiter)
# Applied per IP address by default

POST /auth/login          → 5  requests/minute
POST /auth/forgot-password → 3 requests/minute
POST /auth/reset-password  → 3 requests/minute
GET  /api/*               → 100 requests/minute
POST /api/*               → 30  requests/minute
```

---

## 6. CSRF Protection

HTMX-based forms use SameSite=Strict cookies for session tokens. For additional protection on state-changing operations, CSRF tokens are embedded in forms via Jinja2:

```html
<input type="hidden" name="csrf_token" value="{{ csrf_token }}">
```

Validated server-side using `itsdangerous.URLSafeTimedSerializer`.

---

## 7. File Upload Security

```python
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "image/jpeg",
    "image/png",
    "image/webp",
}
MAX_FILE_SIZE_MB = 10

# Validation:
# 1. Content-Type header check (client-provided, untrusted)
# 2. python-magic byte signature check (server-side, trusted)
# 3. File size check before reading
# 4. Random UUID filename (never use original filename on disk)
```

---

## 8. Environment Variables and Secrets

```env
# Never hardcode — always use environment variables
SECRET_KEY=<64-byte-random-hex>
DATABASE_URL=postgresql://...
AI_API_KEY=sk-...
SMTP_PASSWORD=...
```

Secrets are never:
- Logged
- Returned in API responses
- Committed to version control

---

## 9. Input Validation Strategy

All input is validated at three layers:

1. **Pydantic schemas**: type coercion, field constraints, custom validators
2. **Service layer**: business rule validation
3. **Database layer**: SQL constraints, CHECK constraints, UNIQUE constraints

```python
class CreateJobSchema(BaseSchema):
    title: str = Field(min_length=3, max_length=255)
    salary_min: Optional[Decimal] = Field(None, ge=0)
    salary_max: Optional[Decimal] = Field(None, ge=0)

    @model_validator(mode='after')
    def validate_salary_range(self) -> 'CreateJobSchema':
        if self.salary_min and self.salary_max:
            if self.salary_min > self.salary_max:
                raise ValueError("salary_min cannot exceed salary_max")
        return self
```
