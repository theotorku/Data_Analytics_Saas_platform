from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import pandas as pd
import logging
from pathlib import Path

from app.core.database import get_db
from app.models.user import User
from app.models.file import File
from app.api.deps import get_current_active_user

router = APIRouter()
logger = logging.getLogger(__name__)


def analyze_csv_file(file_path: str) -> Dict[str, Any]:
    """
    Analyze a CSV file and extract metadata and insights.

    Args:
        file_path: Path to the CSV file

    Returns:
        Dict containing analysis results
    """
    try:
        # Read CSV file
        df = pd.read_csv(file_path)

        # Basic metadata
        metadata = {
            "columns": list(df.columns),
            "row_count": len(df),
            "column_count": len(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "memory_usage": int(df.memory_usage(deep=True).sum())
        }

        # Statistical analysis
        results = {
            "summary_statistics": {},
            "missing_values": {},
            "unique_values": {},
            "data_types": {}
        }

        # Analyze each column
        for col in df.columns:
            # Missing values
            results["missing_values"][col] = int(df[col].isna().sum())

            # Unique values
            results["unique_values"][col] = int(df[col].nunique())

            # Data type
            results["data_types"][col] = str(df[col].dtype)

            # Summary statistics for numeric columns
            if pd.api.types.is_numeric_dtype(df[col]):
                results["summary_statistics"][col] = {
                    "mean": float(df[col].mean()) if not df[col].isna().all() else None,
                    "median": float(df[col].median()) if not df[col].isna().all() else None,
                    "std": float(df[col].std()) if not df[col].isna().all() else None,
                    "min": float(df[col].min()) if not df[col].isna().all() else None,
                    "max": float(df[col].max()) if not df[col].isna().all() else None,
                    "q25": float(df[col].quantile(0.25)) if not df[col].isna().all() else None,
                    "q75": float(df[col].quantile(0.75)) if not df[col].isna().all() else None
                }

        return {"metadata": metadata, "results": results}

    except Exception as e:
        logger.error(f"Error analyzing CSV file: {e}")
        raise


def analyze_excel_file(file_path: str) -> Dict[str, Any]:
    """
    Analyze an Excel file and extract metadata and insights.

    Args:
        file_path: Path to the Excel file

    Returns:
        Dict containing analysis results
    """
    try:
        # Read Excel file (first sheet)
        df = pd.read_excel(file_path, sheet_name=0)

        # Use same analysis as CSV
        return analyze_csv_file(file_path)

    except Exception as e:
        logger.error(f"Error analyzing Excel file: {e}")
        raise


def analyze_json_file(file_path: str) -> Dict[str, Any]:
    """
    Analyze a JSON file and extract metadata and insights.

    Args:
        file_path: Path to the JSON file

    Returns:
        Dict containing analysis results
    """
    try:
        # Read JSON file
        df = pd.read_json(file_path)

        # Use same analysis as CSV
        metadata = {
            "columns": list(df.columns),
            "row_count": len(df),
            "column_count": len(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()}
        }

        results = {
            "summary_statistics": {},
            "missing_values": {},
            "unique_values": {}
        }

        for col in df.columns:
            results["missing_values"][col] = int(df[col].isna().sum())
            results["unique_values"][col] = int(df[col].nunique())

        return {"metadata": metadata, "results": results}

    except Exception as e:
        logger.error(f"Error analyzing JSON file: {e}")
        raise


async def process_file_analysis(file_id: int, db: Session):
    """
    Background task to process file analysis.

    Args:
        file_id: The ID of the file to analyze
        db: Database session
    """
    file = db.query(File).filter(File.id == file_id).first()

    if not file:
        logger.error(f"File not found for analysis: {file_id}")
        return

    try:
        # Update status to processing
        file.status = "processing"
        from sqlalchemy.sql import func
        file.processing_started_at = func.now()
        db.commit()

        # Analyze based on file type
        if file.file_type == "csv":
            analysis = analyze_csv_file(file.file_path)
        elif file.file_type in ["xlsx", "xls"]:
            analysis = analyze_excel_file(file.file_path)
        elif file.file_type == "json":
            analysis = analyze_json_file(file.file_path)
        else:
            raise ValueError(f"Unsupported file type: {file.file_type}")

        # Save analysis results
        file.set_analysis_data(
            metadata=analysis["metadata"],
            results=analysis["results"]
        )
        file.status = "completed"
        file.processing_completed_at = func.now()

        # Update user analysis count
        user = db.query(User).filter(User.id == file.owner_id).first()
        if user:
            user.increment_analysis_count()

        db.commit()

        logger.info(f"File analysis completed: {file.filename}")

    except Exception as e:
        logger.error(f"Error processing file analysis: {e}")
        file.status = "failed"
        file.error_message = str(e)
        file.processing_completed_at = func.now()
        db.commit()


@router.post("/analyze/{file_id}")
async def analyze_file(
    file_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Trigger analysis for an uploaded file.

    - **file_id**: The ID of the file to analyze
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

    if file.status == "processing":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is already being processed"
        )

    # Add analysis task to background
    background_tasks.add_task(process_file_analysis, file_id, db)

    return {
        "message": "File analysis started",
        "file_id": file_id,
        "status": "processing"
    }


@router.get("/results/{file_id}")
async def get_analysis_results(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get analysis results for a file.

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

    if file.status == "uploaded":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File has not been analyzed yet. Please trigger analysis first."
        )

    if file.status == "processing":
        return {
            "status": "processing",
            "message": "Analysis is still in progress"
        }

    if file.status == "failed":
        return {
            "status": "failed",
            "error": file.error_message
        }

    return {
        "status": "completed",
        "file_id": file.id,
        "filename": file.original_filename,
        "metadata": file.analysis_metadata,
        "results": file.analysis_results,
        "processed_at": file.processing_completed_at
    }
