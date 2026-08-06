# Database Design
# AI Recruitment Platform

**Version:** 1.0.0  
**Date:** 2026-08-06

---

## 1. Design Principles

- **UUID Primary Keys**: All tables use `UUID` as primary key (non-enumerable, globally unique)
- **Soft Delete**: All critical tables have `deleted_at TIMESTAMPTZ` column
- **Audit Timestamps**: All tables have `created_at` and `updated_at` timestamps
- **Multi-tenancy**: `company_id` foreign key on tenant-scoped tables
- **Normalized**: 3NF normalized with strategic denormalization for performance
- **Referential Integrity**: All foreign keys enforced at database level

---

## 2. Naming Conventions

| Convention | Rule |
|-----------|------|
| Table names | `snake_case`, plural (e.g., `job_postings`) |
| Column names | `snake_case` (e.g., `created_at`) |
| Primary keys | `id UUID` |
| Foreign keys | `<table_singular>_id UUID` |
| Boolean columns | prefix `is_` or `has_` |
| Enum columns | `VARCHAR(50)` with check constraint |
| Timestamps | `TIMESTAMPTZ` (with timezone) |

---

## 3. Common Base Columns

Every table includes:

```sql
id          UUID PRIMARY KEY DEFAULT gen_random_uuid()
created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
deleted_at  TIMESTAMPTZ NULL     -- NULL means active (soft delete)
```

---

## 4. Table Definitions

### 4.1 Module: accounts

#### `users` (authentication identities)
```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    is_verified     BOOLEAN NOT NULL DEFAULT FALSE,
    last_login_at   TIMESTAMPTZ NULL,
    failed_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until    TIMESTAMPTZ NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ NULL
);

CREATE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;
```

#### `refresh_tokens`
```sql
CREATE TABLE refresh_tokens (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash  VARCHAR(255) NOT NULL UNIQUE,
    expires_at  TIMESTAMPTZ NOT NULL,
    is_revoked  BOOLEAN NOT NULL DEFAULT FALSE,
    ip_address  VARCHAR(45) NULL,
    user_agent  TEXT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_hash ON refresh_tokens(token_hash);
```

#### `password_reset_tokens`
```sql
CREATE TABLE password_reset_tokens (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash  VARCHAR(255) NOT NULL UNIQUE,
    expires_at  TIMESTAMPTZ NOT NULL,
    is_used     BOOLEAN NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

### 4.2 Module: companies

#### `companies`
```sql
CREATE TABLE companies (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(255) NOT NULL,
    slug        VARCHAR(100) UNIQUE NOT NULL,
    logo_url    TEXT NULL,
    website     VARCHAR(255) NULL,
    industry    VARCHAR(100) NULL,
    size        VARCHAR(50) NULL,      -- '1-10', '11-50', '51-200', etc.
    country     VARCHAR(100) NULL,
    timezone    VARCHAR(100) NOT NULL DEFAULT 'UTC',
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at  TIMESTAMPTZ NULL
);
```

#### `branches`
```sql
CREATE TABLE branches (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id  UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    name        VARCHAR(255) NOT NULL,
    address     TEXT NULL,
    city        VARCHAR(100) NULL,
    country     VARCHAR(100) NULL,
    phone       VARCHAR(50) NULL,
    is_main     BOOLEAN NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at  TIMESTAMPTZ NULL
);
```

---

### 4.3 Module: users

#### `user_profiles`
```sql
CREATE TABLE user_profiles (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    company_id  UUID NOT NULL REFERENCES companies(id),
    branch_id   UUID NULL REFERENCES branches(id),
    role        VARCHAR(50) NOT NULL,  -- enum: super_admin, company_admin, hr, recruiter, interviewer, accountant
    first_name  VARCHAR(100) NOT NULL,
    last_name   VARCHAR(100) NOT NULL,
    phone       VARCHAR(50) NULL,
    avatar_url  TEXT NULL,
    job_title   VARCHAR(100) NULL,
    department  VARCHAR(100) NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at  TIMESTAMPTZ NULL,
    CONSTRAINT chk_role CHECK (role IN ('super_admin','company_admin','hr','recruiter','interviewer','accountant'))
);

