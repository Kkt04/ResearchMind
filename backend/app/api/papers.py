from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
import logging

from app.models.schemas import PaperSource, PaperResponse, PaperListResponse
from app.services import paper_service
from app.core.cognee_client import forget_paper

router = APIRouter(prefix="/papers", tags=["papers"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=PaperListResponse)
async def list_papers():
    papers = paper_service.get_all_papers()
    return {"papers": papers, "total": len(papers)}


@router.get("/{paper_id}")
async def get_paper(paper_id: str):
    paper = paper_service.get_paper_by_id(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper


@router.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    authors: Optional[str] = Form(None),
    year: Optional[str] = Form(None),
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    file_bytes = await file.read()
    if len(file_bytes) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 20MB)")

    metadata = {}
    if title: metadata["title"] = title
    if authors: metadata["authors"] = authors
    if year: metadata["year"] = year

    paper = await paper_service.ingest_paper(
        source=PaperSource.PDF,
        file_bytes=file_bytes,
        filename=file.filename,
        user_metadata=metadata,
    )
    return paper


@router.post("/arxiv")
async def add_arxiv_paper(payload: dict):
    arxiv_id = payload.get("arxiv_id", "").strip()
    if not arxiv_id:
        raise HTTPException(status_code=400, detail="arxiv_id is required")

    paper = await paper_service.ingest_paper(
        source=PaperSource.ARXIV,
        arxiv_id=arxiv_id,
    )
    return paper


@router.post("/text")
async def add_text_paper(payload: dict):
    content = payload.get("content", "").strip()
    title = payload.get("title", "")

    if not content:
        raise HTTPException(status_code=400, detail="content is required")

    paper = await paper_service.ingest_paper(
        source=PaperSource.TEXT,
        content=content,
        user_metadata={"title": title} if title else None,
    )
    return paper


@router.delete("/{paper_id}")
async def delete_paper(paper_id: str):
    paper = paper_service.get_paper_by_id(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    await forget_paper(paper_id)
    paper_service.delete_paper_record(paper_id)

    return {"success": True, "message": f"Paper '{paper.get('title')}' removed from knowledge graph"}