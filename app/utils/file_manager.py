"""Safe file upload, deletion, and path helpers."""

from __future__ import annotations

import shutil
from pathlib import Path

DEFAULT_ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".txt", ".png", ".jpg", ".jpeg"}


def ensure_directory(path: str | Path) -> Path:
    """Create a directory if needed and return its Path."""
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def build_safe_filename(filename: str) -> str:
    """Return a filesystem-safe filename."""
    safe = "".join(character if character.isalnum() or character in "._-" else "_" for character in filename)
    return safe.strip("._") or "file"


def validate_extension(filename: str, allowed_extensions: set[str] | None = None) -> str:
    """Validate a filename extension and return the normalized extension."""
    extension = Path(filename).suffix.lower()
    allowed = allowed_extensions or DEFAULT_ALLOWED_EXTENSIONS
    if extension not in allowed:
        raise ValueError(f"File extension '{extension}' is not allowed.")
    return extension


def resolve_safe_path(base_directory: str | Path, filename: str) -> Path:
    """Resolve a filename inside a base directory and block path traversal."""
    base_path = ensure_directory(base_directory).resolve()
    target_path = (base_path / build_safe_filename(Path(filename).name)).resolve()
    if base_path not in target_path.parents and target_path != base_path:
        raise ValueError("Resolved path is outside the base directory.")
    return target_path


def save_upload_file(
    source_path: str | Path,
    destination_directory: str | Path,
    filename: str | None = None,
    allowed_extensions: set[str] | None = None,
) -> Path:
    """Copy an uploaded file-like path into a safe destination directory."""
    source = Path(source_path)
    if not source.exists() or not source.is_file():
        raise FileNotFoundError(f"Source file not found: {source}.")

    target_name = filename or source.name
    validate_extension(target_name, allowed_extensions)
    destination = resolve_safe_path(destination_directory, target_name)
    shutil.copyfile(source, destination)
    return destination


def delete_file(path: str | Path, missing_ok: bool = True) -> bool:
    """Delete a file and return whether a file was removed."""
    file_path = Path(path)
    if not file_path.exists():
        if missing_ok:
            return False
        raise FileNotFoundError(f"File not found: {file_path}.")
    if not file_path.is_file():
        raise ValueError("Only regular files can be deleted.")
    file_path.unlink()
    return True
