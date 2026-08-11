```python
"""Candidates module routes."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from app.dependencies import get_current_user_profile
from app.utils.enhanced_templates import EnhancedJinja2Templates


router = APIRouter(
    prefix="/candidates",
    tags=["Candidates"],
)

templates = EnhancedJinja2Templates(
    directory="app/templates"
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
    current_user=Depends(get_current_user_profile),
):
    return templates.TemplateResponse(
        request,
        "candidates/list.html",
        {
            "request": request,
            "current_user": current_user,
        },
    )


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
    return templates.TemplateResponse(
        request,
        "candidates/create.html",
        {
            "request": request,
            "current_user": current_user,
        },
    )


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
    current_user=Depends(get_current_user_profile),
):
    # سيتم إضافة إنشاء المرشح في قاعدة البيانات هنا.
    #
    # مثال لاحقًا:
    # form = await request.form()
    # ...
    #
    # حاليًا نعيد المستخدم إلى القائمة.

    from fastapi.responses import RedirectResponse

    return RedirectResponse(
        url=request.url_for("candidates:list"),
        status_code=303,
    )


# ============================================================
# View Candidate
# ============================================================

@router.get(
    "/{candidate_id}",
    response_class=HTMLResponse,
    name="candidates:view",
)
async def view_candidate(
    candidate_id: str,
    request: Request,
    current_user=Depends(get_current_user_profile),
):
    return templates.TemplateResponse(
        request,
        "candidates/view.html",
        {
            "request": request,
            "current_user": current_user,
            "candidate_id": candidate_id,
        },
    )


# ============================================================
# Edit Candidate - Form
# ============================================================

@router.get(
    "/{candidate_id}/edit",
    response_class=HTMLResponse,
    name="candidates:edit",
)
async def edit_candidate(
    candidate_id: str,
    request: Request,
    current_user=Depends(get_current_user_profile),
):
    return templates.TemplateResponse(
        request,
        "candidates/edit.html",
        {
            "request": request,
            "current_user": current_user,
            "candidate_id": candidate_id,
        },
    )


# ============================================================
# Edit Candidate - Submit
# ============================================================

@router.post(
    "/{candidate_id}/edit",
    response_class=HTMLResponse,
    name="candidates:edit_submit",
)
async def edit_candidate_submit(
    candidate_id: str,
    request: Request,
    current_user=Depends(get_current_user_profile),
):
    from fastapi.responses import RedirectResponse

    return RedirectResponse(
        url=request.url_for(
            "candidates:view",
            candidate_id=candidate_id,
        ),
        status_code=303,
    )
```
