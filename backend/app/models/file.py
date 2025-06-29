from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    file_type = Column(String(50), nullable=False)  # csv, xlsx, json, etc.
    mime_type = Column(String(100), nullable=True)

    # File processing status
    # uploaded, processing, completed, failed
    status = Column(String(50), default="uploaded")
    processing_started_at = Column(DateTime, nullable=True)
    processing_completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

    # Analysis results
    analysis_metadata = Column(JSON, nullable=True)  # columns, row_count, etc.
    analysis_results = Column(JSON, nullable=True)   # processed data insights

    # File metadata
    column_count = Column(Integer, nullable=True)
    row_count = Column(Integer, nullable=True)
    has_headers = Column(Boolean, default=True)
    encoding = Column(String(50), default="utf-8")
    delimiter = Column(String(10), nullable=True)  # for CSV files

    # Access control
    is_public = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(),
                        onupdate=func.now())
    accessed_at = Column(DateTime, nullable=True)

    # Foreign keys
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    owner = relationship("User", back_populates="files")

    def __repr__(self):
        return f"<File(id={self.id}, filename='{self.filename}', owner_id={self.owner_id})>"

    @property
    def file_size_mb(self) -> float:
        """Get file size in MB"""
        return self.file_size / (1024 * 1024) if self.file_size else 0

    @property
    def file_extension(self) -> str:
        """Get file extension"""
        return self.filename.split('.')[-1].lower() if '.' in self.filename else ''

    @property
    def is_processed(self) -> bool:
        """Check if file has been processed"""
        return self.status == "completed"

    def update_processing_status(self, status: str, error_message: str = None):
        """Update file processing status"""
        self.status = status
        if status == "processing":
            self.processing_started_at = func.now()
        elif status in ["completed", "failed"]:
            self.processing_completed_at = func.now()
        if error_message:
            self.error_message = error_message

    def set_analysis_data(self, metadata: dict, results: dict = None):
        """Set analysis metadata and results"""
        self.analysis_metadata = metadata
        if results:
            self.analysis_results = results

        # Extract common metadata
        if 'columns' in metadata:
            self.column_count = len(metadata['columns'])
        if 'row_count' in metadata:
            self.row_count = metadata['row_count']
