
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from app.services.file_storage import save_uploaded_image

router = APIRouter(prefix="/upload", tags=["Uploads"])

MEDIA_DIR = "app/media"

@router.post("/bytes")
async def upload_bytes(file: bytes = File(...)):
    return {
        "filename":"file uploaded",
        "size_bytes": len(file)
    }

@router.post("/file")
async def upload_file(file: UploadFile = File(...)):
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "file_size": len(await file.read())
    }

@router.post("/save")
async def save_file(file: UploadFile = File(...)):
    try:
        return save_uploaded_image(file)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving file: {str(e)}"
        )
