
"""Candidates module routes."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.core.permissions import Permission
from app.dependencies import require_permission


router = APIRouter(
    prefix="/candidates",
    tags=["Candidates"],
)

templates = Jinja2Templates(directory="app/templates")


@router.get(
    "/",
    response_class=HTMLResponse,
    name="candidates:list",
)
async def candidate_list(
    request: Request,
    current_user=Depends(
        require_permission(Permission.VIEW_CANDIDATES)
    ),
):
    """Render the candidates list page."""
    return templates.TemplateResponse(
        "candidates/list.html",
        {
            "request": request,
            "current_user": current_user,
            "candidates": [],
        },
    )


@router.get(
    "/create",
    response_class=HTMLResponse,
    name="candidates:create",
)
async def candidate_create_form(
    request: Request,
    current_user=Depends(
        require_permission(Permission.CREATE_CANDIDATES)
    ),
):
    """Render the candidate creation form."""
    return templates.TemplateResponse(
        "candidates/create.html",
        {
            "request": request,
            "current_user": current_user,
        },
    )


@router.post("/create")
async def candidate_create_submit(
    request: Request,
    current_user=Depends(
        require_permission(Permission.CREATE_CANDIDATES)
    ),
):
    """Handle candidate form submission.

    Database saving logic should be implemented in the
    candidate service when the Candidate model is ready.
    """
    # TODO:
    # 1. Read form data.
    # 2. Validate the submitted data.
    # 3. Create the Candidate through CandidateService.
    # 4. Save the candidate to the database.

    return RedirectResponse(
        url="/candidates/",
        status_code=303,
    )
