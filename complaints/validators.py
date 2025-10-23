
from __future__ import annotations

from typing import Optional
from django.core.exceptions import ValidationError

try:
    import magic  # type: ignore
except Exception:  # pragma: no cover
    magic = None

MAX_FILE_MB = 20
MAX_FILE_BYTES = MAX_FILE_MB * 1024 * 1024

ALLOWED_MIME_TYPES = {
    "image/jpeg", "image/png", "image/gif", "image/webp",
    "audio/mpeg", "audio/wav", "audio/x-wav", "audio/ogg", "audio/x-ogg", "audio/flac",
    "video/mp4", "video/quicktime", "video/x-msvideo", "video/x-matroska", "video/webm",
}


def _detect_mime(file_obj) -> Optional[str]:
    if magic is None:
        return None
    pos = file_obj.tell()
    try:
        header = file_obj.read(2048)
        if isinstance(header, bytes):
            return magic.Magic(mime=True).from_buffer(header)
        if hasattr(header, "encode"):
            return magic.Magic(mime=True).from_buffer(header.encode("utf-8"))
        return None
    finally:
        try:
            file_obj.seek(pos)
        except Exception:
            pass


def validate_file_size(f) -> None:
    size = getattr(f, "size", None)
    if size is not None and size > MAX_FILE_BYTES:
        raise ValidationError(f"File too large: limit is {MAX_FILE_MB} MB.")


def validate_mime_type(f) -> None:
    mime = None
    try:
        if hasattr(f, "file"):
            mime = _detect_mime(f.file)
        else:
            mime = _detect_mime(f)
    except Exception:
        mime = None

    # If detection failed or returned an unallowed type, fallback to file extension mapping
    def mime_from_ext(name: str) -> str | None:
        name = name.lower()
        if name.endswith((".jpg", ".jpeg")):
            return "image/jpeg"
        if name.endswith(".png"):
            return "image/png"
        if name.endswith(".gif"):
            return "image/gif"
        if name.endswith(".webp"):
            return "image/webp"
        if name.endswith((".mp3", ".ogg", ".wav", ".flac")):
            return "audio/mpeg"
        if name.endswith((".mp4", ".mov", ".avi", ".mkv", ".webm")):
            return "video/mp4"
        return None

    if (mime is None or mime not in ALLOWED_MIME_TYPES) and hasattr(f, "name"):
        ext_mime = mime_from_ext(getattr(f, "name", ""))
        if ext_mime in ALLOWED_MIME_TYPES:
            mime = ext_mime

    if mime is None or mime not in ALLOWED_MIME_TYPES:
        raise ValidationError("Unsupported file type. Only image/audio/video files are allowed.")