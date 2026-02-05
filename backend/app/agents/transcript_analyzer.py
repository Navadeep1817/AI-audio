from typing import Dict, Any, List
import json
from app.agents.base_agent import BaseAgent
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TranscriptAnalyzerAgent(BaseAgent):
    """Agent that analyzes call structure, identifies speakers, and extracts key information."""
    
    def __init__(self):
        super().__init__(agent_name="Transcript Analyzer")
    
    def get_system_prompt(self) -> str:
        return """You are an expert sales call analyst. Your role is to:

1. Analyze the structure and flow of sales conversations
2. Identify speaker roles (sales rep vs. customer)
3. Extract key information: customer pain points, questions asked, topics discussed
4. Identify the call phase (intro, discovery, presentation, objection handling, close)
5. Note conversation dynamics and rapport building

Provide structured, objective analysis focusing on factual observations."""
    
    def analyze(self, transcript: str, context: str = "", previous_analyses: List[Dict] = None) -> Dict[str, Any]:
        """Analyze transcript structure and content."""
        
        prompt = f"""Analyze this sales call transcript:

{transcript}

Provide a comprehensive analysis covering:
1. Call structure and phases
2. Speaker identification and roles
3. Key topics and pain points discussed
4. Questions asked by rep and customer
5. Conversation flow and transitions
6. Overall call dynamics

Return your analysis in the following JSON format:
{{
    "call_phases": ["phase1", "phase2", ...],
    "speaker_roles": {{"spk_0": "role", "spk_1": "role"}},
    "customer_pain_points": ["pain1", "pain2", ...],
    "questions_asked_by_rep": ["question1", ...],
    "questions_asked_by_customer": ["question1", ...],
    "key_topics": ["topic1", "topic2", ...],
    "conversation_quality": "assessment",
    "summary": "brief summary"
}}
"""
        
        logger.info(f"{self.agent_name}: Starting analysis...")
        
        response = self.invoke_llm(prompt)
        
        # Parse JSON response
        try:
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()
            
            analysis_result = json.loads(json_str)
            
            logger.info(f"{self.agent_name}: Analysis completed successfully")
            
            return {
                "agent_name": self.agent_name,
                "analysis": analysis_result,
                "raw_response": response
            }
        
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {e}")
            # Fallback: return raw response
            return {
                "agent_name": self.agent_name,
                "analysis": {"raw_analysis": response},
                "raw_response": response
            }