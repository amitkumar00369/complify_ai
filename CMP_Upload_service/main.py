from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
# from app.controllers.image import router as uploadRouter


#  Core
from core.database import Base, engine
from sqlalchemy import text
from core.config import settings

#  Middleware
from app.middleware.logging import LoggingMiddleware
from app.middleware.ratelimit import RateLimitMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.response_time import ResponseTimeMiddleware
from app.middleware.security import SecurityHeadersMiddleware
from app.middleware.exception import global_exception_handler
from app.middleware.auth_middleware import jwt_auth,jwt_auth_admin



#  Routers

from app.api.v1.upload import uploadFileRouter



# Security
security = HTTPBearer()

# File Upload Config
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")


# Lifespan (startup/shutdown)
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("App starting...")

    if settings.ENV == "dev":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    yield

    print(" App shutting down...")


# App Init
app = FastAPI(lifespan=lifespan)





#  CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#  Middleware Order (VERY IMPORTANT)
app.add_middleware(RequestIDMiddleware)                       # 1. Request ID
app.add_middleware(LoggingMiddleware)                         # 2. Logging
app.add_middleware(ResponseTimeMiddleware)                    # 3. Response time
app.add_middleware(SecurityHeadersMiddleware)                 # 4. Security headers
app.add_middleware(RateLimitMiddleware, max_requests=10, window=60)  # 5. Rate limiting


# Global Exception Handler
app.add_exception_handler(Exception, global_exception_handler)


# ===========================
# PUBLIC ROUTES
# ===========================

app.include_router(uploadFileRouter, prefix="/api/v1/upload", tags=["Upload-API"])



# ===========================
# PRIVATE ROUTES

# ===========================


# ===========================
# HEALTH CHECK
# ===========================
@app.get("/health")
async def health_check():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception:
        return {"status": "unhealthy"}


#  Console log
print(f"Server running on: http://localhost:{settings.APP_PORT}/docs")