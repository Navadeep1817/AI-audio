from typing import Dict, Any, List
import json
from app.agents.base_agent import BaseAgent
from app.models import SalesReport, AgentInsight
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SupervisorAgent(BaseAgent):
    """Orchestrates multiple agents and synthesizes final report."""
    
    def __init__(self):
        super().__init__(agent_name="Supervisor")
    
    def get_system_prompt(self) -> str:
        return """You are a senior sales director who synthesizes insights from multiple specialists. Your role is to:

1. Review analyses from all specialist agents
2. Synthesize findings into a coherent narrative
3. Prioritize the most impactful insights
4. Create actionable recommendations
5. Produce an executive summary
6. Assign an overall performance score

Be concise, prioritize action items, and focus on high-impact improvements."""
    
    def synthesize_report(self, transcript: str, agent_analyses: List[Dict]) -> SalesReport:
        """
        Synthesize all agent analyses into final report.
        
        Args:
            transcript: Original call transcript
            agent_analyses: List of analyses from all agents
            
        Returns:
            SalesReport object
        """
        
        # Compile all agent insights
        compiled_insights = "\n\n".join([
            f"## {analysis['agent_name']}\n{json.dumps(analysis.get('analysis', {}), indent=2)}"
            for analysis in agent_analyses
        ])
        
        prompt = f"""Review these specialist analyses of a sales call:

{compiled_insights}

Synthesize a final sales improvement report with:
1. Executive summary (2-3 sentences)
2. Overall performance score (1-10)
3. Top 5 strengths
4. Top 5 weaknesses
5. Top 5 missed opportunities
6. Top 5 recommended actions (prioritized)

Return in JSON format:
{{
    "executive_summary": "concise summary",
    "overall_score": 7.5,
    "top_strengths": ["strength1", ...],
    "top_weaknesses": ["weakness1", ...],
    "missed_opportunities": ["opp1", ...],
    "recommended_actions": ["action1", ...]
}}
"""
        
        logger.info(f"{self.agent_name}: Synthesizing final report...")
        
        response = self.invoke_llm(prompt)
        
        # Parse response
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()
            
            synthesis = json.loads(json_str)
            
            # Build agent insights
            agent_insights = []
            for analysis in agent_analyses:
                agent_data = analysis.get('analysis', {})
                
                # Extract key points
                key_points = []
                if 'summary' in agent_data:
                    key_points.append(agent_data['summary'])
                if 'key_improvements' in agent_data:
                    key_points.extend(agent_data['key_improvements'][:3])
                
                agent_insights.append(AgentInsight(
                    agent_name=analysis['agent_name'],
                    analysis=analysis.get('raw_response', '')[:500],  # Truncate
                    key_points=key_points[:5],
                    score=agent_data.get('overall_score') or agent_data.get('overall_objection_handling_score')
                ))
            
            # Extract objections from Objection Expert
            objections = []
            for analysis in agent_analyses:
                if analysis['agent_name'] == "Objection Expert":
                    objections_data = analysis.get('analysis', {}).get('objections_detected', [])
                    for obj in objections_data:
                        objections.append({
                            "objection": obj.get('objection', ''),
                            "type": obj.get('type', ''),
                            "handling": obj.get('how_handled', '')
                        })
            
            # Create final report
            report = SalesReport(
                job_id="",  # Will be set by caller
                call_summary=synthesis.get('executive_summary', ''),
                overall_score=synthesis.get('overall_score', 5.0),
                strengths=synthesis.get('top_strengths', []),
                weaknesses=synthesis.get('top_weaknesses', []),
                missed_opportunities=synthesis.get('missed_opportunities', []),
                objections_detected=objections,
                recommended_actions=synthesis.get('recommended_actions', []),
                agent_insights=agent_insights
            )
            
            logger.info(f"{self.agent_name}: Report synthesis completed")
            
            return report
        
        except Exception as e:
            logger.error(f"Error synthesizing report: {e}")
            raise
    
    def analyze(self, transcript: str, context: str = "", previous_analyses: List[Dict] = None) -> Dict[str, Any]:
        """Not used directly - use synthesize_report instead."""
        raise NotImplementedError("Use synthesize_report method")   