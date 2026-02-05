class SalesCoachException(Exception):
    """Base exception for Sales Coach application."""
    pass


class TranscriptionException(SalesCoachException):
    """Exception during transcription process."""
    pass


class AgentException(SalesCoachException):
    """Exception during agent execution."""
    pass


class RAGException(SalesCoachException):
    """Exception during RAG operations."""
    pass


class S3Exception(SalesCoachException):
    """Exception during S3 operations."""
    pass          