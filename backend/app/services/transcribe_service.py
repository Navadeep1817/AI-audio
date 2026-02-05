import boto3
import time
from app.config import get_settings
from app.models import TranscriptSegment, TranscriptResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class TranscribeService:
    """Handle AWS Transcribe operations."""

    def __init__(self):

        self.transcribe_client = boto3.client(
            "transcribe",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

        self.s3_client = boto3.client(
            "s3",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

    # ============================================================
    # WAIT UNTIL FILE EXISTS IN S3  🔥 FIXED INDENTATION
    # ============================================================
    def wait_for_s3_object(self, bucket: str, key: str, timeout: int = 120):

        logger.info(f"[TRANSCRIBE] Waiting for S3 upload: {key}")

        start = time.time()

        while True:
            try:
                self.s3_client.head_object(Bucket=bucket, Key=key)
                logger.info(f"[TRANSCRIBE] S3 object confirmed: {key}")
                return

            except Exception:

                elapsed = time.time() - start

                if elapsed > timeout:
                    raise Exception(
                        f"S3 object not found after waiting {timeout}s"
                    )

                logger.info(
                    f"[TRANSCRIBE] Waiting for upload... ({int(elapsed)}s)"
                )

                time.sleep(3)

    # ============================================================
    # Detect media format automatically
    # ============================================================
    def _detect_media_format(self, uri: str) -> str:

        ext = uri.split(".")[-1].lower()

        if ext in ["mp3", "wav", "ogg", "webm", "m4a"]:
            return ext

        return "mp3"

    # ============================================================
    # START TRANSCRIPTION
    # ============================================================
    def start_transcription_job(self, job_id: str, audio_s3_uri: str) -> str:

        transcription_job_name = f"{settings.TRANSCRIBE_JOB_PREFIX}{job_id}"

        logger.info(f"[TRANSCRIBE] Starting job with URI: {audio_s3_uri}")

        bucket = settings.S3_BUCKET_NAME
        key = audio_s3_uri.replace(f"s3://{bucket}/", "")

        # 🔥 Wait until upload finishes
        self.wait_for_s3_object(bucket, key)

        media_format = self._detect_media_format(audio_s3_uri)

        self.transcribe_client.start_transcription_job(
            TranscriptionJobName=transcription_job_name,
            Media={"MediaFileUri": audio_s3_uri},
            MediaFormat=media_format,
            LanguageCode="en-US",
            OutputBucketName=settings.TRANSCRIBE_OUTPUT_BUCKET,
            Settings={
                "ShowSpeakerLabels": True,
                "MaxSpeakerLabels": 2,
            },
        )

        logger.info(f"Started transcription job: {transcription_job_name}")
        return transcription_job_name

    # ============================================================
    # WAIT FOR COMPLETION
    # ============================================================
    def wait_for_completion(self, transcription_job_name: str, timeout: int = 600) -> dict:

        start_time = time.time()

        while True:

            if time.time() - start_time > timeout:
                raise TimeoutError(
                    f"Transcription job timed out after {timeout}s"
                )

            response = self.transcribe_client.get_transcription_job(
                TranscriptionJobName=transcription_job_name
            )

            job = response["TranscriptionJob"]
            status = job["TranscriptionJobStatus"]

            if status == "COMPLETED":
                logger.info(f"Transcription completed: {transcription_job_name}")
                return job

            if status == "FAILED":
                failure_reason = job.get("FailureReason", "Unknown")
                raise Exception(f"Transcription failed: {failure_reason}")

            logger.info(f"Transcription status: {status}. Waiting...")
            time.sleep(10)

    # ============================================================
    # 🔥 FINAL SAFE PARSER (WITH FALLBACK)
    # ============================================================
    def parse_transcript_with_speakers(self, transcript_json: dict) -> TranscriptResponse:

        results = transcript_json.get("results", {})
        speaker_labels = results.get("speaker_labels") or {}
        speaker_segments = speaker_labels.get("segments", [])
        items = results.get("items", [])

        segments = []

        # --------------------------------------------------------
        # CASE 1 — Speaker diarization exists
        # --------------------------------------------------------
        if speaker_segments:

            for segment in speaker_segments:

                speaker = segment.get("speaker_label", "spk_0")
                text_parts = []

                for seg_item in segment.get("items", []):
                    start_time_item = float(seg_item.get("start_time", 0))

                    for word_item in items:

                        if word_item.get("type") == "pronunciation":

                            word_start = float(word_item.get("start_time", 0))

                            if abs(word_start - start_time_item) < 0.01:
                                text_parts.append(
                                    word_item["alternatives"][0]["content"]
                                )

                        elif word_item.get("type") == "punctuation":
                            text_parts.append(
                                word_item["alternatives"][0]["content"]
                            )

                segment_text = (
                    " ".join(text_parts)
                    .replace(" ,", ",")
                    .replace(" .", ".")
                )

                segments.append(
                    TranscriptSegment(
                        speaker=speaker,
                        text=segment_text,
                        start_time=float(segment.get("start_time", 0)),
                        end_time=float(segment.get("end_time", 0)),
                    )
                )

        # --------------------------------------------------------
        # CASE 2 — NO SPEAKER LABELS (SHORT AUDIO)
        # --------------------------------------------------------
        else:

            logger.warning("[TRANSCRIBE] No speaker labels — fallback parsing")

            text_parts = []
            start_time = 0.0
            end_time = 0.0

            for word_item in items:

                if word_item.get("type") == "pronunciation":
                    text_parts.append(
                        word_item["alternatives"][0]["content"]
                    )
                    end_time = float(word_item.get("end_time", end_time))

                elif word_item.get("type") == "punctuation":
                    text_parts.append(
                        word_item["alternatives"][0]["content"]
                    )

            full_text = " ".join(text_parts)

            segments.append(
                TranscriptSegment(
                    speaker="spk_0",
                    text=full_text,
                    start_time=start_time,
                    end_time=end_time,
                )
            )

        # Metadata
        full_text = " ".join([seg.text for seg in segments])
        word_count = len(full_text.split())
        duration = segments[-1].end_time if segments else 0.0

        return TranscriptResponse(
            job_id="",
            segments=segments,
            duration=duration,
            word_count=word_count,
        )
