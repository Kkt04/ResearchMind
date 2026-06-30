from fastapi import APIRouter, HTTPException
from app.models.schemas import QueryRequest, QueryResponse, ChatRequest, ChatResponse
from app.services.query_service import process_query, chat_with_memory

router = APIRouter(prefix="/query", tags=["query"])


@router.post("/", response_model=QueryResponse)
async def query_papers(request: QueryRequest):
    result = await process_query(
        query=request.query,
        paper_ids=request.paper_ids,
        mode=request.mode or "full",
    )
    return result


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    history = [{"role": m.role, "content": m.content} for m in request.history]
    result = await chat_with_memory(request.message, history)
    return result