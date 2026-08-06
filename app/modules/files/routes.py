"""Files module routes."""
from fastapi import APIRouter, Depends, File, Request, UploadFile
from fastapi.responses import JSONResponse

from app.dependencies import get_current_user_profile

router = APIRouter(prefix="/files", tags=["Files"])


@router.post("/upload", name="files:upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user_profile),
):
    """Upload a file."""
    from app.modules.files.storage import get_storage
    storage = get_storage()
    file_bytes = await file.read()
    storage_key = storage.save(file_bytes, file.filename or "upload", file.content_type or "application/octet-stream")
    return JSONResponse({"storage_key": storage_key, "original_name": file.filename})
