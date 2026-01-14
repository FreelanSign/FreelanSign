"""
Supabase Storage adapter for avatar uploads.

AIDEV-NOTE: Simple adapter - uploads file to Supabase Storage, returns public URL.
Bucket must be created manually in Supabase dashboard and set to public.
"""

import logging
import uuid
from typing import BinaryIO

from django.conf import settings

logger = logging.getLogger(__name__)


class SupabaseStorageError(Exception):
    """Raised when Supabase storage operation fails."""

    pass


class SupabaseStorageAdapter:
    """Adapter for Supabase Storage operations."""

    ALLOWED_CONTENT_TYPES = {
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/gif",
    }
    MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB

    def __init__(self):
        self._client = None

    @property
    def client(self):
        """Lazy initialization of Supabase client."""
        if self._client is None:
            if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
                raise SupabaseStorageError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be configured")
            from supabase import create_client

            self._client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
        return self._client

    @property
    def bucket(self) -> str:
        return settings.SUPABASE_STORAGE_BUCKET

    def upload_avatar(self, user_id: int, file: BinaryIO, content_type: str, filename: str) -> str:
        """
        Upload avatar to Supabase Storage.

        Args:
            user_id: User ID for path organization
            file: File-like object with read() method
            content_type: MIME type (must be in ALLOWED_CONTENT_TYPES)
            filename: Original filename (used for extension)

        Returns:
            Public URL of uploaded file

        Raises:
            SupabaseStorageError: If upload fails or validation fails
        """
        if content_type not in self.ALLOWED_CONTENT_TYPES:
            raise SupabaseStorageError(
                f"Invalid content type: {content_type}. " f"Allowed: {', '.join(self.ALLOWED_CONTENT_TYPES)}"
            )

        file_data = file.read()
        if len(file_data) > self.MAX_FILE_SIZE:
            raise SupabaseStorageError(f"File too large: {len(file_data)} bytes. Max: {self.MAX_FILE_SIZE} bytes")

        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "jpg"
        unique_name = f"{uuid.uuid4()}.{ext}"
        path = f"{user_id}/{unique_name}"

        logger.info(f"Uploading avatar for user {user_id}: {path}")

        try:
            self.client.storage.from_(self.bucket).upload(
                path,
                file_data,
                {"content-type": content_type, "upsert": "true"},
            )
        except Exception as e:
            logger.error(f"Supabase upload failed for user {user_id}: {e}")
            raise SupabaseStorageError(f"Upload failed: {e}") from e

        public_url = self.client.storage.from_(self.bucket).get_public_url(path)
        logger.info(f"Avatar uploaded for user {user_id}: {public_url}")

        return public_url

    def delete_avatar(self, path: str) -> bool:
        """
        Delete avatar from Supabase Storage.

        Args:
            path: Full path or URL of the file

        Returns:
            True if deleted successfully
        """
        if not path:
            return False

        # Extract path from URL if needed
        if path.startswith("http"):
            # URL format: https://{project}.supabase.co/storage/v1/object/public/{bucket}/{path}
            try:
                path = path.split(f"/public/{self.bucket}/")[1]
            except IndexError:
                logger.warning(f"Could not extract path from URL: {path}")
                return False

        try:
            self.client.storage.from_(self.bucket).remove([path])
            logger.info(f"Avatar deleted: {path}")
            return True
        except Exception as e:
            logger.warning(f"Failed to delete avatar {path}: {e}")
            return False


# Singleton instance
_storage_adapter = None


def get_storage_adapter() -> SupabaseStorageAdapter:
    """Get singleton instance of SupabaseStorageAdapter."""
    global _storage_adapter
    if _storage_adapter is None:
        _storage_adapter = SupabaseStorageAdapter()
    return _storage_adapter
