"""
Cognee Client — Core Memory Layer for ResearchMind
Wraps all 4 Cognee lifecycle APIs:
  - remember()  → ingest paper into knowledge graph
  - recall()    → query across papers with graph traversal
  - improve()   → update node weights from user feedback
  - forget()    → surgically remove paper from graph
"""

import cognee
import json
import logging
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


async def init_cognee():
    """Initialize Cognee with API keys and config."""
    try:
        cognee.config.set_llm_config({
            "provider": "anthropic",
            "model": settings.llm_model,
            "api_key": settings.anthropic_api_key,
        })

        if settings.cognee_api_key:
            cognee.config.set_vector_db_config({
                "provider": "cognee_cloud",
                "api_key": settings.cognee_api_key,
            })

        logger.info("✅ Cognee initialized successfully")
    except Exception as e:
        logger.warning(f"Cognee init warning (will use defaults): {e}")


async def remember_paper(paper_id: str, content: str, metadata: dict) -> bool:
    """
    Cognee remember() — Ingest paper into permanent knowledge graph.
    Structures raw text into nodes: title, methodology, dataset, findings, gaps.
    """
    try:
        structured_content = f"""
PAPER_ID: {paper_id}
TITLE: {metadata.get('title', 'Unknown')}
AUTHORS: {metadata.get('authors', 'Unknown')}
YEAR: {metadata.get('year', 'Unknown')}
ABSTRACT: {metadata.get('abstract', '')}

FULL_CONTENT:
{content}

METADATA:
{json.dumps(metadata, indent=2)}
        """.strip()

        await cognee.remember(
            structured_content,
            dataset_name=f"researchmind_papers",
            document_id=paper_id,
        )
        logger.info(f"✅ remember() — Paper {paper_id} ingested into knowledge graph")
        return True

    except Exception as e:
        logger.error(f"❌ remember() failed for {paper_id}: {e}")
        return False


async def recall_papers(query: str, paper_ids: Optional[list] = None) -> str:
    """
    Cognee recall() — Query across all papers with hybrid graph+vector search.
    """
    try:
        context_filter = ""
        if paper_ids:
            context_filter = f" Focus on papers: {', '.join(paper_ids)}."

        full_query = f"{query}{context_filter}"

        results = await cognee.recall(
            full_query,
            dataset_name="researchmind_papers",
        )

        if isinstance(results, list):
            return "\n\n".join([str(r) for r in results])
        return str(results)

    except Exception as e:
        logger.error(f"❌ recall() failed: {e}")
        return f"Memory query failed: {str(e)}"


async def improve_paper(paper_id: str, feedback: str, rating: int) -> bool:
    """
    Cognee improve()/memify() — Update node weights based on user feedback.
    """
    try:
        feedback_content = f"""
USER_FEEDBACK for PAPER_ID: {paper_id}
RATING: {rating}/5
FEEDBACK: {feedback}
ACTION: {"INCREASE_WEIGHT" if rating >= 4 else "DECREASE_WEIGHT" if rating <= 2 else "NEUTRAL"}
        """.strip()

        await cognee.memify(
            feedback_content,
            dataset_name="researchmind_papers",
        )
        logger.info(f"✅ improve() — Feedback applied for paper {paper_id}, rating: {rating}")
        return True

    except Exception as e:
        logger.error(f"❌ improve() failed for {paper_id}: {e}")
        return False


async def forget_paper(paper_id: str) -> bool:
    """
    Cognee forget() — Surgically remove paper and all its relationships from graph.
    """
    try:
        await cognee.forget(
            document_id=paper_id,
            dataset_name="researchmind_papers",
        )
        logger.info(f"✅ forget() — Paper {paper_id} removed from knowledge graph")
        return True

    except Exception as e:
        logger.error(f"❌ forget() failed for {paper_id}: {e}")
        return False


async def recall_for_review(focus_area: str = "") -> str:
    """
    Special recall for lit review generation — retrieves structured relationships.
    """
    try:
        query = f"""
        Retrieve all papers with their:
        - Main methodology and models used
        - Datasets used
        - Key findings and accuracy metrics
        - Stated limitations
        - Research gaps identified
        - Relationships with other papers in the collection
        {f'Focus area: {focus_area}' if focus_area else ''}
        Provide structured information for literature review writing.
        """

        results = await cognee.recall(
            query,
            dataset_name="researchmind_papers",
        )

        if isinstance(results, list):
            return "\n\n---\n\n".join([str(r) for r in results])
        return str(results)

    except Exception as e:
        logger.error(f"❌ recall_for_review() failed: {e}")
        return ""