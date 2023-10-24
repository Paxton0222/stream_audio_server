from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError
from http import HTTPStatus
from app.api import api_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.exception_handler(OperationalError)
async def global_exception_handler(request, exc):
    return JSONResponse(content={"error": "Database not connected."}, status_code=HTTPStatus.SERVICE_UNAVAILABLE)