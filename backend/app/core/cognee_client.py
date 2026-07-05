import cognee
import json
import os
import logging
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


async def init_cognee():
    try:
        if settings.cognee_api_key:
            cognee.config.set_vector_db_key(settings.cognee_api_key)

        logger.info("Cognee initialized")
    except Exception as e:
        logger.warning(f"Cognee init warning: {e}")


async def remember_paper(paper_id: str, content: str, metadata: dict) -> bool:
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

        await cognee.add(structured_content, dataset_name="researchmind_papers")

        logger.info(f"Paper {paper_id} stored")
        return True

    except Exception as e:
        logger.error(f"remember() failed for {paper_id}: {e}")
        return False


async def recall_papers(query: str, paper_ids: Optional[list] = None) -> str:
    try:
        context_filter = ""
        if paper_ids:
            context_filter = f" Focus on papers: {', '.join(paper_ids)}."

        full_query = f"{query}{context_filter}"

        results = await cognee.search(
            cognee.SearchType.INSIGHTS,
            full_query,
        )

        if isinstance(results, list):
            return "\n\n".join([str(r) for r in results])
        return str(results)

    except Exception as e:
        logger.warning(f"recall() non-fatal: {e}")
        return ""


async def improve_paper(paper_id: str, feedback: str, rating: int) -> bool:
    try:
        feedback_content = f"""
USER_FEEDBACK for PAPER_ID: {paper_id}
RATING: {rating}/5
FEEDBACK: {feedback}
        """.strip()

        await cognee.add(feedback_content, dataset_name="researchmind_papers")

        logger.info(f"Feedback applied for paper {paper_id}")
        return True

    except Exception as e:
        logger.error(f"improve() failed for {paper_id}: {e}")
        return False


async def forget_paper(paper_id: str) -> bool:
    try:
        logger.info(f"Forget requested for paper {paper_id}")
        return True

    except Exception as e:
        logger.error(f"forget() failed for {paper_id}: {e}")
        return False


async def recall_for_review(focus_area: str = "") -> str:
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

        results = await cognee.search(
            cognee.SearchType.INSIGHTS,
            query,
        )

        if isinstance(results, list):
            return "\n\n---\n\n".join([str(r) for r in results])
        return str(results)

    except Exception as e:
        logger.warning(f"recall_for_review() non-fatal: {e}")
        return ""
