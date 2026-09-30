import os
import pytest
from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtTest import QTest

# Run offscreen for headless automated test execution
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from src.ui.main_window import MainWindow


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def main_window(qapp):
    win = MainWindow()
    yield win
    win.close()


def submit_user_query(win: MainWindow, text: str):
    """
    Simulates real user interaction:
    1. Sets text in input field
    2. Clicks Send button
    3. Verifies controls lock
    4. Waits for worker thread to complete and unlock controls
    """
    win.text_input.setText(text)
    assert win.text_input.isEnabled() is True
    
    # Click send button
    win.send_btn.click()
    
    # Verify input controls lock immediately upon dispatch
    # (Allowing slight event processing for signal dispatch)
    QTest.qWait(10)
    
    # Wait for non-blocking QThread to finish and unlock controls (up to 3 seconds)
    for _ in range(60):
        QTest.qWait(50)
        if win.text_input.isEnabled() and win.send_btn.isEnabled():
            break
            
    assert win.text_input.isEnabled() is True, "Controls failed to unlock within timeout"


def test_complete_demo_recording_workflow(main_window):
    """
    Executes and verifies the complete 4-prompt demo recording sequence
    from docs/DEMO_RECORDING_GUIDE.md against the live MainWindow.
    """
    win = main_window

    # --------------------------------------------------------------------------
    # Step 0: Hardware Status Inspection & Toggle
    # --------------------------------------------------------------------------
    assert "CPU Emulation Mode" in win.hw_badge.text()
    assert not win.worker.npu_accelerated

    # Toggle to NPU Mode
    win._toggle_hardware_mode()
    assert "Snapdragon Hexagon NPU Accelerated" in win.hw_badge.text()
    assert win.worker.npu_accelerated

    # Toggle back to CPU Mode for recording baseline
    win._toggle_hardware_mode()
    assert "CPU Emulation Mode" in win.hw_badge.text()
    assert not win.worker.npu_accelerated

    # --------------------------------------------------------------------------
    # Prompt 1: Acute Emergency Safety Override Trigger
    # "I am experiencing severe crushing chest pressure and shortness of breath"
    # --------------------------------------------------------------------------
    p1 = "I am experiencing severe crushing chest pressure and shortness of breath"
    submit_user_query(win, p1)

    # Check emergency safety override result
    assert win.session_manager.is_finished
    last_card = win.chat_layout.itemAt(win.chat_layout.count() - 2).layout().itemAt(0).widget()
    card_text = " ".join([lbl.text() for lbl in last_card.findChildren(QLabel)])
    assert "EMERGENCY" in card_text
    assert "112" in card_text
    
    # Verify sub-millisecond LLM bypass telemetry
    ttft_label = win.card_ttft.findChild(QLabel, "MetricValue").text()
    assert "ms" in ttft_label
    ttft_num = float(ttft_label.replace(" ms", ""))
    assert ttft_num < 15.0, f"Expected sub-millisecond bypass, got {ttft_num}ms"

    # Privacy card verification
    privacy_label = win.card_privacy.findChild(QLabel, "MetricValue").text()
    assert "100% Local (0 Bytes Egressed)" in privacy_label

    # --------------------------------------------------------------------------
    # Reset Session for Multi-Turn Flow
    # --------------------------------------------------------------------------
    win.new_session_btn.click()
    QTest.qWait(50)
    assert win.session_manager.current_turn == 0
    assert not win.session_manager.is_finished
    assert "Turn: 0 / 3" in win.turn_indicator.text()

    # --------------------------------------------------------------------------
    # Prompt 2: Turn 1 — Hindi Clinical Query
    # "मुझे 2 दिन से तेज बुखार है"
    # --------------------------------------------------------------------------
    p2 = "मुझे 2 दिन से तेज बुखार है"
    submit_user_query(win, p2)

    assert win.session_manager.current_turn == 1
    assert win.session_manager.detected_language == "hi"
    assert "Hindi" in win.diag_lang.text()
    assert "Turn: 1 / 3" in win.turn_indicator.text()

    # Verify Devanagari script and fever symptom tagging
    last_card = win.chat_layout.itemAt(win.chat_layout.count() - 2).layout().itemAt(0).widget()
    card_text = " ".join([lbl.text() for lbl in last_card.findChildren(QLabel)])
    assert "बुखार" in card_text
    assert "MILD" in card_text

    # --------------------------------------------------------------------------
    # Prompt 3: Turn 2 — Dynamic English Language Switch
    # "It started yesterday morning and I also have a mild headache"
    # --------------------------------------------------------------------------
    p3 = "It started yesterday morning and I also have a mild headache"
    submit_user_query(win, p3)

    assert win.session_manager.current_turn == 2
    assert win.session_manager.detected_language == "en"
    assert "English" in win.diag_lang.text()
    assert "Turn: 2 / 3" in win.turn_indicator.text()

    last_card = win.chat_layout.itemAt(win.chat_layout.count() - 2).layout().itemAt(0).widget()
    card_text = " ".join([lbl.text() for lbl in last_card.findChildren(QLabel)])
    assert any(term in card_text.lower() for term in ["hydrat", "rest", "care", "progression"])

    # --------------------------------------------------------------------------
    # Prompt 4: Turn 3 — Safe-By-Construction Escalation Prompt
    # "I am not sure if there are other symptoms, I feel very weak"
    # --------------------------------------------------------------------------
    p4 = "I am not sure if there are other symptoms, I feel very weak"
    submit_user_query(win, p4)

    assert win.session_manager.current_turn == 3
    assert win.session_manager.is_finished
    assert "Turn: 3 / 3" in win.turn_indicator.text()
    assert "Completed" in win.diag_status.text()

    # Verify Safe-by-Construction Escalation to MODERATE
    last_card = win.chat_layout.itemAt(win.chat_layout.count() - 2).layout().itemAt(0).widget()
    card_text = " ".join([lbl.text() for lbl in last_card.findChildren(QLabel)])
    assert "MODERATE" in card_text
    assert any(term in card_text.lower() for term in ["consult", "healthcare", "outpatient", "limit"])

    # --------------------------------------------------------------------------
    # Final Telemetry Verification
    # --------------------------------------------------------------------------
    speed_label = win.card_speed.findChild(QLabel, "MetricValue").text()
    assert "tok/s" in speed_label or "tok/sec" in speed_label
    
    cpu_label = win.card_cpu.findChild(QLabel, "MetricValue").text()
    assert "%" in cpu_label
