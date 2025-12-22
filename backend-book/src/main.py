from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .api.v1 import translation

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Book Translation API",
    description="API for translating book content while preserving technical accuracy and structure",
    version="1.0.0"
)

# Set up rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include API routes
app.include_router(translation.router, prefix="/api/v1", tags=["translation"])

@app.get("/")
def read_root():
    return {"message": "Book Translation API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}