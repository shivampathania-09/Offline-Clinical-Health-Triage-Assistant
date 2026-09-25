import pytest
from unittest.mock import MagicMock, patch
from tests.benchmark_harness import BenchmarkHarness

def test_harness_simulated_mode():
    harness = BenchmarkHarness(npu_inference_fn=None)
    assert harness.npu_mode == "SIMULATED"

def test_harness_real_mode():
    mock_fn = MagicMock(return_value=45.2)
    harness = BenchmarkHarness(npu_inference_fn=mock_fn)
    assert harness.npu_mode == "REAL"
    latency = harness._run_npu_inference("Patient reports slight dizziness.")
    assert latency == 45.2
    mock_fn.assert_called_once_with("Patient reports slight dizziness.")

def test_load_samples_existing(tmp_path):
    sample_file = tmp_path / "samples.json"
    sample_file.write_text('["Prompt 1", "Prompt 2"]')
    harness = BenchmarkHarness(sample_file=str(sample_file))
    samples = harness.load_samples()
    assert samples == ["Prompt 1", "Prompt 2"]

def test_load_samples_fallback():
    harness = BenchmarkHarness(sample_file="nonexistent_samples.json")
    samples = harness.load_samples()
    assert len(samples) == 30
    assert samples[0] == "Sample patient symptom description 1."

@patch("tests.benchmark_harness.GROQ_API_KEY", None)
def test_query_live_groq_api_fallback():
    harness = BenchmarkHarness()
    latency, was_live = harness._query_live_groq_api("Test prompt")
    assert was_live is False
    assert latency > 0
