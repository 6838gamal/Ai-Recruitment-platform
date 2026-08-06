"""File Storage Adapter Pattern."""
import os
import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from app.config import settings


class StorageAdapter(ABC):
    """Abstract base for file storage backends."""

    @abstractmethod
    def save(self, file_bytes: bytes, filename: str, content_type: str) -> str:
        """Save file and return storage key."""
        ...

    @abstractmethod
    def get_url(self, storage_key: str) -> str:
        """Get URL to access the file."""
        ...

    @abstractmethod
    def delete(self, storage_key: str) -> None:
        """Delete a file."""
        ...


class LocalStorageAdapter(StorageAdapter):
    """Store files on local filesystem."""

    def __init__(self, upload_dir: str = "./uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def save(self, file_bytes: bytes, filename: str, content_type: str) -> str:
        ext = Path(filename).suffix
        storage_key = f"{uuid.uuid4().hex}{ext}"
        file_path = self.upload_dir / storage_key
        file_path.write_bytes(file_bytes)
        return storage_key

    def get_url(self, storage_key: str) -> str:
        return f"/files/download/{storage_key}"

    def delete(self, storage_key: str) -> None:
        file_path = self.upload_dir / storage_key
        if file_path.exists():
            file_path.unlink()


class S3StorageAdapter(StorageAdapter):
    """Store files in Amazon S3."""

    def __init__(self, bucket: str, region: str, access_key: str, secret_key: str):
        self.bucket = bucket
        self.region = region
        self.access_key = access_key
        self.secret_key = secret_key

    def save(self, file_bytes: bytes, filename: str, content_type: str) -> str:
        # TODO: Implement S3 upload using boto3
        raise NotImplementedError("S3 storage not yet implemented")

    def get_url(self, storage_key: str) -> str:
        return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{storage_key}"

    def delete(self, storage_key: str) -> None:
        raise NotImplementedError("S3 storage not yet implemented")


def get_storage() -> StorageAdapter:
    """Factory: return the configured storage adapter."""
    backend = settings.STORAGE_BACKEND.lower()
    if backend == "s3":
        return S3StorageAdapter(
            bucket=settings.S3_BUCKET or "",
            region=settings.S3_REGION or "us-east-1",
            access_key=settings.S3_ACCESS_KEY or "",
            secret_key=settings.S3_SECRET_KEY or "",
        )
    else:
        return LocalStorageAdapter(upload_dir=settings.LOCAL_UPLOAD_DIR)
