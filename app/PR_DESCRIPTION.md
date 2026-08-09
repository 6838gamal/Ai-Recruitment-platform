feat(templates): migrate more modules to dynamic partials

- Converted companies list view to use dynamic_table partial and pass fields metadata.
- Added dynamic partials and inspection util in prior commits.

Remaining work:
- Convert accounts, candidates, jobs templates and any other list/detail views to use the partials.
- Implement an in-memory cache for inspect_model results (TTL) to improve performance.

