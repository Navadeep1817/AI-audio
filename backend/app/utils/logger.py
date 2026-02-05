import logging
import sys
from app.config import get_settings

settings = get_settings()


def get_logger(name: str) -> logging.Logger:
    """
    Get configured logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    
    # Only add handler if not already configured
    if not logger.handlers:
        logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
        
        # Console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
        
        # Formatter
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
    
    return logger