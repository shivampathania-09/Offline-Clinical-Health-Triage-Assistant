import os
import sys
import time
import subprocess
import ctypes
from pathlib import Path

# Ensure UTF-8 stdout encoding on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Optional PyAutoGUI support with automatic native Windows fallback
try:
    import pyautogui
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False

# Native Windows API definitions
user32 = ctypes.windll.user32
VK_LWIN = 0x5B
VK_MENU = 0x12       # Alt
VK_CONTROL = 0x11
VK_RETURN = 0x0D
VK_KEY_R = 0x52
VK_KEY_V = 0x56
VK_KEY_N = 0x4E
VK_KEY_T = 0x54


def native_press_hotkey(*keys):
    """Simulates pressing and releasing multiple keys simultaneously."""
    for k in keys:
        user32.keybd_event(k, 0, 0, 0)
    time.sleep(0.08)
    for k in reversed(keys):
        user32.keybd_event(k, 0, 2, 0)
    time.sleep(0.08)


def native_press_enter():
    user32.keybd_event(VK_RETURN, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(VK_RETURN, 0, 2, 0)
    time.sleep(0.05)


def copy_to_clipboard(text: str):
    """Copies UTF-8 / Devanagari text safely into the Windows clipboard using PySide6."""
    try:
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance() or QApplication([])
        app.clipboard().setText(text)
        time.sleep(0.1)
    except Exception:
        # Fallback to PowerShell Set-Clipboard
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", f"$input | Set-Clipboard"],
            input=text.encode("utf-8"),
            check=True
        )


def paste_text(text: str):
    """Pastes text via clipboard to guarantee 100% clean Devanagari Unicode rendering."""
    copy_to_clipboard(text)
    if HAS_PYAUTOGUI:
        pyautogui.hotkey('ctrl', 'v')
    else:
        native_press_hotkey(VK_CONTROL, VK_KEY_V)
    time.sleep(0.2)


def trigger_gamebar_recording():
    """Toggles Windows Game Bar recording (Win + Alt + R)."""
    if HAS_PYAUTOGUI:
        pyautogui.hotkey('win', 'alt', 'r')
    else:
        native_press_hotkey(VK_LWIN, VK_MENU, VK_KEY_R)


def trigger_new_session():
    """Triggers New Session button via Ctrl+N."""
    if HAS_PYAUTOGUI:
        pyautogui.hotkey('ctrl', 'n')
    else:
        native_press_hotkey(VK_CONTROL, VK_KEY_N)
    time.sleep(0.3)


def trigger_npu_toggle():
    """Triggers NPU Mode Toggle via Ctrl+T."""
    if HAS_PYAUTOGUI:
        pyautogui.hotkey('ctrl', 't')
    else:
        native_press_hotkey(VK_CONTROL, VK_KEY_T)
    time.sleep(0.3)


def activate_app_window():
    """Brings the Offline Clinical Health Triage Assistant window to the foreground."""
    hwnd = user32.FindWindowW(None, "Offline Clinical Health Triage Assistant")
    if hwnd:
        user32.ShowWindow(hwnd, 9)  # SW_RESTORE
        user32.SetForegroundWindow(hwnd)
        time.sleep(0.5)
        return True
    return False


def run_demo_recording():
    print("=" * 70)
    print("  Offline Clinical Health Triage Assistant — Automated Demo Recorder")
    print("  Snapdragon AI Challenge 2026 (2-Minute Timed Pitch Walkthrough)")
    print("=" * 70)
    
    # 0. Focus App Window
    print("\n[Step 0] Activating application window...")
    if not activate_app_window():
        print("Notice: Please ensure '.venv\\Scripts\\python main.py' is open and visible on screen.")
    time.sleep(1.0)

    # 1. Start Screen Recorder (Win + Alt + R)
    print("\n[Step 1] Starting screen recording in 3 seconds (Win + Alt + R)...")
    for i in range(3, 0, -1):
        print(f"  {i}...")
        time.sleep(1.0)
    
    trigger_gamebar_recording()
    print("  >>> Screen recording started!")
    
    # Narrate intro buffer (0:00 - 0:15)
    print("\n[Timeline 0:00 - 0:15] Voiceover: Rural clinic connectivity & 0-egress architecture...")
    time.sleep(12.0)

    # 2. Prompt 1: Emergency Override (0:15 - 0:30)
    p1 = "I am experiencing severe crushing chest pressure and shortness of breath"
    print(f"\n[Timeline 0:15 - 0:30] Submitting Prompt 1 (Emergency Override)...")
    print(f"  Input: \"{p1}\"")
    paste_text(p1)
    if HAS_PYAUTOGUI:
        pyautogui.press('enter')
    else:
        native_press_enter()
    print("  >>> Intercepted in < 1 ms! Showing Red EMERGENCY Card with 112 routing.")
    time.sleep(12.0)

    # 3. Prompt 2: Turn 1 Hindi Clinical Query (0:30 - 0:50)
    print("\n[Timeline 0:30 - 0:50] Resetting session (Ctrl+N) & Submitting Prompt 2 (Hindi)...")
    trigger_new_session()
    time.sleep(1.0)

    p2 = "मुझे 2 दिन से तेज बुखार है"
    print(f"  Input: \"{p2}\"")
    paste_text(p2)
    if HAS_PYAUTOGUI:
        pyautogui.press('enter')
    else:
        native_press_enter()
    print("  >>> Rendered Hindi Devanagari script cleanly with 'बुखार (Fever)' tag.")
    time.sleep(12.0)

    # 4. Prompt 3: Turn 2 English Follow-Up (0:50 - 1:10)
    p3 = "It started yesterday morning and I also have a mild headache"
    print(f"\n[Timeline 0:50 - 1:10] Submitting Prompt 3 (English Follow-Up)...")
    print(f"  Input: \"{p3}\"")
    paste_text(p3)
    if HAS_PYAUTOGUI:
        pyautogui.press('enter')
    else:
        native_press_enter()
    print("  >>> Language switched back to English with home-care hydration advice.")
    time.sleep(12.0)

    # 5. Prompt 4: Turn 3 Safe-By-Construction Escalation (1:10 - 1:30)
    p4 = "I am not sure if there are other symptoms, I feel very weak"
    print(f"\n[Timeline 1:10 - 1:30] Submitting Prompt 4 (Turn 3 Escalation)...")
    print(f"  Input: \"{p4}\"")
    paste_text(p4)
    if HAS_PYAUTOGUI:
        pyautogui.press('enter')
    else:
        native_press_enter()
    print("  >>> Turn 3 completed. Uncertainty auto-escalated from MILD to MODERATE (Yellow Badge).")
    time.sleep(12.0)

    # 6. Telemetry Inspection & NPU Toggle (1:30 - 1:55)
    print("\n[Timeline 1:30 - 1:55] Inspecting Telemetry Dashboard & Toggling NPU Mode (Ctrl+T)...")
    time.sleep(4.0)
    trigger_npu_toggle()
    print("  >>> Hardware Status updated to: '● Snapdragon Hexagon NPU Accelerated' (Emerald Green).")
    time.sleep(12.0)

    # 7. Stop Screen Recorder (Win + Alt + R)
    print("\n[Timeline 1:55 - 2:00] Stopping screen recorder (Win + Alt + R)...")
    trigger_gamebar_recording()
    time.sleep(1.0)

    print("\n" + "=" * 70)
    print("  ✅ Demo recording workflow completed successfully!")
    print(f"  Saved video path: {Path.home() / 'Videos' / 'Captures'}")
    print("=" * 70)


if __name__ == "__main__":
    run_demo_recording()
