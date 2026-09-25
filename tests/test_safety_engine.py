import pytest
from src.core.safety_engine import SafetyEngine, SafetyOverrideResult

@pytest.fixture
def engine():
    return SafetyEngine()

def test_unnegated_emergency_symptom(engine):
    text = "Patient presents with crushing chest pressure and dizziness."
    result = engine.evaluate_symptoms(text)
    assert result is not None
    assert isinstance(result, SafetyOverrideResult)
    assert result.severity_level == "EMERGENCY"
    assert result.override_applied is True
    assert result.matched_symptom == "crushing chest pressure"
    assert "CRITICAL SAFETY OVERRIDE" in result.recommended_action
    assert "112" in result.recommended_action

def test_stroke_emergency(engine):
    text = "Possible stroke observed with slurred speech."
    result = engine.evaluate_symptoms(text)
    assert result is not None
    assert result.matched_symptom in ["stroke", "slurred speech"]

def test_single_word_negation(engine):
    # 'no', 'not', 'denies', 'without', 'absent', 'resolved'
    negation_cases = [
        "Patient has no chest pain today.",
        "Patient is not experiencing shortness of breath.",
        "Patient denies chest pain.",
        "Arrived without slurred speech or confusion.",
        "Absent facial drooping upon exam.",
        "Resolved worst headache reported earlier."
    ]
    for case in negation_cases:
        result = engine.evaluate_symptoms(case)
        assert result is None, f"Expected None for negated case: '{case}', got {result}"

def test_multi_word_negation(engine):
    # 'free of', 'ruled out', 'negative for'
    multi_word_cases = [
        "Patient is free of chest pain.",
        "Myocardial infarction was ruled out chest pain.",
        "Tested negative for stroke symptoms."
    ]
    for case in multi_word_cases:
        result = engine.evaluate_symptoms(case)
        assert result is None, f"Expected None for multi-word negated case: '{case}', got {result}"

def test_non_negation_substring_protection(engine):
    # Words like 'nonspecific', 'noticeable', 'knot' shouldn't falsely trigger negation
    text = "Patient reports nonspecific chest pain."
    result = engine.evaluate_symptoms(text)
    assert result is not None
    assert result.matched_symptom == "chest pain"

def test_negation_out_of_window(engine):
    # Negation word earlier than 5 tokens before the symptom should not negate
    # Window size is 5 tokens
    text = "No previous history recorded during initial triage evaluation chest pain."
    result = engine.evaluate_symptoms(text)
    assert result is not None
    assert result.matched_symptom == "chest pain"

def test_normal_benign_symptoms(engine):
    text = "Patient has mild fever, cough, and running nose for two days."
    result = engine.evaluate_symptoms(text)
    assert result is None
