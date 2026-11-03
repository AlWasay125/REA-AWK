from __future__ import annotations

from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import User, UserPreference

DEFAULT_PREFERENCES = {
    "explanation_style": "beginner",
    "analysis_depth": "balanced",
    "privacy_mode": "hybrid",
    "agent_permissions": "automatic",
    "preferred_local_model": None,
    "preferred_external_provider": None,
    "external_inference_enabled": False,
    "max_agent_steps": 20,
    "max_job_duration_seconds": 1800,
    "version": 1,
}


def ensure_user(db: Session, user_id: str) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        user = User(id=user_id, email=f"user-{user_id[:8]}@local.test", name="Local User")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def ensure_preferences(db: Session, user_id: str) -> UserPreference:
    ensure_user(db, user_id)
    pref = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
    if pref is None:
        pref = UserPreference(user_id=user_id, **{k: v for k, v in DEFAULT_PREFERENCES.items() if k != "version"})
        db.add(pref)
        db.commit()
        db.refresh(pref)
    return pref


def normalize_preferences(data: dict[str, Any]) -> dict[str, Any]:
    if data.get("privacy_mode") == "offline":
        data["external_inference_enabled"] = False
    if data.get("external_inference_enabled") and data.get("privacy_mode") == "offline":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Offline privacy mode disables external inference.")
    return data


def preferences_to_response(pref: UserPreference) -> dict[str, Any]:
    return {
        "explanation_style": pref.explanation_style,
        "analysis_depth": pref.analysis_depth,
        "privacy_mode": pref.privacy_mode,
        "agent_permissions": pref.agent_permissions,
        "preferred_local_model": pref.preferred_local_model,
        "preferred_external_provider": pref.preferred_external_provider,
        "external_inference_enabled": pref.external_inference_enabled,
        "max_agent_steps": pref.max_agent_steps,
        "max_job_duration_seconds": pref.max_job_duration_seconds,
        "version": pref.version,
    }
