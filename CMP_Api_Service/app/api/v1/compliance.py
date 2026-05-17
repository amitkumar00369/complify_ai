
from app.controllers.compliance.query_controller import query

from fastapi import APIRouter

complianceRouter: APIRouter = APIRouter()
complianceRouter.post("/query")(query)


