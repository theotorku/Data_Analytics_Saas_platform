from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File as FastAPIFile, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
import shutil
import logging
from pathlib import Path

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.models.file import File
from app.schemas.files import (
    FileUpload,
    File as FileSchema,
    FileList,
    FileMetadata,
    FileUpdate,
    FileWithAnalysis
)
from app.api.deps import get_current_active_user

router = APIRouter()
logger = logging.getLogger(__name__)

# Ensure upload directory exists
UPLOAD_DIR = Path(settings.UPLOAD_FOLDER)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def get_file_extension(filename: str) -> str:
    """Extract file extension from filename"""
    return filename.split('.')[-1].lower() if '.' in filename else ''


def validate_file_extension(filename: str) -> bool:
    """Validate if file extension is allowed"""
    extension = get_file_extension(filename)
    return extension in settings.ALLOWED_EXTENSIONS


def generate_unique_filename(original_filename: str) -> str:
    """Generate a unique filename to prevent collisions"""
    extension = get_file_extension(original_filename)
    unique_id = str(uuid.uuid4())
    return f"{unique_id}.{extension}" if extension else unique_id


@router.post("/upload", response_model=FileUpload, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload a new file for analysis.

    - **file**: The file to upload (CSV, XLSX, XLS, JSON, TXT)
    - Returns file metadata
    """
    # Validate file extension
    if not validate_file_extension(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    # Read file content to check size
    file_content = await file.read()
    file_size = len(file_content)

    # Validate file size
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / (1024 * 1024):.2f} MB"
        )

    # Check user storage quota
    if not current_user.can_upload_file(file_size):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Storage quota exceeded. Please upgrade your plan or delete some files."
        )

    # Generate unique filename and save file
    unique_filename = generate_unique_filename(file.filename)
    file_path = UPLOAD_DIR / unique_filename

    try:
        with open(file_path, 'wb') as f:
            f.write(file_content)
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error saving file"
        )

    # Create file record in database
    db_file = File(
        filename=unique_filename,
        original_filename=file.filename,
        file_path=str(file_path),
        file_size=file_size,
        file_type=get_file_extension(file.filename),
        mime_type=file.content_type,
        status="uploaded",
        owner_id=current_user.id
    )

    db.add(db_file)

    # Update user storage and file count
    current_user.update_storage_used(file_size)
    current_user.increment_file_count()

    db.commit()
    db.refresh(db_file)

    logger.info(
        f"File uploaded: {file.filename} by user {current_user.username}")

    return db_file


@router.get("", response_model=FileList)
async def list_files(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    file_type: Optional[str] = Query(None, description="Filter by file type"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List all files for the current user with pagination and filters.

    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **status_filter**: Filter by status (uploaded, processing, completed, failed)
    - **file_type**: Filter by file type (csv, xlsx, json, etc.)
    """
    # Build query
    query = db.query(File).filter(
        File.owner_id == current_user.id,
        File.is_deleted == False
    )

    # Apply filters
    if status_filter:
        query = query.filter(File.status == status_filter)
    if file_type:
        query = query.filter(File.file_type == file_type)

    # Get total count
    total = query.count()

    # Calculate pagination
    total_pages = (total + page_size - 1) // page_size
    offset = (page - 1) * page_size

    # Get paginated results
    files = query.order_by(File.created_at.desc()).offset(
        offset).limit(page_size).all()

    return {
        "files": files,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


@router.get("/{file_id}", response_model=FileWithAnalysis)
async def get_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific file by ID with analysis results.

    - **file_id**: The ID of the file to retrieve
    """
    file = db.query(File).filter(
        File.id == file_id,
        File.owner_id == current_user.id,
        File.is_deleted == False
    ).first()

    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    # Update accessed_at timestamp
    from sqlalchemy.sql import func
    file.accessed_at = func.now()
    db.commit()

    return file


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a file (soft delete).

    - **file_id**: The ID of the file to delete
    """
    file = db.query(File).filter(
        File.id == file_id,
        File.owner_id == current_user.id,
        File.is_deleted == False
    ).first()

    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    # Soft delete
    file.is_deleted = True

    # Update user storage
    current_user.update_storage_used(-file.file_size)

    db.commit()

    logger.info(
        f"File deleted: {file.filename} by user {current_user.username}")

    return None


@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Download a file.

    - **file_id**: The ID of the file to download
    """
    file = db.query(File).filter(
        File.id == file_id,
        File.owner_id == current_user.id,
        File.is_deleted == False
    ).first()

    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    # Check if file exists on disk
    if not os.path.exists(file.file_path):
        logger.error(f"File not found on disk: {file.file_path}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on server"
        )

    # Update accessed_at timestamp
    from sqlalchemy.sql import func
    file.accessed_at = func.now()
    db.commit()

    return FileResponse(
        path=file.file_path,
        filename=file.original_filename,
        media_type=file.mime_type or 'application/octet-stream'
    )


@router.get("/{file_id}/metadata", response_model=FileMetadata)
async def get_file_metadata(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get file metadata without analysis results.

    - **file_id**: The ID of the file
    """
    file = db.query(File).filter(
        File.id == file_id,
        File.owner_id == current_user.id,
        File.is_deleted == False
    ).first()

    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    return file


@router.patch("/{file_id}", response_model=FileSchema)
async def update_file(
    file_id: int,
    file_update: FileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update file metadata.

    - **file_id**: The ID of the file to update
    - **file_update**: The fields to update
    """
    file = db.query(File).filter(
        File.id == file_id,
        File.owner_id == current_user.id,
        File.is_deleted == False
    ).first()

    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    # Update fields
    if file_update.filename is not None:
        file.filename = file_update.filename
    if file_update.is_public is not None:
        file.is_public = file_update.is_public

    db.commit()
    db.refresh(file)

    logger.info(
        f"File updated: {file.filename} by user {current_user.username}")

    return file
