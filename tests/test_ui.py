import os
import pytest
from unittest.mock import MagicMock

# Ensure headless execution for testing environments
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtWidgets import QApplication, QLabel
from src.ui.main_window import MainWindow, TriageWorker
from src.core.triage_session import TriageSessionManager


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def window(qapp):
    win = MainWindow()
    yield win
    win.close()


def test_window_initialization(window):
    assert "Offline Clinical Health Triage Assistant" in window.windowTitle()
    # Check font family includes Devanagari support
    font_families = window.font().families()
    assert any("Devanagari" in f or "Segoe UI" in f for f in font_families)


def test_hardware_status_toggle(window):
    # Initial is CPU mode
    assert "CPU Emulation Mode" in window.hw_badge.text()
    assert window.worker.npu_accelerated is False

    # Toggle to NPU mode
    window._toggle_hardware_mode()
    assert "Snapdragon Hexagon NPU Accelerated" in window.hw_badge.text()
    assert window.worker.npu_accelerated is True

    # Toggle back to CPU mode
    window._toggle_hardware_mode()
    assert "CPU Emulation Mode" in window.hw_badge.text()
    assert window.worker.npu_accelerated is False


def test_input_control_locking_and_unlocking(window):
    # Lock all controls (text input, send, audio, and New Session button)
    window.lock_all_controls()
    assert window.text_input.isEnabled() is False
    assert window.send_btn.isEnabled() is False
    assert window.audio_btn.isEnabled() is False
    assert window.new_session_btn.isEnabled() is False
    assert "Evaluating" in window.status_label.text()

    # Finished signal unlocks all controls
    window.unlock_all_controls()
    assert window.text_input.isEnabled() is True
    assert window.send_btn.isEnabled() is True
    assert window.audio_btn.isEnabled() is True
    assert window.new_session_btn.isEnabled() is True
    assert "Ready" in window.status_label.text()


def test_worker_error_handling_and_finished_signal():
    """Verifies that an error in TriageWorker emits error_occurred and ALWAYS finished."""
    session_manager = MagicMock()
    session_manager.process_turn.side_effect = RuntimeError("Simulated device failure")

    worker = TriageWorker(session_manager)
    
    error_received = []
    finished_called = []

    worker.error_occurred.connect(lambda msg: error_received.append(msg))
    worker.finished.connect(lambda: finished_called.append(True))

    worker.process_query("Test input", False)

    assert len(error_received) == 1
    assert "Processing failed — please try again" in error_received[0]
    assert len(finished_called) == 1  # Guaranteed by finally block


def test_new_session_resets_dialogue_and_manager(window):
    window.session_manager.current_turn = 2
    window.session_manager.session_history = [{"role": "user", "content": "fever"}]
    window.session_manager.is_finished = True

    window.on_new_session_clicked()

    assert window.session_manager.current_turn == 0
    assert window.session_manager.session_history == []
    assert window.session_manager.is_finished is False
    assert "Turn: 0 / 3" in window.turn_indicator.text()


def test_severity_badge_rendering(window):
    mild_card_data = {
        "severity_level": "MILD",
        "symptoms_identified": ["fever"],
        "recommended_action": "Rest",
        "home_care_steps": ["Hydrate"],
        "current_turn": 1,
        "is_completed": False
    }
    window.add_assistant_triage_card(mild_card_data)
    assert window.chat_layout.count() > 1

    emergency_card_data = {
        "severity_level": "EMERGENCY",
        "symptoms_identified": ["chest pain"],
        "recommended_action": "Call 112 immediately",
        "home_care_steps": [],
        "current_turn": 1,
        "is_completed": True,
        "safety_override": True
    }
    window.add_assistant_triage_card(emergency_card_data)
    assert "Turn: 1 / 3" in window.turn_indicator.text()


def test_telemetry_display_update(window):
    telemetry = {
        "asr_ms": 112.5,
        "ttft_ms": 34.2,
        "tokens_sec": 42.1,
        "peak_cpu": 12.4,
        "privacy_status": "100% Local (0 Bytes Egressed)",
        "detected_lang": "HI",
        "current_turn": 2,
        "is_completed": False
    }
    window._update_telemetry_display(telemetry)
    metric_val = window.card_asr.findChild(QLabel, "MetricValue")
    assert metric_val is not None
    assert "112.5 ms" in metric_val.text()
    
    privacy_val = window.card_privacy.findChild(QLabel, "MetricValue")
    assert privacy_val is not None
    assert "100% Local" in privacy_val.text()
    assert "Hindi" in window.diag_lang.text()


def test_legal_disclaimer_footer(window):
    central = window.centralWidget()
    found_disclaimer = False
    for child in central.findChildren(type(window.hw_badge)):
        if "112" in child.text() and "diagnosis" in child.text():
            found_disclaimer = True
            break
    assert found_disclaimer is True
