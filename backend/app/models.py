from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class ProcessingStatus(str, Enum):
    """Status of audio processing pipeline."""
    PENDING = "pending"
    UPLOADING = "uploading"
    TRANSCRIBING = "transcribing"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class AudioUploadResponse(BaseModel):
    """Response after audio upload."""
    job_id: str
    upload_url: str
    status: ProcessingStatus
    message: str


class TranscriptSegment(BaseModel):
    """Individual transcript segment with speaker."""
    speaker: str
    text: str
    start_time: float
    end_time: float


class TranscriptResponse(BaseModel):
    """Full transcript with metadata."""
    job_id: str
    segments: List[TranscriptSegment]
    duration: float
    word_count: int


class AgentInsight(BaseModel):
    """Individual agent analysis result."""
    agent_name: str
    analysis: str
    key_points: List[str]
    score: Optional[float] = None


class SalesReport(BaseModel):
    """Final aggregated sales improvement report."""
    job_id: str
    call_summary: str
    overall_score: float
    strengths: List[str]
    weaknesses: List[str]
    missed_opportunities: List[str]
    objections_detected: List[Dict[str, str]]
    recommended_actions: List[str]
    agent_insights: List[AgentInsight]
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class JobStatusResponse(BaseModel):
    """Job processing status."""
    job_id: str
    status: ProcessingStatus
    progress_percentage: int
    current_step: str
    transcript: Optional[TranscriptResponse] = None
    report: Optional[SalesReport] = None
    error_message: Optional[str] = None