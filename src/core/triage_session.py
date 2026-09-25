from typing import Optional, Dict, Any, Callable
from pydantic import BaseModel
from src.core.safety_engine import SafetyEngine, SafetyOverrideResult
from src.core.parser import RobustTriageParser, TriageResponse


class TurnResult(BaseModel):
    current_turn: int
    detected_language: str
    is_completed: bool
    followup_needed: bool
    followup_question: Optional[str] = None
    triage_response: TriageResponse
    safety_override: Optional[SafetyOverrideResult] = None


class TriageSessionManager:
    """
    Manages multi-turn triage interactions across English and Hindi.
    Bounded to a hard cap of 3 turns to prevent endless loop chatter.
    """

    def __init__(
        self,
        safety_engine: Optional[SafetyEngine] = None,
        parser: Optional[RobustTriageParser] = None,
        max_turns: int = 3
    ):
        self.safety_engine = safety_engine or SafetyEngine()
        self.parser = parser or RobustTriageParser()
        self.max_turns = max_turns
        
        self.current_turn: int = 0
        self.session_history: list[dict[str, str]] = []
        self.detected_language: str = "en"
        self.is_finished: bool = False

    def reset(self) -> None:
        """Resets dialogue state for a fresh user interaction."""
        self.current_turn = 0
        self.session_history = []
        self.detected_language = "en"
        self.is_finished = False

    def detect_language(self, text: str) -> str:
        """
        Detects if input is primarily Hindi or English.
        Checks Devanagari script unicode block range or common Hindi transliterations.
        """
        # Devanagari Unicode block check (\u0900 - \u097F)
        devanagari_chars = sum(1 for char in text if '\u0900' <= char <= '\u097f')
        if devanagari_chars > 0:
            return "hi"
        
        # Hinglish / Hindi transliteration keywords
        hinglish_keywords = {"bukhar", "dard", "sirkadard", "kamzori", "pet", "khasi", "saans"}
        tokens = set(text.lower().split())
        if tokens.intersection(hinglish_keywords):
            return "hi"

        return "en"

    def _build_system_prompt(self, language: str) -> str:
        lang_name = "Hindi" if language == "hi" else "English"
        return (
            f"You are an on-device clinical triage AI assistant. "
            f"The user spoke in {lang_name}. You MUST generate your entire response strictly in {lang_name} "
            f"using clear, accessible clinical terms.\n\n"
            f"Output ONLY valid JSON matching this schema:\n"
            f"{{\n"
            f'  "symptoms_identified": ["string"],\n'
            f'  "followup_needed": boolean,\n'
            f'  "followup_question": "string or null",\n'
            f'  "severity_level": "MILD" | "MODERATE" | "EMERGENCY",\n'
            f'  "recommended_action": "string",\n'
            f'  "home_care_steps": ["string"]\n'
            f"}}\n"
        )

    def process_turn(
        self,
        user_input: str,
        llm_call_fn: Callable[[str, str], str]
    ) -> TurnResult:
        """
        Processes a single turn of interaction.
        llm_call_fn takes (system_prompt, full_dialogue_context) and returns raw text JSON.
        """
        if self.is_finished:
            raise RuntimeError("Session has already finished. Call reset() for a new query.")

        self.current_turn += 1
        
        # 1. Update detected language dynamically on every turn
        self.detected_language = self.detect_language(user_input)

        # 2. Check Core Safety Override BEFORE calling LLM
        safety_result = self.safety_engine.evaluate_symptoms(user_input)
        if safety_result:
            self.is_finished = True
            
            # Format Emergency Triage Output
            rec_action = (
                "आपातकालीन स्थिति: कृपया तुरंत 112 पर कॉल करें या नजदीकी अस्पताल जाएं।"
                if self.detected_language == "hi"
                else safety_result.recommended_action
            )
            
            emergency_triage = TriageResponse(
                symptoms_identified=[safety_result.matched_symptom],
                followup_needed=False,
                followup_question=None,
                severity_level="EMERGENCY",
                recommended_action=rec_action,
                home_care_steps=["Do not delay seeking medical attention."]
            )
            return TurnResult(
                current_turn=self.current_turn,
                detected_language=self.detected_language,
                is_completed=True,
                followup_needed=False,
                triage_response=emergency_triage,
                safety_override=safety_result
            )

        # 3. Update Conversation History
        self.session_history.append({"role": "user", "content": user_input})
        full_context = "\n".join([f"{m['role']}: {m['content']}" for m in self.session_history])
        
        system_prompt = self._build_system_prompt(self.detected_language)

        # 4. Invoke LLM via Capped Parser
        def llm_invoker(prompt: str) -> str:
            return llm_call_fn(system_prompt, prompt)

        raw_llm_output = llm_call_fn(system_prompt, full_context)
        triage_response = self.parser.parse_with_capped_retry(
            raw_llm_output,
            llm_retry_fn=llm_invoker
        )

        # 5. Turn 3 Forced Completion (Safe-by-Construction)
        if self.current_turn >= self.max_turns:
            self.is_finished = True
            
            # Capture model uncertainty BEFORE zeroing out flags
            llm_still_uncertain = triage_response.followup_needed or not triage_response.symptoms_identified
            
            triage_response.followup_needed = False
            triage_response.followup_question = None
            
            # Escalate uncertain MILD classifications to MODERATE
            if llm_still_uncertain and triage_response.severity_level == "MILD":
                triage_response.severity_level = "MODERATE"

            if self.detected_language == "hi":
                triage_response.recommended_action = (
                    "अधिक जानकारी प्राप्त नहीं हो सकी। सटीक मूल्यांकन के लिए कृपया अपने "
                    "स्थानीय डॉक्टर या स्वास्थ्य केंद्र से परामर्श लें।"
                )
            else:
                triage_response.recommended_action = (
                    "Maximum evaluation turns reached. Please consult a local healthcare "
                    "professional for a complete clinical evaluation."
                )

            return TurnResult(
                current_turn=self.current_turn,
                detected_language=self.detected_language,
                is_completed=True,
                followup_needed=False,
                triage_response=triage_response
            )

        # Turns 1 or 2: Check if LLM completed assessment early
        if not triage_response.followup_needed:
            self.is_finished = True

        if triage_response.followup_question:
            self.session_history.append({
                "role": "assistant",
                "content": triage_response.followup_question
            })

        return TurnResult(
            current_turn=self.current_turn,
            detected_language=self.detected_language,
            is_completed=self.is_finished,
            followup_needed=triage_response.followup_needed,
            followup_question=triage_response.followup_question,
            triage_response=triage_response
        )
