import json
import re
from typing import Literal, Optional, List
from pydantic import BaseModel, ValidationError

class TriageResponse(BaseModel):
    symptoms_identified: List[str]
    followup_needed: bool
    followup_question: Optional[str] = None
    severity_level: Literal["MILD", "MODERATE", "EMERGENCY"]
    recommended_action: str
    home_care_steps: List[str]

class RobustTriageParser:
    def __init__(self):
        self.fallback_response = TriageResponse(
            symptoms_identified=["Unspecified symptoms"],
            followup_needed=False,
            followup_question=None,
            severity_level="MODERATE",
            recommended_action=(
                "Unable to parse structured response safely. Please consult a qualified "
                "healthcare professional or local clinic for clinical evaluation."
            ),
            home_care_steps=["Monitor symptoms and seek medical advice if condition worsens."]
        )

    def _clean_json_string(self, raw_text: str) -> str:
        """Extracts JSON substring from raw text or markdown code blocks."""
        cleaned = re.sub(r'```json\s*', '', raw_text)
        cleaned = re.sub(r'```\s*', '', cleaned)
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match:
            return match.group(0).strip()
        return raw_text.strip()

    def parse_with_capped_retry(self, raw_llm_output: str, llm_retry_fn=None) -> TriageResponse:
        """
        Parses LLM output into Pydantic schema. 
        Hard-capped at 1 retry; falls back to deterministic safe response on second failure.
        """
        # Attempt 1: Initial parse
        try:
            json_str = self._clean_json_string(raw_llm_output)
            parsed_dict = json.loads(json_str)
            return TriageResponse(**parsed_dict)
        except (json.JSONDecodeError, ValidationError):
            if not llm_retry_fn:
                return self.fallback_response

        # Attempt 2: Capped 1-Time Retry Loop
        try:
            repair_prompt = (
                "Your previous output was invalid JSON. Re-format strictly into this schema:\n"
                "{\n"
                '  "symptoms_identified": ["string"],\n'
                '  "followup_needed": true/false,\n'
                '  "followup_question": "string or null",\n'
                '  "severity_level": "MILD" | "MODERATE" | "EMERGENCY",\n'
                '  "recommended_action": "string",\n'
                '  "home_care_steps": ["string"]\n'
                "}\n"
                "Do NOT include commentary, markdown, or text outside the JSON object."
            )
            repaired_raw_output = llm_retry_fn(repair_prompt)
            json_str = self._clean_json_string(repaired_raw_output)
            parsed_dict = json.loads(json_str)
            return TriageResponse(**parsed_dict)
        except Exception:
            return self.fallback_response
