from datetime import datetime

from pydantic import BaseModel, Field


class ScanCreate(BaseModel):
    target: str = Field(min_length=3, max_length=255)
    authorized: bool = Field(
        default=False,
        description="User confirms they own the target or have explicit permission to scan it.",
    )


class FindingOut(BaseModel):
    id: int
    title: str
    severity: str
    category: str
    evidence: str | None = None
    recommendation: str | None = None
    details: dict = {}

    model_config = {"from_attributes": True}


class ScanOut(BaseModel):
    id: str
    target: str
    normalized_target: str
    status: str
    score: int
    summary: str | None = None
    error: str | None = None
    scanner_meta: dict = {}
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ScanResult(ScanOut):
    findings: list[FindingOut] = []


class HistoryItem(BaseModel):
    id: str
    target: str
    status: str
    score: int
    findings_count: int
    created_at: datetime

