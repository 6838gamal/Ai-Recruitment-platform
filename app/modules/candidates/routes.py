
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


@router.get(
    "/",
    response_class=HTMLResponse,
    name="candidates_list",
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


@router.get(
    "/create",
    response_class=HTMLResponse,
    name="candidates_create",
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


@router.get(
    "/{candidate_id}",
    response_class=HTMLResponse,
    name="candidates_view",
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


@router.get(
    "/{candidate_id}/edit",
    response_class=HTMLResponse,
    name="candidates_edit",
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

