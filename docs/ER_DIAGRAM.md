# Entity Relationship Diagram
# AI Recruitment Platform

**Version:** 1.0.0  
**Date:** 2026-08-06

---

## 1. Core Entity Relationships (Text-Based ERD)

```
┌─────────────┐         ┌────────────────────┐
│   companies │ 1─────< │      branches      │
│─────────────│         │────────────────────│
│ id (PK)     │         │ id (PK)            │
│ name        │         │ company_id (FK)    │
│ slug        │         │ name               │
│ logo_url    │         │ address            │
│ industry    │         │ city               │
│ timezone    │         │ is_main            │
└──────┬──────┘         └────────────────────┘
       │ 1
       │
       │<─ Many ─────────────────────────────────────────────┐
       │                                                       │
       ▼                                                       │
┌──────────────────┐    ┌──────────┐    ┌───────────────────┐│
│  user_profiles   │    │  users   │    │  refresh_tokens   ││
│──────────────────│    │──────────│    │───────────────────││
│ id (PK)          │    │ id (PK)  │    │ id (PK)           ││
│ user_id (FK) ────┼───>│ email    │    │ user_id (FK) ─────┼┘
│ company_id (FK)─>│    │ password │    │ token_hash        │
│ branch_id (FK)   │    │ is_active│    │ expires_at        │
│ role             │    │ failed_  │    │ is_revoked        │
│ first_name       │    │ attempts │    └───────────────────┘
│ last_name        │    └──────────┘
│ phone            │
└────────┬─────────┘
         │ 1
         │
    ┌────┴────────────────────┐
    │                         │
    ▼ many                    ▼ many
┌─────────────┐         ┌─────────────┐
│job_postings │         │  interviews │
│─────────────│         │─────────────│
│ id (PK)     │         │ id (PK)     │
│ company_id  │         │ application_│
│ created_by  │         │ _id (FK)    │
│ title       │         │ type        │
│ description │         │ scheduled_at│
│ status      │         │ status      │
│ salary_min  │         └──────┬──────┘
│ salary_max  │                │ 1
└──────┬──────┘                │
       │ 1                     ▼ many
       │              ┌────────────────────┐
       │              │interview_evaluations│
       │              │────────────────────│
       ▼ many         │ id (PK)            │
┌──────────────┐      │ interview_id (FK)  │
│ job_skills   │      │ evaluator_id (FK)  │
│──────────────│      │ score              │
│ job_id (FK)  │      │ recommendation     │
│ skill_id (FK)│      └────────────────────┘
│ is_required  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│    skills    │
│──────────────│
│ id (PK)      │
│ name         │<──────────────────────────────────┐
│ category     │                                   │
└──────────────┘                                   │
                                                   │
┌──────────────┐    ┌──────────────────────┐       │
│  candidates  │1──<│  candidate_skills    │>──────┘
│──────────────│    │──────────────────────│
│ id (PK)      │    │ candidate_id (FK)    │
│ company_id   │    │ skill_id (FK)        │
│ first_name   │    │ years_exp            │
│ last_name    │    └──────────────────────┘
│ email        │
│ phone        │1──<┌──────────────────────┐
│ status       │    │ candidate_experiences │
└──────┬───────┘    │──────────────────────│
       │            │ id (PK)              │
       │1           │ candidate_id (FK)    │
       │            │ company_name         │
       ▼ many       │ job_title            │
┌──────────────┐    │ start_date           │
│ applications │    └──────────────────────┘
│──────────────│
│ id (PK)      │1──<┌──────────────────────┐
│ job_id (FK)  │    │ candidate_education  │
│ candidate_id │    │──────────────────────│
│ stage        │    │ id (PK)              │
│ applied_at   │    │ candidate_id (FK)    │
└──────┬───────┘    │ institution          │
       │1           │ degree               │
       │            └──────────────────────┘
       │
       ▼ many       ┌──────────────────────┐
┌──────────────┐    │ candidate_languages  │
│app_stage_    │ 1──<──────────────────────│
│history       │    │ candidate_id (FK)    │
│──────────────│    │ language             │
│ id (PK)      │    │ proficiency          │
│ application_ │    └──────────────────────┘
│ _id (FK)     │
│ from_stage   │    ┌──────────────────────┐
│ to_stage     │    │  candidate_notes     │
│ changed_by   │ 1──<──────────────────────│
└──────────────┘    │ candidate_id (FK)    │
                    │ author_id (FK)       │
                    │ content              │
                    └──────────────────────┘
```

