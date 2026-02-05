from typing import Dict, Any, List
import json
from app.agents.base_agent import BaseAgent
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ObjectionExpertAgent(BaseAgent):
    """Agent specialized in detecting and analyzing objection handling."""
    
    def __init__(self):
        super().__init__(agent_name="Objection Expert")
    
    def get_system_prompt(self) -> str:
        return """You are an expert in sales objection handling. Your role is to:

1. Detect all customer objections (explicit and implicit)
2. Classify objection types (price, timing, authority, need, competition, etc.)
3. Evaluate how the rep handled each objection
4. Identify missed opportunities to address concerns
5. Suggest better objection handling strategies
6. Reference proven objection handling frameworks

Be thorough in identifying subtle objections and resistance."""
    
    def analyze(self, transcript: str, context: str = "", previous_analyses: List[Dict] = None) -> Dict[str, Any]:
        """Analyze objection handling in the call."""
        
        # Include RAG context about objection handling
        objection_context = context if context else ""
        
        # Include previous agent insights
        previous_insights = ""
        if previous_analyses:
            previous_insights = "\n\n## Context from other agents:\n"
            for analysis in previous_analyses:
                previous_insights += f"\n### {analysis['agent_name']}:\n{json.dumps(analysis.get('analysis', {}), indent=2)}\n"
        
        prompt = f"""Analyze objection handling in this sales call:

{transcript}

## Sales Coaching Knowledge:
{objection_context}

{previous_insights}

Identify and analyze:
1. All customer objections (explicit and implicit)
2. Objection classification
3. How each objection was handled
4. Effectiveness rating for each response
5. Missed opportunities to address concerns
6. Recommended improvements using proven frameworks

Return your analysis in JSON format:
{{
    "objections_detected": [
        {{
            "objection": "text of objection",
            "type": "price|timing|authority|need|competition|other",
            "severity": "low|medium|high",
            "how_handled": "rep's response",
            "effectiveness_score": 6,
            "missed_opportunity": "what could have been done better",
            "recommended_approach": "specific suggestion"
        }}
    ],
    "overall_objection_handling_score": 7.0,
    "unaddressed_concerns": ["concern1", ...],
    "key_improvements": ["improvement1", ...],
    "framework_recommendations": ["framework1", ...]
}}
"""
        
        logger.info(f"{self.agent_name}: Starting objection analysis...")
        
        response = self.invoke_llm(prompt)
        
        # Parse JSON response
        try:
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
            return {
                "agent_name": self.agent_name,
                "analysis": {"raw_analysis": response},
                "raw_response": response
            }
        