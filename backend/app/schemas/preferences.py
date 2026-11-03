from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ExplanationStyle = Literal["beginner", "technical", "expert"]
AnalysisDepth = Literal["quick", "balanced", "deep"]
PrivacyMode = Literal["offline", "hybrid"]
AgentPermissions = Literal["approval", "automatic"]


class PreferenceUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    explanation_style: ExplanationStyle | None = None
    analysis_depth: AnalysisDepth | None = None
    privacy_mode: PrivacyMode | None = None
    agent_permissions: AgentPermissions | None = None
    external_inference_enabled: bool | None = None
    preferred_local_model: str | None = None
    preferred_external_provider: str | None = None
    max_agent_steps: int | None = Field(default=None, ge=1, le=100)
    max_job_duration_seconds: int | None = Field(default=None, ge=60, le=7200)
    version: int | None = None


class PreferenceResponse(BaseModel):
    explanation_style: ExplanationStyle
    analysis_depth: AnalysisDepth
    privacy_mode: PrivacyMode
    agent_permissions: AgentPermissions
    preferred_local_model: str | None = None
    preferred_external_provider: str | None = None
    external_inference_enabled: bool
    max_agent_steps: int
    max_job_duration_seconds: int
    version: int


class PreferenceAuditRecord(BaseModel):
    id: str
    user_id: str
    action: str
    changed_fields: dict
    created_at: str
