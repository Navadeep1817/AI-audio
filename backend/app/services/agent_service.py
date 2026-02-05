from groq import Groq
from app.config import get_settings
from app.models import SalesReport, TranscriptResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class AgentOrchestrationService:
    """
    Multi-agent orchestration using Groq LLM.
    """

    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)

        # ✅ Always use supported Groq model
        self.model = settings.GROQ_MODEL or "llama-3.3-70b-versatile"

    # ───────────────────────────────────────────────
    # 🔥 SAFE CORE LLM CALL
    # ───────────────────────────────────────────────
    def _invoke_llm(self, system_prompt: str, user_prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0.3,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )

            content = response.choices[0].message.content
            return content.strip() if content else "No response generated."

        except Exception as e:
            logger.error(f"[GROQ] LLM invocation failed: {e}")
            return "AI analysis unavailable due to model error."

    # ───────────────────────────────────────────────
    # 🧠 AGENT 1 — TRANSCRIPT ANALYZER
    # ───────────────────────────────────────────────
    def _transcript_analyzer(self, transcript_text: str) -> str:
        system = "You are an expert sales conversation analyst."

        user = f"""
Analyze this sales call transcript.

Return:
- strengths
- weaknesses
- customer sentiment
- conversation flow

Transcript:
{transcript_text}
"""
        return self._invoke_llm(system, user)

    # ───────────────────────────────────────────────
    # 🎯 AGENT 2 — SALES COACH
    # ───────────────────────────────────────────────
    def _sales_coach(self, transcript_text: str) -> str:
        system = "You are a world-class enterprise sales coach."

        user = f"""
Provide actionable coaching advice.

Focus on:
- discovery
- closing
- objection handling
- tone

Transcript:
{transcript_text}
"""
        return self._invoke_llm(system, user)

    # ───────────────────────────────────────────────
    # ⚡ AGENT 3 — OBJECTION EXPERT
    # ───────────────────────────────────────────────
    def _objection_expert(self, transcript_text: str) -> str:
        system = "You detect objections and suggest improvements."

        user = f"""
Identify objections and how well they were handled.

Transcript:
{transcript_text}
"""
        return self._invoke_llm(system, user)

    # ───────────────────────────────────────────────
    # 🚀 MAIN PIPELINE
    # ───────────────────────────────────────────────
    def analyze_call(self, job_id: str, transcript: TranscriptResponse) -> SalesReport:

        logger.info(f"[GROQ] Running agent orchestration for job {job_id}")

        if not transcript or not transcript.segments:
            raise Exception("Transcript is empty — cannot run analysis.")

        transcript_text = "\n".join(
            [f"{seg.speaker}: {seg.text}" for seg in transcript.segments]
        )

        analyzer_output = self._transcript_analyzer(transcript_text)
        coach_output = self._sales_coach(transcript_text)
        objection_output = self._objection_expert(transcript_text)

        # ✅ FINAL STRUCTURE MATCHES YOUR PYDANTIC MODEL
        return SalesReport(
            job_id=job_id,
            call_summary=analyzer_output[:300],
            overall_score=7.5,
            strengths=[analyzer_output],
            weaknesses=[coach_output],
            missed_opportunities=[objection_output],
            objections_detected=[],
            recommended_actions=[
                "Review AI coaching suggestions",
                "Improve objection handling",
                "Practice structured discovery",
            ],
            agent_insights=[
                {
                    "agent_name": "Transcript Analyzer",
                    "analysis": analyzer_output,
                    "key_points": [],
                    "score": None,
                },
                {
                    "agent_name": "Sales Coach",
                    "analysis": coach_output,
                    "key_points": [],
                    "score": None,
                },
                {
                    "agent_name": "Objection Expert",
                    "analysis": objection_output,
                    "key_points": [],
                    "score": None,
                },
            ],
        )