CREATE INDEX idx_user_profiles_company ON user_profiles(company_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_user_profiles_role ON user_profiles(role);
```

---

### 4.4 Module: jobs

#### `departments`
```sql
CREATE TABLE departments (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id  UUID NOT NULL REFERENCES companies(id),
    name        VARCHAR(100) NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at  TIMESTAMPTZ NULL
);
```

#### `job_postings`
```sql
CREATE TABLE job_postings (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      UUID NOT NULL REFERENCES companies(id),
    branch_id       UUID NULL REFERENCES branches(id),
    department_id   UUID NULL REFERENCES departments(id),
    created_by_id   UUID NOT NULL REFERENCES user_profiles(id),
    title           VARCHAR(255) NOT NULL,
    description     TEXT NOT NULL,
    requirements    TEXT NULL,
    responsibilities TEXT NULL,
    employment_type VARCHAR(50) NULL,  -- full_time, part_time, contract, internship
    work_type       VARCHAR(50) NULL,  -- on_site, remote, hybrid
    experience_min  INTEGER NULL,      -- years
    experience_max  INTEGER NULL,
    salary_min      NUMERIC(12,2) NULL,
    salary_max      NUMERIC(12,2) NULL,
    salary_currency VARCHAR(10) NOT NULL DEFAULT 'USD',
    status          VARCHAR(50) NOT NULL DEFAULT 'draft',  -- draft, active, paused, closed
    expires_at      TIMESTAMPTZ NULL,
    headcount       INTEGER NOT NULL DEFAULT 1,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ NULL,
    CONSTRAINT chk_job_status CHECK (status IN ('draft','active','paused','closed'))
);

CREATE INDEX idx_job_postings_company ON job_postings(company_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_job_postings_status ON job_postings(status) WHERE deleted_at IS NULL;
```

#### `skills` (master list)
```sql
CREATE TABLE skills (
    id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name    VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(100) NULL
);
```

#### `job_skills`
```sql
CREATE TABLE job_skills (
    job_id      UUID NOT NULL REFERENCES job_postings(id) ON DELETE CASCADE,
    skill_id    UUID NOT NULL REFERENCES skills(id),
    is_required BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (job_id, skill_id)
);
```

---

### 4.5 Module: candidates

#### `candidates`
```sql
CREATE TABLE candidates (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      UUID NOT NULL REFERENCES companies(id),
    first_name      VARCHAR(100) NOT NULL,
    last_name       VARCHAR(100) NOT NULL,
    email           VARCHAR(255) NOT NULL,
    phone           VARCHAR(50) NULL,
    location        VARCHAR(255) NULL,
    linkedin_url    TEXT NULL,
    portfolio_url   TEXT NULL,
    summary         TEXT NULL,
    status          VARCHAR(50) NOT NULL DEFAULT 'active',  -- active, blacklisted, hired
    source          VARCHAR(100) NULL,   -- referral, linkedin, website, etc.
    avatar_url      TEXT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ NULL,
    UNIQUE(company_id, email),
    CONSTRAINT chk_candidate_status CHECK (status IN ('active','blacklisted','hired'))
);

CREATE INDEX idx_candidates_company ON candidates(company_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_candidates_email ON candidates(email);
```

#### `candidate_experiences`
```sql
CREATE TABLE candidate_experiences (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id    UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    company_name    VARCHAR(255) NOT NULL,
    job_title       VARCHAR(255) NOT NULL,
    start_date      DATE NOT NULL,
    end_date        DATE NULL,       -- NULL = current
    is_current      BOOLEAN NOT NULL DEFAULT FALSE,
    description     TEXT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

#### `candidate_education`
```sql
CREATE TABLE candidate_education (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id    UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    institution     VARCHAR(255) NOT NULL,
    degree          VARCHAR(255) NOT NULL,
    field_of_study  VARCHAR(255) NULL,
    start_year      INTEGER NULL,
    end_year        INTEGER NULL,
    grade           VARCHAR(50) NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

#### `candidate_languages`
```sql
CREATE TABLE candidate_languages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id    UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    language        VARCHAR(100) NOT NULL,
    proficiency     VARCHAR(50) NOT NULL,  -- native, fluent, advanced, intermediate, basic
    CONSTRAINT chk_proficiency CHECK (proficiency IN ('native','fluent','advanced','intermediate','basic'))
);
```

#### `candidate_skills`
```sql
CREATE TABLE candidate_skills (
    candidate_id    UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    skill_id        UUID NOT NULL REFERENCES skills(id),
    years_exp       INTEGER NULL,
    PRIMARY KEY (candidate_id, skill_id)
);
```

#### `candidate_notes`
```sql
CREATE TABLE candidate_notes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id    UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    author_id       UUID NOT NULL REFERENCES user_profiles(id),
    content         TEXT NOT NULL,
    is_private      BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

### 4.6 Module: ats

#### `applications`
```sql
CREATE TABLE applications (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id          UUID NOT NULL REFERENCES job_postings(id),
    candidate_id    UUID NOT NULL REFERENCES candidates(id),
    stage           VARCHAR(50) NOT NULL DEFAULT 'applied',
    rejection_reason TEXT NULL,
    applied_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ NULL,
    UNIQUE(job_id, candidate_id),
    CONSTRAINT chk_stage CHECK (stage IN (
        'applied','screening','shortlisted','interview',
        'technical','hr_interview','offer','hired','rejected'
    ))
);

CREATE INDEX idx_applications_job ON applications(job_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_applications_candidate ON applications(candidate_id);
CREATE INDEX idx_applications_stage ON applications(stage);
```

#### `application_stage_history`
```sql
CREATE TABLE application_stage_history (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id  UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    from_stage      VARCHAR(50) NULL,
    to_stage        VARCHAR(50) NOT NULL,
    changed_by_id   UUID NOT NULL REFERENCES user_profiles(id),
    note            TEXT NULL,
    changed_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

### 4.7 Module: interviews

#### `interviews`
```sql
CREATE TABLE interviews (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id  UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    interview_type  VARCHAR(50) NOT NULL,  -- phone, video, in_person, technical
    scheduled_at    TIMESTAMPTZ NOT NULL,
    duration_min    INTEGER NOT NULL DEFAULT 60,
    location        VARCHAR(255) NULL,     -- address or video link
    status          VARCHAR(50) NOT NULL DEFAULT 'scheduled',  -- scheduled, completed, cancelled, no_show
    notes           TEXT NULL,
    created_by_id   UUID NOT NULL REFERENCES user_profiles(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ NULL
);
```

#### `interview_interviewers`
```sql
CREATE TABLE interview_interviewers (
    interview_id    UUID NOT NULL REFERENCES interviews(id) ON DELETE CASCADE,
    interviewer_id  UUID NOT NULL REFERENCES user_profiles(id),
    PRIMARY KEY (interview_id, interviewer_id)
);
```

#### `interview_evaluations`
```sql
CREATE TABLE interview_evaluations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    interview_id    UUID NOT NULL REFERENCES interviews(id),
    evaluator_id    UUID NOT NULL REFERENCES user_profiles(id),
    score           INTEGER CHECK (score BETWEEN 1 AND 10),
    recommendation  VARCHAR(50) NOT NULL,  -- hire, no_hire, consider
    strengths       TEXT NULL,
    weaknesses      TEXT NULL,
    notes           TEXT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

### 4.8 Module: notifications

#### `notifications`
```sql
CREATE TABLE notifications (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title           VARCHAR(255) NOT NULL,
    message         TEXT NOT NULL,
    type            VARCHAR(50) NOT NULL DEFAULT 'info',  -- info, success, warning, error
    is_read         BOOLEAN NOT NULL DEFAULT FALSE,
    read_at         TIMESTAMPTZ NULL,
    action_url      TEXT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_notifications_user ON notifications(user_id, is_read);
```

---

### 4.9 Module: ai_matching

#### `match_results`
```sql
CREATE TABLE match_results (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id          UUID NOT NULL REFERENCES job_postings(id),
    candidate_id    UUID NOT NULL REFERENCES candidates(id),
    score           NUMERIC(5,2) NOT NULL,   -- 0.00 to 100.00
    provider        VARCHAR(100) NOT NULL,    -- openai, anthropic, etc.
    model           VARCHAR(100) NULL,
    strengths       TEXT[] NULL,
    weaknesses      TEXT[] NULL,
    missing_skills  TEXT[] NULL,
    summary         TEXT NULL,
    raw_response    JSONB NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_match_results_job ON match_results(job_id, score DESC);
```

---

### 4.10 Module: files

#### `file_uploads`
```sql
CREATE TABLE file_uploads (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      UUID NOT NULL REFERENCES companies(id),
    uploaded_by_id  UUID NOT NULL REFERENCES user_profiles(id),
    original_name   VARCHAR(255) NOT NULL,
    storage_key     TEXT NOT NULL,           -- path or S3 key
    storage_backend VARCHAR(50) NOT NULL,    -- local, s3, supabase
    content_type    VARCHAR(100) NOT NULL,
    size_bytes      BIGINT NOT NULL,
    entity_type     VARCHAR(100) NULL,       -- candidate, company, etc.
    entity_id       UUID NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

### 4.11 Module: audit

#### `audit_logs`
```sql
CREATE TABLE audit_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NULL REFERENCES users(id),
    company_id      UUID NULL REFERENCES companies(id),
    action          VARCHAR(100) NOT NULL,   -- user.login, job.create, etc.
    entity_type     VARCHAR(100) NULL,
    entity_id       UUID NULL,
    old_values      JSONB NULL,
    new_values      JSONB NULL,
    ip_address      VARCHAR(45) NULL,
    user_agent      TEXT NULL,
    status          VARCHAR(50) NOT NULL DEFAULT 'success',  -- success, failure
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_company ON audit_logs(company_id);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at DESC);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
```

---

### 4.12 Module: crm

#### `clients`
```sql
CREATE TABLE clients (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      UUID NOT NULL REFERENCES companies(id),
    name            VARCHAR(255) NOT NULL,
    industry        VARCHAR(100) NULL,
    website         VARCHAR(255) NULL,
    status          VARCHAR(50) NOT NULL DEFAULT 'active',
    notes           TEXT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ NULL
);
```

#### `client_contacts`
```sql
CREATE TABLE client_contacts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id       UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    full_name       VARCHAR(255) NOT NULL,
    email           VARCHAR(255) NULL,
    phone           VARCHAR(50) NULL,
    job_title       VARCHAR(100) NULL,
    is_primary      BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

#### `contracts`
```sql
CREATE TABLE contracts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id       UUID NOT NULL REFERENCES clients(id),
    company_id      UUID NOT NULL REFERENCES companies(id),
    title           VARCHAR(255) NOT NULL,
    value           NUMERIC(12,2) NULL,
    currency        VARCHAR(10) NOT NULL DEFAULT 'USD',
    start_date      DATE NULL,
    end_date        DATE NULL,
    status          VARCHAR(50) NOT NULL DEFAULT 'draft',  -- draft, active, expired, cancelled
    file_id         UUID NULL REFERENCES file_uploads(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ NULL
);
```

---

### 4.13 Module: billing

#### `subscription_plans`
```sql
CREATE TABLE subscription_plans (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(100) NOT NULL,
    description     TEXT NULL,
    price           NUMERIC(10,2) NOT NULL,
    currency        VARCHAR(10) NOT NULL DEFAULT 'USD',
    billing_cycle   VARCHAR(50) NOT NULL DEFAULT 'monthly',  -- monthly, yearly
    max_users       INTEGER NULL,
    max_jobs        INTEGER NULL,
    features        JSONB NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

#### `subscriptions`
```sql
CREATE TABLE subscriptions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      UUID NOT NULL REFERENCES companies(id),
    plan_id         UUID NOT NULL REFERENCES subscription_plans(id),
    status          VARCHAR(50) NOT NULL DEFAULT 'active',  -- active, cancelled, expired
    starts_at       TIMESTAMPTZ NOT NULL,
    expires_at      TIMESTAMPTZ NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

#### `invoices`
```sql
CREATE TABLE invoices (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      UUID NOT NULL REFERENCES companies(id),
    subscription_id UUID NULL REFERENCES subscriptions(id),
    invoice_number  VARCHAR(50) UNIQUE NOT NULL,
    amount          NUMERIC(10,2) NOT NULL,
    currency        VARCHAR(10) NOT NULL DEFAULT 'USD',
    status          VARCHAR(50) NOT NULL DEFAULT 'pending',  -- pending, paid, overdue, cancelled
    due_date        DATE NOT NULL,
    paid_at         TIMESTAMPTZ NULL,
    notes           TEXT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ NULL
);
```

---

### 4.14 Module: settings

#### `company_settings`
```sql
CREATE TABLE company_settings (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      UUID NOT NULL UNIQUE REFERENCES companies(id) ON DELETE CASCADE,
    smtp_host       VARCHAR(255) NULL,
    smtp_port       INTEGER NULL DEFAULT 587,
    smtp_username   VARCHAR(255) NULL,
    smtp_password   TEXT NULL,            -- encrypted at app level
    smtp_use_tls    BOOLEAN NOT NULL DEFAULT TRUE,
    from_email      VARCHAR(255) NULL,
    whatsapp_token  TEXT NULL,            -- encrypted
    ai_provider     VARCHAR(100) NULL DEFAULT 'openai',
    ai_model        VARCHAR(100) NULL,
    ai_api_key      TEXT NULL,            -- encrypted
    storage_backend VARCHAR(50) NOT NULL DEFAULT 'local',
    s3_bucket       VARCHAR(255) NULL,
    s3_region       VARCHAR(100) NULL,
    s3_access_key   TEXT NULL,
    s3_secret_key   TEXT NULL,            -- encrypted
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## 5. Key Indexes Summary

| Table | Index | Purpose |
|-------|-------|---------|
| users | email | Login lookup |
| job_postings | company_id, status | Job listing |
| candidates | company_id | Candidate listing |
| applications | job_id, stage | Pipeline view |
| audit_logs | user_id, company_id, created_at | Audit queries |
| notifications | user_id, is_read | Notification bell |
| match_results | job_id, score DESC | Ranked matching |
