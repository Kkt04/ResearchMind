"""
Query Service — Routes queries through Cognee recall() and enriches with Claude.
"""

import logging
from openai import OpenAI
from typing import Optional, List
from app.core.config import settings
from app.core.cognee_client import recall_papers
from app.services.paper_service import papers_db

logger = logging.getLogger(__name__)


QUERY_SYSTEM_PROMPT = """You are ResearchMind, an expert research assistant with deep knowledge of academic literature.

You have access to a knowledge graph containing research papers that the user has uploaded.
The memory context below contains retrieved information from this knowledge graph via Cognee.

Your job is to:
1. Answer the user's research question using ONLY information from the retrieved memory context
2. Cite which papers support each claim
3. Highlight connections and patterns across papers
4. Be precise, academic, and structured in your response
5. If the memory context doesn't contain enough info, say so clearly

Always format your response in a clear, structured way suitable for academic research.
When citing papers, use [Paper Title] or [Paper ID] format."""


async def process_query(
    query: str,
    paper_ids: Optional[List[str]] = None,
    mode: str = "full",
) -> dict:
    try:
        mode_query = _build_mode_query(query, mode)
        memory_context = await recall_papers(mode_query, paper_ids)

        papers_context = _build_papers_context(paper_ids)

        if not memory_context or "failed" in memory_context.lower():
            memory_context = papers_context

        full_context = f"""
KNOWLEDGE GRAPH MEMORY (from Cognee recall()):
{memory_context}

PAPER METADATA SUMMARY:
{papers_context}
        """.strip()

        answer = await _synthesize_with_claude(query, full_context, mode)

        sources = _extract_sources(paper_ids)

        return {
            "query": query,
            "answer": answer,
            "sources": sources,
            "mode": mode,
        }

    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        return {
            "query": query,
            "answer": f"I encountered an error while searching the knowledge graph: {str(e)}. Please try again.",
            "sources": [],
            "mode": mode,
        }


def _build_mode_query(query: str, mode: str) -> str:
    mode_prefixes = {
        "gaps": "Research gaps, limitations, and future work: " + query,
        "methods": "Methodology, models, algorithms, and techniques: " + query,
        "datasets": "Datasets, corpora, benchmarks used: " + query,
        "findings": "Key findings, results, accuracy metrics: " + query,
        "full": query,
    }
    return mode_prefixes.get(mode, query)


def _build_papers_context(paper_ids: Optional[List[str]] = None) -> str:
    papers = list(papers_db.values())
    if paper_ids:
        papers = [p for p in papers if p["id"] in paper_ids]

    if not papers:
        return "No papers in collection."

    lines = []
    for p in papers[:20]:
        lines.append(f"""
Paper: {p.get('title', 'Unknown')}
Authors: {p.get('authors', 'N/A')} | Year: {p.get('year', 'N/A')}
Abstract: {(p.get('abstract') or '')[:200]}...
Methodology: {p.get('methodology', 'N/A')}
Dataset: {p.get('dataset', 'N/A')}
Key Findings: {p.get('key_findings', 'N/A')}
Limitations: {p.get('limitations', 'N/A')}
Research Gaps: {p.get('research_gaps', 'N/A')}
Rating: {p.get('rating', 'Unrated')}/5
""".strip())

    return "\n\n---\n\n".join(lines)


async def _synthesize_with_claude(query: str, context: str, mode: str) -> str:
    try:
        client = OpenAI(
            api_key=settings.groq_api_key,
            base_url="https://api.groq.com/openai/v1",
        )

        mode_instructions = {
            "gaps": "Focus specifically on research gaps, limitations, and opportunities for future work.",
            "methods": "Focus on methodologies, models, and technical approaches used across papers.",
            "datasets": "Focus on datasets, their characteristics, sizes, and how they were used.",
            "findings": "Focus on key findings, results, and comparative performance metrics.",
            "full": "Provide a comprehensive answer covering all relevant aspects.",
        }

        user_prompt = f"""Research Question: {query}

{mode_instructions.get(mode, '')}

Retrieved Memory Context:
{context}

Please provide a thorough, well-structured answer citing specific papers where relevant."""

        response = client.chat.completions.create(
            model=settings.llm_model,
            max_tokens=1500,
            messages=[
                {"role": "system", "content": QUERY_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"LLM synthesis failed: {e}")
        return f"Based on your research collection:\n\n{context[:2000]}"


def _extract_sources(paper_ids: Optional[List[str]] = None) -> List[str]:
    papers = list(papers_db.values())
    if paper_ids:
        papers = [p for p in papers if p["id"] in paper_ids]
    return [p.get("title", "Unknown") for p in papers[:10]]


async def chat_with_memory(message: str, history: list) -> dict:
    try:
        memory_context = await recall_papers(message)
        papers_context = _build_papers_context()

        client = OpenAI(
            api_key=settings.groq_api_key,
            base_url="https://api.groq.com/openai/v1",
        )

        system = f"""{QUERY_SYSTEM_PROMPT}

Current Knowledge Graph Context (from Cognee):
{memory_context}

Paper Collection Summary:
{papers_context}"""

        messages = []
        for msg in history[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.insert(0, {"role": "system", "content": system})
        messages.append({"role": "user", "content": message})

        response = client.chat.completions.create(
            model=settings.llm_model,
            max_tokens=1000,
            messages=messages,
        )

        sources = _extract_sources()
        return {
            "response": response.choices[0].message.content,
            "sources_used": sources[:5],
        }

    except Exception as e:
        logger.error(f"Chat failed: {e}")
        return {
            "response": f"Chat error: {str(e)}",
            "sources_used": [],
        }