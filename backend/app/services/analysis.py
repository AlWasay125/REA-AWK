from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.config import settings
from app.db.models import Artifact, Case, AnalysisJob, User
from app.db.session import get_db
from app.services.analysis import analyze_artifact

router = APIRouter(tags=["cases"])


@router.post("/cases")
def create_case(
    name: str = Form(...),
    description: str | None = Form(default=None),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown user")
    case = Case(user_id=user.id, name=name, description=description)
    db.add(case)
    db.commit()
    db.refresh(case)
    return {"id": case.id, "name": case.name, "description": case.description}


@router.get("/cases")
def list_cases(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    cases = db.query(Case).filter(Case.user_id == user_id).order_by(Case.created_at.desc()).all()
    return [{"id": c.id, "name": c.name, "description": c.description, "created_at": c.created_at.isoformat()} for c in cases]


@router.get("/cases/{case_id}")
def get_case(case_id: str, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id, Case.user_id == user_id).first()
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return {"id": case.id, "name": case.name, "description": case.description, "created_at": case.created_at.isoformat()}


@router.post("/cases/{case_id}/artifacts")
async def upload_artifact(
    case_id: str,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    case = db.query(Case).filter(Case.id == case_id, Case.user_id == user_id).first()
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty upload")
    if len(content) > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File exceeds configured size")

    sha256 = hashlib.sha256(content).hexdigest()
    file_format = detect_format(content)
    filename = file.filename or "upload.bin"
    storage_dir = Path(settings.artifact_storage_path) / case_id
    storage_dir.mkdir(parents=True, exist_ok=True)
    storage_key = storage_dir / f"{sha256}_{filename}"
    storage_key.write_bytes(content)

    artifact = Artifact(
        case_id=case_id,
        filename=filename,
        sha256=sha256,
        format=file_format,
        storage_key=str(storage_key),
        size_bytes=len(content),
        status="uploaded",
    )
    db.add(artifact)
    db.commit()
    db.refresh(artifact)
    return {"id": artifact.id, "filename": filename, "sha256": sha256, "format": file_format, "size_bytes": len(content)}


@router.post("/artifacts/{artifact_id}/analyze")
def analyze_artifact_endpoint(
    artifact_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    artifact = db.query(Artifact).join(Case).filter(Artifact.id == artifact_id, Case.user_id == user_id).first()
    if artifact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artifact not found")
    job = analyze_artifact(db, artifact)
    return {"job_id": job.id, "status": job.status, "analysis_goal": job.analysis_goal}


@router.get("/jobs/{job_id}")
def get_job(job_id: str, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    job = (
        db.query(AnalysisJob)
        .join(Artifact)
        .join(Case)
        .filter(AnalysisJob.id == job_id, Case.user_id == user_id)
        .first()
    )
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return {
        "id": job.id,
        "artifact_id": job.artifact_id,
        "status": job.status,
        "analysis_goal": job.analysis_goal,
        "error_message": job.error_message,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
    }


def detect_format(content: bytes) -> str:
    if content.startswith(b"MZ"):
        return "PE"
    if content.startswith(b"\x7fELF"):
        return "ELF"
    return "unsupported"