---

## 2. AI & Files Relationships

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│job_postings  │    │match_results │    │  candidates  │
│──────────────│    │──────────────│    │──────────────│
│ id (PK)      │1──<│ id (PK)      │>──1│ id (PK)      │
└──────────────┘    │ job_id (FK)  │    └──────────────┘
                    │ candidate_id │
                    │ score        │
                    │ provider     │
                    │ strengths[]  │
                    │ missing_     │
                    │ skills[]     │
                    └──────────────┘

┌──────────────┐    ┌──────────────┐
│  companies   │    │ file_uploads │
│──────────────│    │──────────────│
│ id (PK)      │1──<│ id (PK)      │
└──────────────┘    │ company_id   │
                    │ uploaded_by  │
                    │ storage_key  │
                    │ content_type │
                    │ entity_type  │
                    │ entity_id    │
                    └──────────────┘
```

---

## 3. CRM & Billing Relationships

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  companies   │    │   clients    │    │client_contacts│
│──────────────│    │──────────────│    │──────────────│
│ id (PK)      │1──<│ id (PK)      │1──<│ id (PK)      │
└──────────────┘    │ company_id   │    │ client_id    │
                    │ name         │    │ full_name    │
                    └──────┬───────┘    │ email        │
                           │1           └──────────────┘
                           │
                           ▼ many
                    ┌──────────────┐
                    │  contracts   │
                    │──────────────│
                    │ id (PK)      │
                    │ client_id    │
                    │ title        │
                    │ value        │
                    │ status       │
                    └──────────────┘

┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  companies   │    │subscriptions │    │subscription_ │
│──────────────│    │──────────────│    │plans         │
│ id (PK)      │1──<│ id (PK)      │>──1│──────────────│
└──────┬───────┘    │ company_id   │    │ id (PK)      │
       │            │ plan_id (FK) │    │ name         │
       │1           │ status       │    │ price        │
       │            └──────────────┘    │ max_users    │
       ▼ many                           └──────────────┘
┌──────────────┐
│   invoices   │
│──────────────│
│ id (PK)      │
│ company_id   │
│ amount       │
│ status       │
│ due_date     │
└──────────────┘
```

---

## 4. Audit & Notifications

```
┌──────────────┐    ┌──────────────┐
│    users     │    │  audit_logs  │
│──────────────│    │──────────────│
│ id (PK)      │1──<│ id (PK)      │
└──────────────┘    │ user_id (FK) │
                    │ action       │
                    │ entity_type  │
                    │ entity_id    │
                    │ old_values   │
                    │ new_values   │
                    │ ip_address   │
                    └──────────────┘

┌──────────────┐    ┌──────────────────┐
│    users     │    │  notifications   │
│──────────────│    │──────────────────│
│ id (PK)      │1──<│ id (PK)          │
└──────────────┘    │ user_id (FK)     │
                    │ title            │
                    │ message          │
                    │ type             │
                    │ is_read          │
                    │ action_url       │
                    └──────────────────┘
```

---

## 5. Interview Relationships Detail

```
┌──────────────┐    ┌──────────────────────┐
│ applications │    │      interviews      │
│──────────────│    │──────────────────────│
│ id (PK)      │1──<│ id (PK)              │
│ job_id       │    │ application_id (FK)  │
│ candidate_id │    │ interview_type       │1──<┌─────────────────────┐
│ stage        │    │ scheduled_at         │    │interview_interviewers│
└──────────────┘    │ duration_min         │    │─────────────────────│
                    │ location             │    │ interview_id (FK)   │
                    │ status               │    │ interviewer_id (FK) │
                    └─────────┬────────────┘    └─────────────────────┘
                              │1
                              ▼ many
                    ┌─────────────────────┐
                    │interview_evaluations│
                    │─────────────────────│
                    │ id (PK)             │
                    │ interview_id (FK)   │
                    │ evaluator_id (FK)   │
                    │ score (1-10)        │
                    │ recommendation      │
                    │ strengths           │
                    │ weaknesses          │
                    └─────────────────────┘
```
