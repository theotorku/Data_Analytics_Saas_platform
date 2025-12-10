from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


# Base file schema
class FileBase(BaseModel):
    filename: str
    file_type: str
    is_public: bool = False


# File upload response
class FileUpload(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_size: int
    file_type: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# File response schema
class File(FileBase):
    id: int
    original_filename: str
    file_path: str
    file_size: int
    mime_type: Optional[str] = None
    status: str
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    column_count: Optional[int] = None
    row_count: Optional[int] = None
    has_headers: bool = True
    encoding: str = "utf-8"
    delimiter: Optional[str] = None
    is_deleted: bool = False
    created_at: datetime
    updated_at: datetime
    accessed_at: Optional[datetime] = None
    owner_id: int

    class Config:
        from_attributes = True


# File with analysis results
class FileWithAnalysis(File):
    analysis_metadata: Optional[Dict[str, Any]] = None
    analysis_results: Optional[Dict[str, Any]] = None

    @property
    def file_size_mb(self) -> float:
        return self.file_size / (1024 * 1024) if self.file_size else 0.0


# File list response
class FileList(BaseModel):
    files: List[File]
    total: int
    page: int
    page_size: int
    total_pages: int


# File metadata
class FileMetadata(BaseModel):
    id: int
    filename: str
    file_size: int
    file_type: str
    column_count: Optional[int] = None
    row_count: Optional[int] = None
    has_headers: bool = True
    encoding: str = "utf-8"
    delimiter: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# File update schema
class FileUpdate(BaseModel):
    filename: Optional[str] = None
    is_public: Optional[bool] = None

    @validator('filename')
    def validate_filename(cls, v):
        if v is not None and len(v) < 1:
            raise ValueError('Filename cannot be empty')
        return v
