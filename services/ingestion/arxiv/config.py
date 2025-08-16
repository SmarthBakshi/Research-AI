from pydantic import BaseModel, Field
from datetime import datetime, timedelta

class ArxivConfig(BaseModel):
    base_url: str = "http://export.arxiv.org/api/query"
    categories: list[str] = Field(default_factory=lambda: ["cs.AI", "cs.CL"])
    max_results: int = 100
    per_request: int = 50
    delay_seconds: float = 3.0  # for rate-limiting
    retries: int = 3
    retry_backoff: float = 2.0  # exponential backoff
    start_date: datetime = Field(default_factory=lambda: datetime.utcnow() - timedelta(days=7))
