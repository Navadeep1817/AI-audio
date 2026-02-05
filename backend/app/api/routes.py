from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Optional
from datetime import datetime
import boto3
import json

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


from app.models import (
    AudioUploadResponse,
    JobStatusResponse,
    ProcessingStatus,
    TranscriptResponse,
    SalesReport,
)
from app.services.s3_service import S3Service
from app.services.transcribe_service import TranscribeService
from app.services.agent_service import AgentOrchestrationService
from app.utils.logger import get_logger
from app.config import get_settings

logger = get_logger(__name__)
settings = get_settings()

router = APIRouter(prefix="/api/v1", tags=["Sales Coach API"])

job_status_store: Dict[str, Dict] = {}

s3_service = S3Service()
transcribe_service = TranscribeService()
agent_service = AgentOrchestrationService()

s3_client = boto3.client(
    "s3",
    region_name=settings.AWS_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)

# ----------------------------------------------------------
# JOB STATUS HELPER
# ----------------------------------------------------------
def update_job_status(
    job_id: str,
    status: ProcessingStatus,
    progress: int,
    step: str,
    transcript: Optional[TranscriptResponse] = None,
    report: Optional[SalesReport] = None,
    error: Optional[str] = None,
):
    job_status_store[job_id] = {
        "job_id": job_id,
        "status": status,
        "progress_percentage": progress,
        "current_step": step,
        "transcript": transcript,
        "report": report,
        "error_message": error,
        "updated_at": datetime.utcnow(),
    }

    logger.info(f"Job {job_id}: {status.value} - {step} ({progress}%)")


# ----------------------------------------------------------
# MAIN PIPELINE
# ----------------------------------------------------------
async def process_audio_pipeline(job_id: str, file_extension: str):

    try:
        update_job_status(job_id, ProcessingStatus.TRANSCRIBING, 10, "Starting transcription")

        audio_uri = s3_service.get_audio_uri(job_id, file_extension)
        logger.info(f"[PIPELINE] Audio URI resolved: {audio_uri}")

        transcription_job_name = transcribe_service.start_transcription_job(job_id, audio_uri)

        update_job_status(job_id, ProcessingStatus.TRANSCRIBING, 20, "Transcription in progress")

        job_result = transcribe_service.wait_for_completion(transcription_job_name)

        update_job_status(job_id, ProcessingStatus.TRANSCRIBING, 50, "Transcription completed")

        # 🔥 FETCH TRANSCRIPT FROM S3 DIRECTLY (PRODUCTION SAFE)
        bucket = settings.S3_BUCKET_NAME
        key = f"{settings.TRANSCRIBE_JOB_PREFIX}{job_id}.json"

        logger.info(f"[TRANSCRIBE] Fetching transcript via S3 API")
        logger.info(f"[TRANSCRIBE] Bucket: {bucket}")
        logger.info(f"[TRANSCRIBE] Key: {key}")

        obj = s3_client.get_object(Bucket=bucket, Key=key)
        transcript_json = json.loads(obj["Body"].read().decode("utf-8"))

        logger.info("[TRANSCRIBE] Transcript loaded successfully from S3")

        s3_service.save_transcript(job_id, transcript_json)

        transcript_response = transcribe_service.parse_transcript_with_speakers(transcript_json)
        transcript_response.job_id = job_id

        update_job_status(
            job_id,
            ProcessingStatus.ANALYZING,
            60,
            "Running AI agent analysis",
            transcript=transcript_response,
        )

        logger.info(f"Starting agent orchestration for job {job_id}")
        sales_report = agent_service.analyze_call(job_id, transcript_response)

        update_job_status(
            job_id,
            ProcessingStatus.COMPLETED,
            100,
            "Analysis complete",
            transcript=transcript_response,
            report=sales_report,
        )

        logger.info(f"✓ Job {job_id} completed successfully")

    except Exception as e:
        logger.error(f"Error processing job {job_id}: {e}")
        update_job_status(job_id, ProcessingStatus.FAILED, 0, "Processing failed", error=str(e))


# ----------------------------------------------------------
# UPLOAD ENDPOINT
# ----------------------------------------------------------
@router.post("/upload")
async def upload_audio(file_extension: str = "mp3"):

    job_id, upload_url = s3_service.generate_presigned_upload_url(file_extension)

    # ⭐ SAVE EXTENSION WITH JOB STATUS
    update_job_status(
        job_id,
        ProcessingStatus.PENDING,
        0,
        "Awaiting upload",
    )

    # 🔥 NEW LINE (store extension)
    job_status_store[job_id]["file_extension"] = file_extension

    return AudioUploadResponse(
        job_id=job_id,
        upload_url=upload_url,
        status=ProcessingStatus.PENDING,
        message="Upload URL generated.",
    )


# ----------------------------------------------------------
# 🔥 START PIPELINE AFTER UPLOAD (CRITICAL FIX)
# ----------------------------------------------------------
@router.post("/start/{job_id}")
async def start_pipeline(job_id: str, background_tasks: BackgroundTasks):

    if job_id not in job_status_store:
        raise HTTPException(status_code=404, detail="Job not found")

    # ⭐ GET REAL EXTENSION
    file_extension = job_status_store[job_id].get("file_extension", "mp3")

    background_tasks.add_task(process_audio_pipeline, job_id, file_extension)

    return {"status": "started"}


# ----------------------------------------------------------
# STATUS
# ----------------------------------------------------------
@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):

    if job_id not in job_status_store:
        raise HTTPException(status_code=404, detail="Job not found")

    job_data = job_status_store[job_id]

    return JobStatusResponse(
        job_id=job_data["job_id"],
        status=job_data["status"],
        progress_percentage=job_data["progress_percentage"],
        current_step=job_data["current_step"],
        transcript=job_data.get("transcript"),
        report=job_data.get("report"),
        error_message=job_data.get("error_message"),
    )

# =====================================================
# HEALTH CHECK — REQUIRED FOR FRONTEND
# =====================================================
@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "ai-sales-coach-api",
        "timestamp": datetime.utcnow().isoformat()
    }
