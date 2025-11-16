from datetime import datetime

from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException

from app.celery_app import celery_app
from app.models import JOBS, Job
from app.schemas import JobInfo


router = APIRouter(prefix="/jobs", tags=["jobs"])


def _sync_job_from_celery(job: Job, async_result: AsyncResult) -> Job:
    job.status = async_result.state
    job.updated_at = datetime.utcnow()

    if async_result.successful():
        job.preview = str(async_result.result)
        job.error = None
    elif async_result.failed():
        job.error = str(async_result.result)

    return job


@router.get("/{job_id}", response_model=JobInfo)
def get_job(job_id: str) -> JobInfo:
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    async_result = AsyncResult(job_id, app=celery_app)
    job = _sync_job_from_celery(job, async_result)

    return JobInfo(
        id=job.id,
        file_name=job.file_name,
        mime=job.mime,
        status=job.status,
        preview=job.preview,
        error=job.error,
    )
