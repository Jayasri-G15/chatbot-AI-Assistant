import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import conversations, documents, messages, auth, customers, deals, activities, leads, admin
from app.core.config import settings
from app.core.database import Base, engine
import app.models  # Ensure all models are registered for Base.metadata.create_all
from app.database.seed import seed_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

Base.metadata.create_all(bind=engine)
try:
    seed_db()
except Exception as e:
    logger.warning(f"Seed DB check: {e}")

app = FastAPI(title="AI CRM Assistant API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail
    if isinstance(detail, dict) and "error" in detail:
        return JSONResponse(status_code=exc.status_code, content=detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": "HTTP_ERROR", "message": str(detail)}},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error")
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_ERROR", "message": "Something went wrong. Please try again."}},
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
@app.get("/health/ready")
def ready():
    from app.services.redis_service import redis_health_check
    redis_info = redis_health_check()
    
    try:
        with engine.connect():
            pass
        db_status = "ok"
    except Exception:
        return JSONResponse(status_code=503, content={"status": "not_ready", "database": "unavailable", "redis": redis_info["status"]})

    return {"status": "ready", "database": db_status, "redis": redis_info["status"]}


app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(conversations.router)
app.include_router(messages.router)
app.include_router(documents.router)
app.include_router(customers.router)
app.include_router(deals.router)
app.include_router(activities.router)
app.include_router(leads.router)
