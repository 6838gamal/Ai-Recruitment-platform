"""Candidates module routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user_profile
from app.modules.candidates.services import CandidateService
from app.utils.enhanced_templates import EnhancedJinja2Templates

router = APIRouter(
prefix="/candidates",
tags=["Candidates"],
)

templates = EnhancedJinja2Templates(
directory="app/templates",
)

# ============================================================

# Candidates List

# ============================================================

@router.get(
"/",
response_class=HTMLResponse,
name="candidates:list",
)
async def list_candidates(
request: Request,
db: Session = Depends(get_db),
current_user=Depends(get_current_user_profile),
):
"""Display candidates for the current company."""

```
company_id = current_user.company_id

service = CandidateService(db)

candidates = service.get_candidates(
    company_id=company_id,
)

return templates.TemplateResponse(
    request,
    "candidates/list.html",
    {
        "request": request,
        "current_user": current_user,
        "candidates": candidates,
    },
)
```

# ============================================================

# Create Candidate - Form

# ============================================================

@router.get(
"/create",
response_class=HTMLResponse,
name="candidates:create",
)
async def create_candidate(
request: Request,
current_user=Depends(get_current_user_profile),
):
"""Display create candidate form."""

```
return templates.TemplateResponse(
    request,
    "candidates/create.html",
    {
        "request": request,
        "current_user": current_user,
    },
)
```

# ============================================================

# Create Candidate - Submit

# ============================================================

@router.post(
"/create",
response_class=HTMLResponse,
name="candidates:create_submit",
)
async def create_candidate_submit(
request: Request,
db: Session = Depends(get_db),
current_user=Depends(get_current_user_profile),
):
"""Create a candidate and redirect to candidates list."""

```
form = await request.form()

first_name = str(form.get("first_name", "")).strip()
last_name = str(form.get("last_name", "")).strip()
email = str(form.get("email", "")).strip()

phone = str(form.get("phone", "")).strip() or None
location = str(form.get("location", "")).strip() or None
linkedin_url = str(form.get("linkedin_url", "")).strip() or None
portfolio_url = str(form.get("portfolio_url", "")).strip() or None
summary = str(form.get("summary", "")).strip() or None
status = str(form.get("status", "new")).strip() or "new"
source = str(form.get("source", "")).strip() or None

# Basic validation
if not first_name or not last_name or not email:
    return templates.TemplateResponse(
        request,
        "candidates/create.html",
        {
            "request": request,
            "current_user": current_user,
            "error": "First name, last name and email are required.",
        },
        status_code=400,
    )

company_id = current_user.company_id

service = CandidateService(db)

candidate = service.create_candidate(
    company_id=company_id,
    first_name=first_name,
    last_name=last_name,
    email=email,
    phone=phone,
    location=location,
    linkedin_url=linkedin_url,
    portfolio_url=portfolio_url,
    summary=summary,
    status=status,
    source=source,
)

return RedirectResponse(
    url=request.url_for(
        "candidates:view",
        candidate_id=str(candidate.id),
    ),
    status_code=303,
)
```

# ============================================================

# View Candidate

# ============================================================

@router.get(
"/{candidate_id}",
response_class=HTMLResponse,
name="candidates:view",
)
async def view_candidate(
candidate_id: UUID,
request: Request,
db: Session = Depends(get_db),
current_user=Depends(get_current_user_profile),
):
"""Display a single candidate."""

```
company_id = current_user.company_id

service = CandidateService(db)

candidate = service.get_candidate(
    candidate_id=candidate_id,
    company_id=company_id,
)

if not candidate:
    return RedirectResponse(
        url=request.url_for("candidates:list"),
        status_code=303,
    )

return templates.TemplateResponse(
    request,
    "candidates/view.html",
    {
        "request": request,
        "current_user": current_user,
        "candidate": candidate,
    },
)
```

# ============================================================

# Edit Candidate - Form

# ============================================================

@router.get(
"/{candidate_id}/edit",
response_class=HTMLResponse,
name="candidates:edit_form",
)
async def edit_candidate(
candidate_id: UUID,
request: Request,
db: Session = Depends(get_db),
current_user=Depends(get_current_user_profile),
):
"""Display edit candidate form."""

```
company_id = current_user.company_id

service = CandidateService(db)

candidate = service.get_candidate(
    candidate_id=candidate_id,
    company_id=company_id,
)

if not candidate:
    return RedirectResponse(
        url=request.url_for("candidates:list"),
        status_code=303,
    )

return templates.TemplateResponse(
    request,
    "candidates/edit.html",
    {
        "request": request,
        "current_user": current_user,
        "candidate": candidate,
    },
)
```

# ============================================================

# Edit Candidate - Submit

# ============================================================

@router.post(
"/{candidate_id}/edit",
response_class=HTMLResponse,
name="candidates:edit_submit",
)
async def edit_candidate_submit(
candidate_id: UUID,
request: Request,
db: Session = Depends(get_db),
current_user=Depends(get_current_user_profile),
):
"""Update an existing candidate."""

```
form = await request.form()

first_name = str(form.get("first_name", "")).strip()
last_name = str(form.get("last_name", "")).strip()
email = str(form.get("email", "")).strip()

phone = str(form.get("phone", "")).strip() or None
location = str(form.get("location", "")).strip() or None
linkedin_url = str(form.get("linkedin_url", "")).strip() or None
portfolio_url = str(form.get("portfolio_url", "")).strip() or None
summary = str(form.get("summary", "")).strip() or None
status = str(form.get("status", "new")).strip() or "new"
source = str(form.get("source", "")).strip() or None

if not first_name or not last_name or not email:
    return RedirectResponse(
        url=request.url_for(
            "candidates:edit_form",
            candidate_id=str(candidate_id),
        ),
        status_code=303,
    )

company_id = current_user.company_id

service = CandidateService(db)

candidate = service.update_candidate(
    candidate_id=candidate_id,
    company_id=company_id,
    first_name=first_name,
    last_name=last_name,
    email=email,
    phone=phone,
    location=location,
    linkedin_url=linkedin_url,
    portfolio_url=portfolio_url,
    summary=summary,
    status=status,
    source=source,
)

if not candidate:
    return RedirectResponse(
        url=request.url_for("candidates:list"),
        status_code=303,
    )

return RedirectResponse(
    url=request.url_for(
        "candidates:view",
        candidate_id=str(candidate.id),
    ),
    status_code=303,
)
```

# ============================================================

# Delete Candidate

# ============================================================

@router.post(
"/{candidate_id}/delete",
response_class=HTMLResponse,
name="candidates:delete",
)
async def delete_candidate(
candidate_id: UUID,
request: Request,
db: Session = Depends(get_db),
current_user=Depends(get_current_user_profile),
):
"""Delete a candidate."""

```
company_id = current_user.company_id

service = CandidateService(db)

deleted = service.delete_candidate(
    candidate_id=candidate_id,
    company_id=company_id,
)

return RedirectResponse(
    url=request.url_for("candidates:list"),
    status_code=303,
)
```
