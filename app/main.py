from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from app.api.endpoints import router
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


app = FastAPI()

@app.on_event("startup")
async def startup():
    print("App is starting up...")

app.include_router(router)

app = FastAPI(
    title="WorldBank Country API",
    version="1.0.0",
    description="Get country info and GDP graph from World Bank",
)

# Include your endpoints
app.include_router(router)

@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend(), prefix="worldbank-cache")

# Enable CORS if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)