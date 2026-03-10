from fastapi import APIRouter, Query

from app.services.retrieval_service import retrieve_notes

router = APIRouter(prefix="/query", tags=["query"])


@router.get("", summary="Run a semantic query over notes")
def query_notes(q: str = Query(min_length=1)) -> dict[str, object]:
    results = retrieve_notes(q)
    return {"query": q, "results": results}
