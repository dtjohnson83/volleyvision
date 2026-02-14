import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import init_db
from .routers.upload import router as upload_router

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
        await init_db()
        yield

app = FastAPI(
        title="VolleyVision API",
        description="Volleyball video analytics powered by computer vision",
        version="0.1.0",
        lifespan=lifespan,
)

# Build CORS origins from env or use defaults
_default_origins = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://volleyvision-gray.vercel.app",
]
_extra = os.getenv("CORS_ORIGINS", "")
cors_origins = _default_origins + [o.strip() for o in _extra.split(",") if o.strip()]

app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
)

app.include_router(upload_router, prefix="/api")

# Serve output files
output_dir = Path("data/output")
output_dir.mkdir(parents=True, exist_ok=True)
app.mount("/output", StaticFiles(directory=str(output_dir)), name="output")

@app.get("/api/health")
async def health():
        return {"status": "ok", "service": "volleyvision"}
