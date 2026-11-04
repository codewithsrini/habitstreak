from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.errors import ApiError, api_error_handler
from app.routers import habits

app = FastAPI(title="HabitStreak", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_methods=["*"],
    allow_headers=["*"],    # includes our custom X-Client-Id header
)

app.add_exception_handler(ApiError, api_error_handler)
app.include_router(habits.router, prefix="/api/v1")

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}