import os
import shutil
import uuid
from fastapi import UploadFile, HTTPException, status

MEDIA_DIR = "app/media"
ALLOW_MIME = ["image/jpeg", "image/png"]
MAX_UPLOAD_FILE_SIZE_MB = int(os.getenv("MAX_UPLOAD_FILE_SIZE_MB", 1))

def ensure_media_dir() -> None:
    os.makedirs(MEDIA_DIR, exist_ok=True)

def save_uploaded_image(file: UploadFile) -> dict:

    if file.content_type not in ALLOW_MIME:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, 
            detail=f"Only {', '.join(ALLOW_MIME)} images are allowed")
    
    ensure_media_dir()

    extension = os.path.splitext(file.filename)[1]
    file_name = f"{uuid.uuid4().hex}{extension}"
    file_path = os.path.join(MEDIA_DIR, file_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer, length=1024*1024)

    size = os.path.getsize(file_path)
    if size > MAX_UPLOAD_FILE_SIZE_MB * 1024 * 1024:
        os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, 
            detail=f"File size must be less than {MAX_UPLOAD_FILE_SIZE_MB}MB")

    return {
        "filename": file_name,
        "content_type": file.content_type,
        "file_size": file.size,
        "file_url": f"/media/{file_name}"
    }