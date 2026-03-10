from fastapi import FastAPI

from app.routes.health import router as health_router
from app.routes.notes import router as notes_router
from app.routes.query import router as query_router

app = FastAPI(title="AI Class Backend", version="0.1.0")

app.include_router(health_router)
app.include_router(notes_router)
app.include_router(query_router)
