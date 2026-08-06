"""Files module schemas."""
import uuid
from typing import Optional
from datetime import datetime
from app.core.base.schema import BaseSchema


class FileUploadResponse(BaseSchema):
    id: uuid.UUID
    original_name: str
    content_type: str
    size_bytes: int
    storage_backend: str
    created_at: datetime
