"""
FastAPI application main entry point.
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.core.database import init_db
import logging

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.APP_VERSION,
    description="Pizzeria Management System API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Validation error handler for better error messages
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors with user-friendly messages."""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        # Make error messages more user-friendly
        if "value_error" in error["type"]:
            message = error.get("msg", "Ongeldige waarde")
        elif "type_error" in error["type"]:
            message = f"Verwacht type {error.get('type', 'unknown')}"
        
        errors.append({
            "field": field,
            "message": message,
            "type": error.get("type", "validation_error")
        })
    
    # Return first error message as detail for simplicity
    detail = errors[0]["message"] if errors else "Validatiefout"
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": detail,
            "errors": errors
        }
    )

# CORS middleware
# Convert list to list of strings if needed
cors_origins = settings.BACKEND_CORS_ORIGINS
if isinstance(cors_origins, str):
    cors_origins = [origin.strip() for origin in cors_origins.split(",")]
elif not isinstance(cors_origins, list):
    cors_origins = list(cors_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response

# Trusted hosts (only in production)
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure with actual domain in production
    )


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info("Starting Pizzeria Management API...")
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Pizzeria Management System API",
        "version": settings.APP_VERSION,
        "docs": "/api/docs"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Import and include routers
from app.api import customers, auth, orders, menu, extras, reports, websocket, printer, contact, addresses, settings as settings_api, order_tracking
app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["auth"])
app.include_router(customers.router, prefix=settings.API_V1_STR, tags=["customers"])
app.include_router(orders.router, prefix=settings.API_V1_STR, tags=["orders"])
app.include_router(order_tracking.router, prefix=settings.API_V1_STR, tags=["order-tracking"])
app.include_router(menu.router, prefix=settings.API_V1_STR, tags=["menu"])
app.include_router(extras.router, prefix=settings.API_V1_STR, tags=["extras"])
app.include_router(reports.router, prefix=settings.API_V1_STR, tags=["reports"])
app.include_router(websocket.router, tags=["websocket"])
app.include_router(printer.router, prefix=settings.API_V1_STR, tags=["printer"])
app.include_router(contact.router, prefix=settings.API_V1_STR, tags=["contact"])
app.include_router(addresses.router, prefix=settings.API_V1_STR, tags=["addresses"])
app.include_router(settings_api.router, prefix=settings.API_V1_STR, tags=["settings"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

