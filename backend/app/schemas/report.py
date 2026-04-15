from datetime import datetime

from pydantic import BaseModel, Field


class MonthlyReportGenerateRequest(BaseModel):
    scope_type: str = Field(pattern="^(merchant|program)$")
    scope_id: str = Field(min_length=1)
    year: int = Field(ge=2000, le=2100)
    month: int = Field(ge=1, le=12)


class MonthlyReportGenerateResponse(BaseModel):
    report_id: str
    job_id: str
    status: str


class ReportListItemResponse(BaseModel):
    report_id: str
    scope_type: str
    scope_id: str
    year: int
    month: int
    status: str
    created_at: datetime


class ReportListResponse(BaseModel):
    items: list[ReportListItemResponse]
