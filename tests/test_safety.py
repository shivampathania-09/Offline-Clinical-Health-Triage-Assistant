import pytest
from src.core.safety_engine import SafetyEngine

@pytest.fixture
def safety_engine():
    return SafetyEngine()

def test_true_emergency_triggers_override(safety_engine):
    inputs = [
        "Patient is experiencing severe chest pain and dizziness",
        "Sudden weakness on left side with facial drooping",
        "Worst headache of life starting 10 mins ago",
        "Coughing up blood with blue lips"
    ]
    for text in inputs:
        result = safety_engine.evaluate_symptoms(text)
        assert result is not None, f"Failed to catch emergency in: {text}"
        assert result.override_applied is True
        assert result.severity_level == "EMERGENCY"

def test_similar_words_not_falsely_negated(safety_engine):
    """Guards against false negatives caused by substring matches like 'no' in 'nonspecific'."""
    inputs = [
        "Nonspecific chest pain reported by patient",
        "Chest pain, unresolved since this morning",
        "Known chest pain worsening over the day",
    ]
    for text in inputs:
        result = safety_engine.evaluate_symptoms(text)
        assert result is not None, f"False negative (missed emergency) in: {text}"
        assert result.severity_level == "EMERGENCY"

def test_negated_emergency_passes_to_llm(safety_engine):
    inputs = [
        "Patient reports mild fever and cough but no chest pain",
        "Denies slurred speech or facial drooping",
        "Has high blood pressure without worst headache",
        "Doctor ruled out chest pain during last visit",
        "Coughing symptoms present, chest pain resolved"
    ]
    for text in inputs:
        result = safety_engine.evaluate_symptoms(text)
        assert result is None, f"Incorrectly triggered emergency override for negated symptom in: {text}"
