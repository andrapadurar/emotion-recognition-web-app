import os
import uuid
from pathlib import Path

#funcții auxiliare utilizate pentru gestionarea fișierelor încărcate, validarea extensiilor 
# și generarea unor nume unice


def ensure_folder_exists(folder_path: str) -> None:
    os.makedirs(folder_path, exist_ok=True)


def get_file_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


def is_allowed_extension(filename: str, allowed_extensions: set[str]) -> bool:
    return get_file_extension(filename) in allowed_extensions


def generate_unique_filename(filename: str) -> str:
    extension = get_file_extension(filename)
    return f"{uuid.uuid4().hex}{extension}"


def get_file_size_mb(file_path: str) -> float:
    size_bytes = os.path.getsize(file_path)
    return size_bytes / (1024 * 1024)