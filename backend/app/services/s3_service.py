import boto3
import uuid
import json
from botocore.exceptions import ClientError
from botocore.client import Config

from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class S3Service:
    """
    Production-ready S3 Service.

    Fixes included:
    ✔ Signature Version 4 (prevents 403 SignatureDoesNotMatch)
    ✔ No ContentType locking
    ✔ Supports all audio formats
    ✔ Safe presigned uploads
    """

    def __init__(self):
        # ⭐ CRITICAL FIX:
        # Force Signature V4 (required for browser PUT uploads)
        self.s3_client = boto3.client(
            "s3",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            config=Config(signature_version="s3v4"),
        )

        self.bucket_name = settings.S3_BUCKET_NAME

    # ======================================================
    # 🔥 GENERATE PRESIGNED UPLOAD URL (FINAL VERSION)
    # ======================================================
    def generate_presigned_upload_url(self, file_extension: str = "mp3") -> tuple[str, str]:
        job_id = str(uuid.uuid4())

        object_key = f"{settings.S3_AUDIO_PREFIX}{job_id}.{file_extension}"

        try:
            # IMPORTANT:
            # Do NOT include ContentType here.
            presigned_url = self.s3_client.generate_presigned_url(
                ClientMethod="put_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": object_key,
                },
                ExpiresIn=3600,
            )

            logger.info(f"Generated presigned upload URL for job {job_id}")
            return job_id, presigned_url

        except ClientError as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise

    # ======================================================
    # GET AUDIO S3 URI
    # ======================================================
    def get_audio_uri(self, job_id: str, file_extension: str = "mp3") -> str:
        object_key = f"{settings.S3_AUDIO_PREFIX}{job_id}.{file_extension}"
        return f"s3://{self.bucket_name}/{object_key}"

    # ======================================================
    # SAVE TRANSCRIPT JSON TO S3
    # ======================================================
    def save_transcript(self, job_id: str, transcript_data: dict) -> str:
        object_key = f"{settings.S3_TRANSCRIPT_PREFIX}{job_id}.json"

        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=json.dumps(transcript_data),
                ContentType="application/json",
            )

            logger.info(f"Saved transcript for job {job_id}")
            return f"s3://{self.bucket_name}/{object_key}"

        except ClientError as e:
            logger.error(f"Error saving transcript: {e}")
            raise

    # ======================================================
    # DOWNLOAD TRANSCRIPT FROM S3
    # ======================================================
    def download_transcript(self, s3_uri: str) -> dict:
        parts = s3_uri.replace("s3://", "").split("/", 1)
        bucket = parts[0]
        key = parts[1]

        try:
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            transcript_json = response["Body"].read().decode("utf-8")
            return json.loads(transcript_json)

        except ClientError as e:
            logger.error(f"Error downloading transcript: {e}")
            raise
