import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routes.invoice_routes import router as invoice_router
from app.schemas.invoice_response import ApiResponse, ErrorDetail

load_dotenv(override=True)

app = FastAPI(
    title="Invoice Extractor API",
    description="AI-powered utility invoice extraction system",
    version="1.0.0",
)

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    if isinstance(exc.detail, dict) and "success" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)

    return JSONResponse(
        status_code=exc.status_code,
        content=ApiResponse(
            success=False,
            error=ErrorDetail(
                code="REQUEST_ERROR",
                message=str(exc.detail),
            ),
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, __: Exception):
    return JSONResponse(
        status_code=500,
        content=ApiResponse(
            success=False,
            error=ErrorDetail(
                code="INTERNAL_ERROR",
                message="An unexpected error occurred. Please try again.",
            ),
        ).model_dump(),
    )


app.include_router(invoice_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
