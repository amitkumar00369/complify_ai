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
from app.api.v1.user.api_routes import userRouter

from app.api.v1.admin.api_routes import adminRouter
from app.api.v1.compliance import complianceRouter
# from app.api.v1.routes_whatsapp import whatsappRouter
# from app.api.v1.stripe_routes import stripeRouter


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


#  Static Files
# app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")


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
app.include_router(userRouter, prefix="/api/v1/user", tags=["User-API"])
app.include_router(adminRouter, prefix="/api/v1/admin", tags=["Admin-API"])
app.include_router(complianceRouter, prefix="/api/v1/compliance", tags=["Compliance-API"])

# app.include_router(whatsappRouter, prefix="/api/v1/whatsapp", tags=["WhatsApp-API"])
# app.include_router(stripeRouter, prefix="/api/v1/stripe", tags=["Stripe-API"])
# app.include_router(uploadRouter)


# ===========================
# PRIVATE ROUTES
# ===========================
app.include_router(
    userRouter,
    prefix="/api/v1/user/private",
    tags=["User-Private-API"],
    dependencies=[Depends(security), Depends(jwt_auth)]
)

app.include_router(
    adminRouter,
    prefix="/api/v1/admin/private",
    tags=["Admin-Private-API"],
    dependencies=[Depends(security), Depends(jwt_auth_admin)]
)


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