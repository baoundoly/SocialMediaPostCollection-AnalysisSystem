from pydantic import BaseModel
from typing import Optional
from datetime import date

class ReportRequest(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    platform_id: Optional[int] = None
    format: Optional[str] = "json"  # json, csv, excel, pdf
