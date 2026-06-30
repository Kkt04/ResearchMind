from fastapi import APIRouter, HTTPException
from app.models.schemas import FeedbackRequest, FeedbackResponse
from app.services import paper_service
from app.core.cognee_client import improve_paper

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    paper = paper_service.get_paper_by_id(request.paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    success = await improve_paper(request.paper_id, request.feedback, request.rating)
    paper_service.update_paper_rating(request.paper_id, request.rating, request.feedback)

    return {
        "success": True,
        "message": f"Feedback recorded. Paper credibility weight {'increased' if request.rating >= 4 else 'decreased' if request.rating <= 2 else 'unchanged'}.",
    }