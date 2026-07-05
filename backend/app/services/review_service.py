"""
Review Service — Generates structured literature review drafts.
"""

import logging
from openai import OpenAI
from datetime import datetime
from typing import Optional, List
from app.core.config import settings
from app.core.cognee_client import recall_for_review
from app.services.paper_service import papers_db

logger = logging.getLogger(__name__)


REVIEW_SYSTEM_PROMPT = """You are an expert academic writer specializing in literature reviews.
You will be given information about multiple research papers from a knowledge graph.

Write a structured, academic literature review with the following sections:
1. Introduction & Scope
2. Methodology Landscape (grouped by approach type)
3. Datasets & Evaluation Benchmarks
4. Key Findings & Comparative Analysis
5. Common Limitations & Challenges
6. Research Gaps & Future Directions
7. Conclusion

Rules:
- Write in formal academic prose
- Cite papers naturally: (AuthorLastName et al., Year) or [Paper Title]
- Group related papers together, don't just list them sequentially
- Identify patterns, contradictions, and trends across papers
- Be specific about metrics, numbers, and findings where available
- Each section should be substantive (3-5 paragraphs minimum)
- Highlight the most credible papers (high user ratings) more prominently"""


async def generate_literature_review(
    title: str = "Literature Review",
    focus_area: str = "",
    paper_ids: Optional[List[str]] = None,
) -> dict:
    try:
        all_papers = list(papers_db.values())
        if paper_ids:
            relevant_papers = [p for p in all_papers if p["id"] in paper_ids]
        else:
            relevant_papers = [p for p in all_papers if p.get("status") != "failed"]

        if not relevant_papers:
            return {
                "title": title,
                "sections": [{"heading": "Error", "content": "No papers available for review generation. Please add papers first."}],
                "total_papers": 0,
                "generated_at": datetime.now().isoformat(),
            }

        memory_context = await recall_for_review(focus_area)
        papers_summary = _build_comprehensive_summary(relevant_papers)

        sections = await _generate_review_sections(
            title=title,
            focus_area=focus_area,
            memory_context=memory_context,
            papers_summary=papers_summary,
            paper_count=len(relevant_papers),
        )

        return {
            "title": title,
            "sections": sections,
            "total_papers": len(relevant_papers),
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Review generation failed: {e}")
        return {
            "title": title,
            "sections": [{"heading": "Generation Error", "content": str(e)}],
            "total_papers": 0,
            "generated_at": datetime.now().isoformat(),
        }


def _build_comprehensive_summary(papers: list) -> str:
    lines = [f"TOTAL PAPERS: {len(papers)}\n"]
    sorted_papers = sorted(papers, key=lambda p: p.get("rating") or 0, reverse=True)

    for i, p in enumerate(sorted_papers, 1):
        lines.append(f"""
PAPER {i}: {p.get('title', 'Unknown')}
Authors: {p.get('authors', 'Unknown')} ({p.get('year', 'N/A')})
Abstract: {(p.get('abstract') or 'Not available')[:400]}
Methodology/Models: {p.get('methodology', 'Not specified')}
Dataset Used: {p.get('dataset', 'Not specified')}
Key Findings: {p.get('key_findings', 'Not specified')}
Limitations: {p.get('limitations', 'Not specified')}
Research Gaps: {p.get('research_gaps', 'Not specified')}
User Rating: {p.get('rating', 'Unrated')}/5
User Feedback: {p.get('feedback', 'None')}
""".strip())

    return "\n\n".join(lines)


async def _generate_review_sections(
    title: str,
    focus_area: str,
    memory_context: str,
    papers_summary: str,
    paper_count: int,
) -> list:
    try:
        client = OpenAI(
            api_key=settings.groq_api_key,
            base_url="https://api.groq.com/openai/v1",
        )

        focus_note = f"\nFocus Area: {focus_area}" if focus_area else ""
        user_prompt = f"""Generate a comprehensive literature review titled: "{title}"
{focus_note}
Number of papers to synthesize: {paper_count}

KNOWLEDGE GRAPH CONTEXT (from Cognee memory recall):
{memory_context[:3000] if memory_context else 'Not available'}

DETAILED PAPER SUMMARIES:
{papers_summary[:5000]}

Write the complete literature review with all 7 sections.
Format your response as:

## Section Title
[content]

## Next Section Title
[content]

Make each section substantive and academically rigorous."""

        response = client.chat.completions.create(
            model=settings.llm_model,
            max_tokens=4000,
            messages=[
                {"role": "system", "content": REVIEW_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )

        raw_text = response.choices[0].message.content
        sections = _parse_sections(raw_text)

        return sections

    except Exception as e:
        logger.error(f"LLM review generation failed: {e}")
        return _fallback_review(papers_summary)


def _parse_sections(raw_text: str) -> list:
    import re
    sections = []
    parts = re.split(r'\n##\s+', raw_text)

    for part in parts:
        if not part.strip():
            continue
        lines = part.strip().split('\n', 1)
        heading = lines[0].strip().lstrip('#').strip()
        content = lines[1].strip() if len(lines) > 1 else ""
        if heading and content:
            sections.append({"heading": heading, "content": content})

    if not sections:
        sections = [{"heading": "Literature Review", "content": raw_text}]

    return sections


def _fallback_review(papers_summary: str) -> list:
    return [
        {
            "heading": "Overview",
            "content": "Literature review generated from your paper collection. Please ensure Claude API is configured for a full AI-generated review."
        },
        {
            "heading": "Paper Collection",
            "content": papers_summary[:2000]
        }
    ]