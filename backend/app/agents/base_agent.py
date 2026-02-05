from abc import ABC, abstractmethod
from typing import Dict, Any, List
import boto3
from langchain_aws import ChatBedrock
from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class BaseAgent(ABC):
    """Abstract base class for all sales coaching agents."""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self) -> ChatBedrock:
        """Initialize AWS Bedrock LLM client."""
        bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        
        llm = ChatBedrock(
            client=bedrock_client,
            model_id=settings.BEDROCK_MODEL_ID,
            model_kwargs={
                "max_tokens": 4096,
                "temperature": 0.7,
                "top_p": 0.9
            }
        )
        
        return llm
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return agent-specific system prompt."""
        pass
    
    @abstractmethod
    def analyze(self, transcript: str, context: str = "", previous_analyses: List[Dict] = None) -> Dict[str, Any]:
        """
        Perform agent-specific analysis.
        
        Args:
            transcript: Full call transcript
            context: RAG-retrieved context (optional)
            previous_analyses: Results from other agents (optional)
            
        Returns:
            Dictionary with analysis results
        """
        pass
    
    def invoke_llm(self, prompt: str) -> str:
        """Invoke LLM with prompt."""
        try:
            messages = [
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": prompt}
            ]
            
            response = self.llm.invoke(messages)
            return response.content
        
        except Exception as e:
            logger.error(f"Error invoking LLM for {self.agent_name}: {e}")
            raise           