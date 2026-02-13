import uuid
import asyncio
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks

from ..database import create_job, get_job, get_all_jobs, update_job
from ..services.processor import process_video

router = APIRouter()

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv"}


@router.post("/upload")
async def upload_video(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported format: {ext}. Use: {ALLOWED_EXTENSIONS}")

    job_id = str(uuid.uuid4())
    save_path = UPLOAD_DIR / f"{job_id}{ext}"

    with open(save_path, "wb") as buf:
        shutil.copyfileobj(file.file, buf)

    await create_job(job_id, file.filename, str(save_path))
    background_tasks.add_task(process_video, job_id, str(save_path))

    return {"job_id": job_id, "status": "pending", "message": "Upload successful, processing started"}


@router.get("/jobs")
async def list_jobs():
    jobs = await get_all_jobs()
    return {"jobs": jobs}


@router.get("/jobs/{job_id}")
async def job_status(job_id: str):
    job = await get_job(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return job


@router.get("/jobs/{job_id}/stats")
async def job_stats(job_id: str):
    import json
    job = await get_job(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    if job["status"] != "completed":
        raise HTTPException(400, f"Job status: {job['status']}")
    if not job.get("stats_json"):
        raise HTTPException(404, "No stats available")
    return json.loads(job["stats_json"])
