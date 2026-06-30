from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class PaperStatus(str, Enum):
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class PaperSource(str, Enum):
    PDF = "pdf"
    ARXIV = "arxiv"
    URL = "url"
    TEXT = "text"


class PaperMetadata(BaseModel):
    title: str
    authors: Optional[str] = None
    year: Optional[str] = None
    abstract: Optional[str] = None
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    source_url: Optional[str] = None
    methodology: Optional[str] = None
    dataset: Optional[str] = None
    key_findings: Optional[str] = None
    limitations: Optional[str] = None
    research_gaps: Optional[str] = None
    tags: Optional[List[str]] = []


class PaperCreate(BaseModel):
    source: PaperSource
    content: Optional[str] = None
    arxiv_id: Optional[str] = None
    url: Optional[str] = None
    metadata: Optional[PaperMetadata] = None


class PaperResponse(BaseModel):
    id: str
    title: str
    authors: Optional[str] = None
    year: Optional[str] = None
    abstract: Optional[str] = None
    source: PaperSource
    status: PaperStatus
    rating: Optional[int] = None
    tags: Optional[List[str]] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaperListResponse(BaseModel):
    papers: List[PaperResponse]
    total: int


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=1000)
    paper_ids: Optional[List[str]] = None
    mode: Optional[str] = "full"


class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: Optional[List[str]] = []
    mode: str


class FeedbackRequest(BaseModel):
    paper_id: str
    rating: int = Field(..., ge=1, le=5)
    feedback: str = Field(..., min_length=1, max_length=2000)


class FeedbackResponse(BaseModel):
    success: bool
    message: str


class ReviewRequest(BaseModel):
    title: Optional[str] = "Literature Review"
    focus_area: Optional[str] = ""
    paper_ids: Optional[List[str]] = None


class ReviewSection(BaseModel):
    heading: str
    content: str


class ReviewResponse(BaseModel):
    title: str
    sections: List[ReviewSection]
    total_papers: int
    generated_at: datetime


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    response: str
    sources_used: Optional[List[str]] = []