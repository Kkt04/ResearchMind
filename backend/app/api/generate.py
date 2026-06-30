from fastapi import APIRouter
from app.models.schemas import ReviewRequest, ReviewResponse
from app.services.review_service import generate_literature_review

router = APIRouter(prefix="/generate", tags=["generate"])


@router.post("/review", response_model=ReviewResponse)
async def generate_review(request: ReviewRequest):
    result = await generate_literature_review(
        title=request.title or "Literature Review",
        focus_area=request.focus_area or "",
        paper_ids=request.paper_ids,
    )
    return result