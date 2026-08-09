---
name: Dynamic templates migration
about: Move static tables and detail views to dynamic partials driven by SQLAlchemy model metadata
---

This PR migrates several list/detail templates to use reusable Jinja2 macros that render tables and detail cards dynamically from SQLAlchemy model metadata. The goal is to reduce template duplication, make views resilient to schema changes, and ensure a consistent UX when data is missing.

Changes included:

- New utility: `app/utils/inspect_model.py` to extract model fields metadata (already added).
- New partials:
  - `app/templates/partials/dynamic_table.html` (macro `dynamic_table`)
  - `app/templates/partials/dynamic_detail.html` (macro `dynamic_detail`)
- Updated routes to pass `fields = get_model_fields_sqlalchemy(Model)` into template context where applicable.
- Converted `users` and `companies` list/profile templates to use the dynamic partials with graceful fallbacks when metadata or data is missing.

Notes for reviewers:
- Sensitive fields are excluded centrally via `SENSITIVE` in `inspect_model.py`. Current list includes common sensitive names like `password`, `hashed_password`, token hashes, and related fields. Please review and propose additions if necessary.
- Rendering of FK relationships attempts to access `full_name` or `name` attributes; complex relationship labeling may need model-specific overrides.

Smoke tests:
1. Run server and open `/users` and `/companies`.
2. Verify empty states show a friendly message and invite/new button.
3. Verify existing records render columns dynamically and sensitive fields are not shown.

