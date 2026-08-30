from fastapi import FastAPI

from backend.app.config import settings
from backend.app.api.routes.verify import router as verify_router


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Claim-Level Verification Framework for AI-Generated Legal Responses",
    version="0.1.0",
)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "service": "TrustGate-AI",
    }


app.include_router(
    verify_router,
    prefix=settings.API_V1_STR,
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
