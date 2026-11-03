from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.db.models import PreferenceAuditLog
from app.db.session import get_db
from app.schemas.preferences import PreferenceUpdate, PreferenceResponse
from app.services.preferences import (
    ensure_preferences,
    normalize_preferences,
    preferences_to_response,
)

router = APIRouter(tags=["preferences"])


@router.get("/preferences", response_model=PreferenceResponse)
def read_preferences(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)) -> PreferenceResponse:
    pref = ensure_preferences(db, user_id)
    return PreferenceResponse(**preferences_to_response(pref))


@router.patch("/preferences", response_model=PreferenceResponse)
def update_preferences(
    payload: PreferenceUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> PreferenceResponse:
    pref = ensure_preferences(db, user_id)
    data = payload.model_dump(exclude_unset=True)
    if "version" in data:
        if data["version"] is not None and data["version"] != pref.version:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Preference version conflict")
        data.pop("version")
    if not data:
        return PreferenceResponse(**preferences_to_response(pref))
    data = normalize_preferences(data)
    for key, value in data.items():
        setattr(pref, key, value)
    if pref.version is None:
        pref.version = 1
    pref.version += 1
    db.add(pref)
    audit = PreferenceAuditLog(
        user_id=user_id,
        action="update",
        changed_fields=data,
    )
    db.add(audit)
    db.commit()
    db.refresh(pref)
    return PreferenceResponse(**preferences_to_response(pref))


@router.put("/preferences/reset", response_model=PreferenceResponse)
def reset_preferences(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)) -> PreferenceResponse:
    pref = ensure_preferences(db, user_id)
    for key, value in {
        "explanation_style": "beginner",
        "analysis_depth": "balanced",
        "privacy_mode": "hybrid",
        "agent_permissions": "automatic",
        "preferred_local_model": None,
        "preferred_external_provider": None,
        "external_inference_enabled": False,
        "max_agent_steps": 20,
        "max_job_duration_seconds": 1800,
    }.items():
        setattr(pref, key, value)
    pref.version += 1
    db.add(pref)
    db.add(PreferenceAuditLog(user_id=user_id, action="reset", changed_fields={"reset": True}))
    db.commit()
    db.refresh(pref)
    return PreferenceResponse(**preferences_to_response(pref))


@router.get("/preferences/audit")
def read_preferences_audit(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    records = db.query(PreferenceAuditLog).filter(PreferenceAuditLog.user_id == user_id).order_by(PreferenceAuditLog.created_at.desc()).all()
    return [{
        "id": record.id,
        "user_id": record.user_id,
        "action": record.action,
        "changed_fields": record.changed_fields,
        "created_at": record.created_at.isoformat() if record.created_at else None,
    } for record in records]


@router.get("/preferences/options")
def read_preferences_options() -> dict[str, list[str] | dict[str, str]]:
    return {
        "explanation_style": ["beginner", "technical", "expert"],
        "analysis_depth": ["quick", "balanced", "deep"],
        "privacy_mode": ["offline", "hybrid"],
        "agent_permissions": ["approval", "automatic"],
        "descriptions": {
            "beginner": "Explain concepts in plain language, define unfamiliar terms, and keep technical evidence available.",
            "balanced": "Run standard static analysis and investigate relevant functions and call chains without exhaustively analyzing every function.",
            "hybrid": "Prefer local analysis. External inference remains disabled until a provider is configured and authorization is explicit.",
            "automatic": "Allow predefined, bounded static-analysis tasks to run without individual approval.",
        },
    }
