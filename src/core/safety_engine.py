import re
from typing import Optional
from pydantic import BaseModel

class SafetyOverrideResult(BaseModel):
    severity_level: str = "EMERGENCY"
    recommended_action: str
    override_applied: bool = True
    matched_symptom: str

class SafetyEngine:
    def __init__(self):
        # High-risk emergency keywords requiring immediate care
        self.emergency_patterns = [
            r"chest pain",
            r"crushing chest pressure",
            r"slurred speech",
            r"facial drooping",
            r"sudden weakness",
            r"worst headache",
            r"severe shortness of breath",
            r"uncontrolled bleeding",
            r"blue lips",
            r"stroke"
        ]
        
        # Explicit single-token and multi-word negation phrases
        self.negation_terms = {
            "no", "not", "denies", "without", "absent", 
            "free of", "ruled out", "resolved", "negative for"
        }

    def _is_negated(self, text: str, match_start: int, window_size: int = 5, match_end: Optional[int] = None) -> bool:
        """
        Checks if any negation term exists in the preceding or following N tokens using strict
        token and bigram matching to avoid false substring matches (e.g., 'no' in 'nonspecific').
        """
        preceding_text = text[:match_start].lower()
        tokens = re.findall(r'\b\w+\b', preceding_text)
        
        lookback_tokens = tokens[-window_size:] if len(tokens) >= window_size else tokens
        if lookback_tokens:
            # Construct exact 2-token phrases (bigrams) for multi-word terms like "ruled out"
            bigrams = [" ".join(lookback_tokens[i:i+2]) for i in range(len(lookback_tokens) - 1)]

            for term in self.negation_terms:
                if " " in term:
                    if term in bigrams:
                        return True
                else:
                    if term in lookback_tokens:
                        return True

        # Check following tokens for post-symptom negation (e.g. 'chest pain resolved', 'facial drooping absent')
        if match_end is not None:
            following_text = text[match_end:].lower()
        else:
            following_text = text[match_start:].lower()
            tokens_after = re.findall(r'\b\w+\b', following_text)
            following_text = " ".join(tokens_after[1:]) if len(tokens_after) > 1 else ""

        post_tokens = re.findall(r'\b\w+\b', following_text)
        lookahead_tokens = post_tokens[:window_size] if len(post_tokens) >= window_size else post_tokens
        if lookahead_tokens:
            post_bigrams = [" ".join(lookahead_tokens[i:i+2]) for i in range(len(lookahead_tokens) - 1)]

            for term in self.negation_terms:
                if " " in term:
                    if term in post_bigrams:
                        return True
                else:
                    if term in lookahead_tokens:
                        return True
                    
        return False

    def evaluate_symptoms(self, text: str) -> Optional[SafetyOverrideResult]:
        """
        Evaluates input text. Returns SafetyOverrideResult if an un-negated emergency 
        symptom is detected, otherwise returns None to pass to the LLM.
        """
        text_lower = text.lower()
        
        for pattern in self.emergency_patterns:
            for match in re.finditer(pattern, text_lower):
                start_pos = match.start()
                end_pos = match.end()
                if not self._is_negated(text_lower, start_pos, match_end=end_pos):
                    return SafetyOverrideResult(
                        recommended_action=(
                            "CRITICAL SAFETY OVERRIDE: Emergency symptoms detected ("
                            f"'{match.group()}'). Please call emergency services (112) or "
                            "go to the nearest emergency department immediately."
                        ),
                        matched_symptom=match.group()
                    )
        return None
