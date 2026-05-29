from contextlib import asynccontextmanager
import os

from fastapi import (
    FastAPI,
    Depends
)

from fastapi.middleware.cors import (
    CORSMiddleware
)

from fastapi.security import (
    HTTPBearer
)

from sqlalchemy import text

# ==========================================
# CORE
# ==========================================
from core.database import (
    Base,
    engine,
    AsyncSessionLocal
)

from core.config import (
    settings
)

# ==========================================
# SCHEDULER
# ==========================================
from app.schedulers.scheduler import (
    scheduler
)

from app.schedulers.job_scheduler import (
    JobScheduler
)

# ==========================================
# MIDDLEWARE
# ==========================================
from app.middleware.logging import (
    LoggingMiddleware
)

from app.middleware.ratelimit import (
    RateLimitMiddleware
)

from app.middleware.request_id import (
    RequestIDMiddleware
)

from app.middleware.response_time import (
    ResponseTimeMiddleware
)

from app.middleware.security import (
    SecurityHeadersMiddleware
)

from app.middleware.exception import (
    global_exception_handler
)

from app.middleware.auth_middleware import (
    jwt_auth,
    jwt_auth_admin
)

# ==========================================
# ROUTERS
# ==========================================
from app.api.v1.user.api_routes import (
    userRouter
)

from app.api.v1.admin.api_routes import (
    adminRouter
)

from app.api.v1.compliance import (
    complianceRouter
)



# ==========================================
# SECURITY
# ==========================================
security = HTTPBearer()

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# ==========================================
# SCHEDULER RUNNER
# ==========================================
async def run_pending_jobs():

    async with AsyncSessionLocal() as db:

        await JobScheduler.process_pending_jobs(
            db
        )


# ==========================================
# APP LIFESPAN
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):

    print("App starting...")

    try:

        if settings.ENV == "dev":

            async with engine.begin() as conn:

                await conn.run_sync(
                    Base.metadata.create_all
                )

        scheduler.add_job(
            run_pending_jobs,
            trigger="interval",
            seconds=10,
            max_instances=1,
            coalesce=True,
            id="process_pending_jobs",
            replace_existing=True
        )

        scheduler.start()

        yield

    finally:

        if scheduler.running:

            scheduler.shutdown()

        print("App shutting down...")


# ==========================================
# APP INIT
# ==========================================
app = FastAPI(
    lifespan=lifespan
)

# ==========================================
# CORS
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# MIDDLEWARE
# ==========================================
app.add_middleware(
    RequestIDMiddleware
)

app.add_middleware(
    LoggingMiddleware
)

app.add_middleware(
    ResponseTimeMiddleware
)

app.add_middleware(
    SecurityHeadersMiddleware
)

app.add_middleware(
    RateLimitMiddleware,
    max_requests=10,
    window=60
)

# ==========================================
# EXCEPTION HANDLER
# ==========================================
app.add_exception_handler(
    Exception,
    global_exception_handler
)

# ==========================================
# PUBLIC ROUTES
# ==========================================
app.include_router(
    userRouter,
    prefix="/api/v1/user",
    tags=["User-API"]
)

app.include_router(
    adminRouter,
    prefix="/api/v1/admin",
    tags=["Admin-API"]
)

app.include_router(
    complianceRouter,
    prefix="/api/v1/compliance",
    tags=["Compliance-API"]
)



# ==========================================
# PRIVATE ROUTES
# ==========================================
app.include_router(
    userRouter,
    prefix="/api/v1/user/private",
    tags=["User-Private-API"],
    dependencies=[
        Depends(security),
        Depends(jwt_auth)
    ]
)

app.include_router(
    adminRouter,
    prefix="/api/v1/admin/private",
    tags=["Admin-Private-API"],
    dependencies=[
        Depends(security),
        Depends(jwt_auth_admin)
    ]
)

# ==========================================
# HEALTH CHECK
# ==========================================
@app.get("/health")
async def health_check():

    try:

        async with engine.connect() as conn:

            await conn.execute(
                text("SELECT 1")
            )

        return {
            "status": "healthy"
        }

    except Exception:

        return {
            "status": "unhealthy"
        }


print(
    f"Server running on: "
    f"http://localhost:{settings.APP_PORT}/docs"
)