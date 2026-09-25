import pytest
import json
from src.core.triage_session import TriageSessionManager


@pytest.fixture
def session_manager():
    return TriageSessionManager(max_turns=3)


def test_single_turn_immediate_completion(session_manager):
    user_input = "I have had a mild fever of 100F for 2 days without any other symptoms."

    def mock_llm_call(system_prompt: str, context: str) -> str:
        assert "The user spoke in English" in system_prompt
        return json.dumps({
            "symptoms_identified": ["fever"],
            "followup_needed": False,
            "followup_question": None,
            "severity_level": "MILD",
            "recommended_action": "Rest and drink plenty of fluids.",
            "home_care_steps": ["Monitor temperature", "Stay hydrated"]
        })

    result = session_manager.process_turn(user_input, mock_llm_call)

    assert result.current_turn == 1
    assert result.detected_language == "en"
    assert result.is_completed is True
    assert result.followup_needed is False
    assert result.triage_response.severity_level == "MILD"


def test_turn_3_escalates_severity_when_llm_still_uncertain(session_manager):
    """
    Verifies that if the LLM identifies symptoms but remains uncertain (followup_needed=True)
    at Turn 3, severity escalates from MILD to MODERATE.
    """
    def mock_llm_turn_1(system_prompt, context):
        return json.dumps({
            "symptoms_identified": ["headache"],
            "followup_needed": True,
            "followup_question": "How long have you had this headache?",
            "severity_level": "MILD",
            "recommended_action": "Gathering more details.",
            "home_care_steps": []
        })

    def mock_llm_turn_2(system_prompt, context):
        return json.dumps({
            "symptoms_identified": ["headache"],
            "followup_needed": True,
            "followup_question": "Is it accompanied by nausea?",
            "severity_level": "MILD",
            "recommended_action": "Gathering more details.",
            "home_care_steps": []
        })

    def mock_llm_turn_3(system_prompt, context):
        return json.dumps({
            "symptoms_identified": ["headache"],
            "followup_needed": True,  # Model still wants info
            "followup_question": "Is it throbbing?",
            "severity_level": "MILD",
            "recommended_action": "Gathering details.",
            "home_care_steps": []
        })

    session_manager.process_turn("I have a headache.", mock_llm_turn_1)
    session_manager.process_turn("A couple hours.", mock_llm_turn_2)
    result = session_manager.process_turn("No fever.", mock_llm_turn_3)

    assert result.current_turn == 3
    assert result.is_completed is True
    assert result.triage_response.severity_level == "MODERATE"


def test_bidirectional_language_switching(session_manager):
    """Verifies that language detection updates dynamically when switching from Hindi to English."""
    def mock_llm(system_prompt, context):
        return json.dumps({
            "symptoms_identified": ["fever"],
            "followup_needed": True,
            "followup_question": "Details?",
            "severity_level": "MILD",
            "recommended_action": "Rest",
            "home_care_steps": []
        })

    # Turn 1: Hindi
    res1 = session_manager.process_turn("मुझे बुखार है", mock_llm)
    assert res1.detected_language == "hi"

    # Turn 2: English (Language should switch back)
    res2 = session_manager.process_turn("It started yesterday morning", mock_llm)
    assert res2.detected_language == "en"


def test_safety_override_bypasses_dialogue_state(session_manager):
    emergency_input = "I am having severe chest pain"
    llm_was_called = False

    def mock_llm_call(system_prompt: str, context: str) -> str:
        nonlocal llm_was_called
        llm_was_called = True
        return ""

    result = session_manager.process_turn(emergency_input, mock_llm_call)

    assert llm_was_called is False
    assert result.is_completed is True
    assert result.safety_override is not None
    assert result.triage_response.severity_level == "EMERGENCY"
