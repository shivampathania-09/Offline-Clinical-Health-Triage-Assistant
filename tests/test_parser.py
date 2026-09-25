import json
import pytest
from unittest.mock import MagicMock
from src.core.parser import RobustTriageParser, TriageResponse

@pytest.fixture
def parser():
    return RobustTriageParser()

@pytest.fixture
def valid_triage_dict():
    return {
        "symptoms_identified": ["mild cough", "sore throat"],
        "followup_needed": True,
        "followup_question": "How long have you had the sore throat?",
        "severity_level": "MILD",
        "recommended_action": "Drink warm liquids and rest. Contact a clinic if symptoms worsen.",
        "home_care_steps": ["Hydration", "Throat lozenges", "Adequate rest"]
    }

def test_clean_direct_json(parser, valid_triage_dict):
    raw_output = json.dumps(valid_triage_dict)
    response = parser.parse_with_capped_retry(raw_output)
    assert isinstance(response, TriageResponse)
    assert response.severity_level == "MILD"
    assert response.symptoms_identified == ["mild cough", "sore throat"]
    assert response.followup_needed is True

def test_markdown_code_block_json(parser, valid_triage_dict):
    raw_output = f"```json\n{json.dumps(valid_triage_dict)}\n```"
    response = parser.parse_with_capped_retry(raw_output)
    assert isinstance(response, TriageResponse)
    assert response.severity_level == "MILD"
    assert response.home_care_steps == ["Hydration", "Throat lozenges", "Adequate rest"]

def test_conversational_wrapped_json(parser, valid_triage_dict):
    raw_output = f"Here is the evaluation:\n\n```\n{json.dumps(valid_triage_dict)}\n```\nHope this helps!"
    response = parser.parse_with_capped_retry(raw_output)
    assert isinstance(response, TriageResponse)
    assert response.recommended_action == valid_triage_dict["recommended_action"]

def test_invalid_json_without_retry_fn(parser):
    raw_output = "I cannot provide a structured evaluation right now."
    response = parser.parse_with_capped_retry(raw_output)
    assert response == parser.fallback_response
    assert response.severity_level == "MODERATE"
    assert response.symptoms_identified == ["Unspecified symptoms"]

def test_invalid_json_with_successful_retry(parser, valid_triage_dict):
    mock_retry_fn = MagicMock(return_value=json.dumps(valid_triage_dict))
    raw_output = "Malformed JSON: {symptoms: cough"
    
    response = parser.parse_with_capped_retry(raw_output, llm_retry_fn=mock_retry_fn)
    
    assert mock_retry_fn.call_count == 1
    assert isinstance(response, TriageResponse)
    assert response.severity_level == "MILD"

def test_invalid_json_with_failing_retry_fallback(parser):
    mock_retry_fn = MagicMock(return_value="Still not valid JSON!")
    raw_output = "Malformed JSON"
    
    response = parser.parse_with_capped_retry(raw_output, llm_retry_fn=mock_retry_fn)
    
    assert mock_retry_fn.call_count == 1
    assert response == parser.fallback_response

def test_schema_validation_error_triggers_fallback(parser):
    # Invalid severity_level: "UNKNOWN"
    invalid_data = {
        "symptoms_identified": ["fever"],
        "followup_needed": False,
        "followup_question": None,
        "severity_level": "UNKNOWN",
        "recommended_action": "Rest",
        "home_care_steps": ["Drink water"]
    }
    raw_output = json.dumps(invalid_data)
    response = parser.parse_with_capped_retry(raw_output, llm_retry_fn=None)
    assert response == parser.fallback_response
