from pathlib import Path

from app.services import s3_service
from fastapi import APIRouter, File, UploadFile
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/files", tags=["files"])

# Base directory for downloadable files
DOWNLOADS_DIR = Path("/app/downloads")


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    file_url = await s3_service.upload_file_to_s3(
        contents, file.filename, file.content_type
    )
    return {"url": file_url}


@router.get("/download/{filename}")
async def download_file(filename: str):
    """
    Download a file by name from the downloads directory.
    FileResponse handles streaming and content-type automatically.
    """
    # Construct full path and validate it exists
    file_path = DOWNLOADS_DIR / filename

    file_url = await s3_service.download_file_from_s3(filename)
    # FileResponse streams the file and sets Content-Type based on extension

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=filename,  # Sets Content-Disposition header
        media_type="application/octet-stream",  # Force download instead of display
    )
