from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ShootMissionInput(BaseModel):
    """Raw shoot mission input from user."""
    location: str = Field(..., description="Shoot location (e.g. 'Downtown Los Angeles')")
    date: str = Field(..., description="Shoot date or timing (e.g. 'Tomorrow', '2026-09-12')")
    description: str = Field(..., description="Detailed description and operational requirements")


class SearchEvidenceItem(BaseModel):
    """Genuine evidence item retrieved via Parallel Search."""
    title: str = Field(..., description="Page or document title")
    url: str = Field(..., description="Authentic source URL")
    excerpts: List[str] = Field(default_factory=list, description="LLM-optimized excerpts from source")
    query: str = Field(..., description="Search query that surfaced this evidence")
    search_id: Optional[str] = Field(None, description="Parallel Search ID")


class RegulatoryFinding(BaseModel):
    """Structured regulatory and logistical finding extracted from live search evidence."""
    category: str = Field(..., description="Category (e.g. 'road_control', 'drone_uas', 'generator_noise')")
    requirement: str = Field(..., description="Specific requirement (e.g. 'permit_required', 'night_waiver')")
    description: str = Field(..., description="Description of the requirement found in evidence")
    mandatory: bool = Field(True, description="Whether this is mandatory for legal shoot operation")
    approval_status: str = Field("not_confirmed", description="'approved', 'not_confirmed', 'unobtainable', 'not_required'")
    required_lead_time_hours: Optional[float] = Field(None, description="Established lead time in hours (if found in evidence)")
    remaining_time_hours: Optional[float] = Field(None, description="Estimated hours remaining until shoot")
    source_urls: List[str] = Field(default_factory=list, description="Real source URLs establishing this fact")
    details: Optional[str] = Field(None, description="Additional context or notes from evidence")


class BlockerItem(BaseModel):
    """Critical hard stop preventing safe or legal shoot operations."""
    title: str = Field(..., description="Blocker title")
    reason: str = Field(..., description="Detailed explanation of the blocker")
    category: str = Field(..., description="Risk domain")
    required_lead_time_hours: Optional[float] = Field(None, description="Required notice/permit lead time in hours")
    remaining_time_hours: Optional[float] = Field(None, description="Remaining hours before call time")
    sources: List[str] = Field(default_factory=list, description="Direct source URLs")


class RiskItem(BaseModel):
    """Operational or regulatory hazard requiring active mitigation."""
    title: str = Field(..., description="Risk title")
    severity: str = Field(..., description="Severity level: 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'")
    category: str = Field(..., description="Risk category")
    description: str = Field(..., description="Explanation of hazard")
    mitigation: str = Field(..., description="Recommended mitigation strategy")
    sources: List[str] = Field(default_factory=list, description="Direct source URLs")


class ConditionItem(BaseModel):
    """Condition that must be fulfilled before production clearance is granted."""
    condition: str = Field(..., description="Specific prerequisite condition")
    action_required: str = Field(..., description="Action needed to satisfy condition")
    sources: List[str] = Field(default_factory=list, description="Direct source URLs")


class ReadinessAssessment(BaseModel):
    """Complete production-readiness assessment dossier returned to UI."""
    status: str = Field(..., description="'GO', 'CONDITIONAL GO', or 'NO-GO'")
    readiness_score: int = Field(..., description="Readiness score from 0 to 100")
    summary: str = Field(..., description="Executive summary and rationale")
    mission_specs: Dict[str, Any] = Field(default_factory=dict, description="Parsed shoot specifications")
    blockers: List[BlockerItem] = Field(default_factory=list, description="List of hard blocking constraints")
    risks: List[RiskItem] = Field(default_factory=list, description="Identified operational risks")
    conditions: List[ConditionItem] = Field(default_factory=list, description="Mandatory conditions for GO")
    recommended_actions: List[str] = Field(default_factory=list, description="Prioritized operational checklist")
    findings: List[RegulatoryFinding] = Field(default_factory=list, description="Extracted factual findings")
    evidence: List[SearchEvidenceItem] = Field(default_factory=list, description="Retained search evidence with real URLs")
