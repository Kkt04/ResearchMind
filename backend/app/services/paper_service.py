"""
Paper Service — Handles ingestion of papers from multiple sources.
Extracts text, metadata, and feeds into Cognee memory graph.
"""

import uuid
import logging
import httpx
import re
from typing import Optional, Tuple
from datetime import datetime

try:
    import PyPDF2
    import io
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

from app.core.config import settings
from app.core.cognee_client import remember_paper
from app.models.schemas import PaperSource

logger = logging.getLogger(__name__)

papers_db: dict = {}


async def extract_arxiv_paper(arxiv_id: str) -> Tuple[str, dict]:
    clean_id = arxiv_id.replace("arxiv:", "").strip()
    if "abs/" in clean_id:
        clean_id = clean_id.split("abs/")[-1]

    api_url = f"https://export.arxiv.org/abs/{clean_id}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(api_url)
        if response.status_code != 200:
            raise ValueError(f"arXiv paper not found: {clean_id}")

        html = response.text

        title_match = re.search(r'<h1 class="title[^"]*"[^>]*>(?:Title:)?\s*(.*?)</h1>', html, re.DOTALL)
        title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip() if title_match else f"arXiv:{clean_id}"

        authors_match = re.search(r'<div class="authors">(.*?)</div>', html, re.DOTALL)
        authors = re.sub(r'<[^>]+>', '', authors_match.group(1)).strip() if authors_match else ""
        authors = re.sub(r'\s+', ' ', authors)

        abstract_match = re.search(r'<blockquote class="abstract[^"]*">(.*?)</blockquote>', html, re.DOTALL)
        abstract = re.sub(r'<[^>]+>', '', abstract_match.group(1)).strip() if abstract_match else ""
        abstract = abstract.replace("Abstract:", "").strip()

        date_match = re.search(r'Submitted on (\d+ \w+ \d{4})', html)
        year = date_match.group(1).split()[-1] if date_match else str(datetime.now().year)

        metadata = {
            "title": title,
            "authors": authors,
            "year": year,
            "abstract": abstract,
            "arxiv_id": clean_id,
            "source_url": f"https://arxiv.org/abs/{clean_id}",
        }

        content = f"Title: {title}\n\nAuthors: {authors}\n\nAbstract: {abstract}"
        return content, metadata


async def extract_pdf_content(file_bytes: bytes) -> str:
    if not PDF_AVAILABLE:
        return "PDF extraction not available"

    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text_parts = []
        for page_num, page in enumerate(reader.pages[:50]):
            text = page.extract_text()
            if text:
                text_parts.append(text)
        return "\n\n".join(text_parts)
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        return ""


async def extract_metadata_from_text(title: str, content: str) -> dict:
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

        prompt = f"""Analyze this research paper and extract structured metadata.
Return a JSON object with these fields (use null if not found):
- title: paper title
- authors: author names as a string
- year: publication year
- abstract: abstract text (max 500 chars)
- methodology: main methods/models used (max 200 chars)
- dataset: datasets used (max 200 chars)  
- key_findings: main results/findings (max 300 chars)
- limitations: stated limitations (max 200 chars)
- research_gaps: identified gaps/future work (max 200 chars)

Paper title hint: {title}
Paper content (first 3000 chars):
{content[:3000]}

Return ONLY valid JSON, no explanation."""

        response = client.messages.create(
            model=settings.llm_model,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )

        import json
        text = response.content[0].text.strip()
        text = re.sub(r'```json\s*|\s*```', '', text).strip()
        return json.loads(text)

    except Exception as e:
        logger.error(f"Metadata extraction failed: {e}")
        return {"title": title}


async def ingest_paper(
    source: PaperSource,
    content: Optional[str] = None,
    arxiv_id: Optional[str] = None,
    url: Optional[str] = None,
    file_bytes: Optional[bytes] = None,
    filename: Optional[str] = None,
    user_metadata: Optional[dict] = None,
) -> dict:
    paper_id = str(uuid.uuid4())
    extracted_content = ""
    metadata = user_metadata or {}

    try:
        if source == PaperSource.ARXIV and arxiv_id:
            extracted_content, arxiv_meta = await extract_arxiv_paper(arxiv_id)
            metadata = {**arxiv_meta, **metadata}

        elif source == PaperSource.PDF and file_bytes:
            extracted_content = await extract_pdf_content(file_bytes)
            if not metadata.get("title"):
                metadata["title"] = filename or "Uploaded Paper"

        elif source == PaperSource.URL and url:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(url)
                extracted_content = resp.text[:10000]
            if not metadata.get("title"):
                metadata["title"] = url

        elif source == PaperSource.TEXT and content:
            extracted_content = content
            if not metadata.get("title"):
                metadata["title"] = content[:80] + "..."

        if extracted_content and not metadata.get("methodology"):
            enriched = await extract_metadata_from_text(
                metadata.get("title", ""), extracted_content
            )
            for key, val in enriched.items():
                if val and not metadata.get(key):
                    metadata[key] = val

        success = await remember_paper(
            paper_id=paper_id,
            content=extracted_content or metadata.get("abstract", ""),
            metadata=metadata,
        )

        paper_record = {
            "id": paper_id,
            "title": metadata.get("title", "Untitled"),
            "authors": metadata.get("authors"),
            "year": metadata.get("year"),
            "abstract": metadata.get("abstract"),
            "methodology": metadata.get("methodology"),
            "dataset": metadata.get("dataset"),
            "key_findings": metadata.get("key_findings"),
            "limitations": metadata.get("limitations"),
            "research_gaps": metadata.get("research_gaps"),
            "source": source,
            "source_url": metadata.get("source_url") or url,
            "arxiv_id": arxiv_id,
            "status": "ready" if success else "processing",
            "rating": None,
            "tags": metadata.get("tags", []),
            "created_at": datetime.now().isoformat(),
            "updated_at": None,
            "cognee_stored": success,
        }

        papers_db[paper_id] = paper_record
        logger.info(f"✅ Paper ingested: {paper_record['title']} [{paper_id}]")
        return paper_record

    except Exception as e:
        logger.error(f"❌ Paper ingestion failed: {e}")
        paper_record = {
            "id": paper_id,
            "title": metadata.get("title", "Failed Paper"),
            "source": source,
            "status": "failed",
            "error": str(e),
            "created_at": datetime.now().isoformat(),
        }
        papers_db[paper_id] = paper_record
        return paper_record


def get_all_papers() -> list:
    return list(papers_db.values())


def get_paper_by_id(paper_id: str) -> Optional[dict]:
    return papers_db.get(paper_id)


def delete_paper_record(paper_id: str) -> bool:
    if paper_id in papers_db:
        del papers_db[paper_id]
        return True
    return False


def update_paper_rating(paper_id: str, rating: int, feedback: str) -> bool:
    if paper_id in papers_db:
        papers_db[paper_id]["rating"] = rating
        papers_db[paper_id]["feedback"] = feedback
        papers_db[paper_id]["updated_at"] = datetime.now().isoformat()
        return True
    return False