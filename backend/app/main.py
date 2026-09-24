from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from backend.app.config import settings
from backend.app.api.routes.verify import router as verify_router
from backend.app.api.routes.retrieval_test import router as retrieval_test_router

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STATIC_DIR = BASE_DIR / "frontend" / "static"
TEMPLATES_DIR = BASE_DIR / "frontend" / "templates"

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Claim-Level Verification Framework for AI-Generated Legal Responses",
    version="0.1.0",
)

# Enable CORS for browser frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Setup Jinja2 Templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.get("/", tags=["Frontend"])
async def read_index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


@app.get("/verify", tags=["Frontend"])
async def read_verify(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="verify.html"
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
app.include_router(
    retrieval_test_router,
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
