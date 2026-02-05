from typing import Dict, Any, List
import json
from app.agents.base_agent import BaseAgent
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SalesCoachAgent(BaseAgent):
    """Agent that evaluates sales rep performance and provides coaching feedback."""
    
    def __init__(self):
        super().__init__(agent_name="Sales Coach")
    
    def get_system_prompt(self) -> str:
        return """You are an expert sales coach with 20+ years of experience. Your role is to:

1. Evaluate sales rep performance across key dimensions
2. Identify what the rep did well (strengths)
3. Identify areas for improvement (weaknesses)
4. Assess discovery skills, product presentation, and closing techniques
5. Score the rep's performance (1-10 scale)
6. Provide specific, actionable coaching recommendations

Be constructive, specific, and data-driven in your feedback."""
    
    def analyze(self, transcript: str, context: str = "", previous_analyses: List[Dict] = None) -> Dict[str, Any]:
        """Evaluate sales rep performance."""
        
        # Include context from previous agents
        previous_insights = ""
        if previous_analyses:
            previous_insights = "\n\n## Context from other agents:\n"
            for analysis in previous_analyses:
                previous_insights += f"\n### {analysis['agent_name']}:\n{json.dumps(analysis.get('analysis', {}), indent=2)}\n"
        
        prompt = f"""Evaluate the sales rep's performance in this call:

{transcript}

{context}

{previous_insights}

Provide a detailed coaching evaluation covering:
1. Overall performance score (1-10)
2. Strengths: What did the rep do well?
3. Weaknesses: What needs improvement?
4. Discovery skills assessment
5. Product presentation quality
6. Closing effectiveness
7. Rapport and relationship building
8. Specific coaching recommendations

Return your evaluation in JSON format:
{{
    "overall_score": 7.5,
    "strengths": ["strength1", "strength2", ...],
    "weaknesses": ["weakness1", "weakness2", ...],
    "discovery_assessment": "detailed assessment",
    "presentation_quality": "assessment",
    "closing_effectiveness": "assessment",
    "rapport_building": "assessment",
    "coaching_recommendations": ["rec1", "rec2", ...],
    "top_priority_improvement": "specific area"
}}
"""
        
        logger.info(f"{self.agent_name}: Starting performance evaluation...")
        
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
            
            logger.info(f"{self.agent_name}: Evaluation completed successfully")
            
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
        
        