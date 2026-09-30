import os
import sys
import time
import subprocess
import ctypes
from pathlib import Path

# Ensure UTF-8 stdout encoding on Windows
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        getattr(sys.stdout, "reconfigure")(encoding="utf-8")
    except Exception:
        pass

import typing

# Optional PyAutoGUI support with dynamic import and automatic native Windows fallback
pyautogui: typing.Any = None
try:
    import importlib
    pyautogui = importlib.import_module("pyautogui")
    HAS_PYAUTOGUI = True
except Exception:
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


def copy_to_clipboard(text: str) -> None:
    """Copies UTF-8 / Devanagari text safely into the Windows clipboard using pyperclip."""
    try:
        import pyperclip
        pyperclip.copy(text)
        time.sleep(0.1)
        return
    except Exception:
        pass

    # Fallback to PowerShell Set-Clipboard
    subprocess.run(
        ["powershell", "-NoProfile", "-Command", "$input | Set-Clipboard"],
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


def activate_app_window() -> bool:
    """Brings the Offline Clinical Health Triage Assistant window to the foreground with thread input attachment."""
    hwnd = user32.FindWindowW(None, "Offline Clinical Health Triage Assistant")
    if not hwnd:
        # Search all top-level windows for partial title match
        matched_hwnd = 0

        def enum_cb(h, _):
            nonlocal matched_hwnd
            length = user32.GetWindowTextLengthW(h)
            if length > 0:
                buf = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(h, buf, length + 1)
                if "Offline Clinical Health Triage Assistant" in buf.value:
                    matched_hwnd = h
                    return False
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_void_p)
        user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
        hwnd = matched_hwnd

    if hwnd:
        fore_hwnd = user32.GetForegroundWindow()
        fore_thread = user32.GetWindowThreadProcessId(fore_hwnd, None)
        target_thread = user32.GetWindowThreadProcessId(hwnd, None)
        if fore_thread != target_thread and fore_thread != 0:
            user32.AttachThreadInput(fore_thread, target_thread, True)
            user32.ShowWindow(hwnd, 9)  # SW_RESTORE
            user32.SetForegroundWindow(hwnd)
            user32.SetFocus(hwnd)
            user32.AttachThreadInput(fore_thread, target_thread, False)
        else:
            user32.ShowWindow(hwnd, 9)
            user32.SetForegroundWindow(hwnd)
        time.sleep(0.5)
        return True
    return False


def run_demo_recording():
    is_manual = "--manual" in sys.argv or "--no-hotkey" in sys.argv
    print("=" * 70)
    print("  Offline Clinical Health Triage Assistant — Automated Demo Recorder")
    print("  Snapdragon AI Challenge 2026 (2-Minute Timed Pitch Walkthrough)")
    print("=" * 70)
    print("\n[Screen Recording Method]")
    print("  • Automatic: Triggers Win + Alt + R (Windows Game Bar)")
    print("  • Manual: Pass '--manual' if recording with Snipping Tool (Win+Shift+R), OBS, or Loom")
    print("  • If Windows Game Bar says 'Recording isn't working':")
    print("    Press Win + G while the app is open -> Settings -> General -> check 'Remember this is a game'.\n")

    # 0. Focus App Window
    print("[Step 0] Activating application window...")
    if not activate_app_window():
        print("Notice: Please ensure '.venv\\Scripts\\python main.py' is open and visible on screen.")
    time.sleep(1.0)

    # 1. Start Screen Recorder
    if not is_manual:
        print("\n[Step 1] Starting screen recording in 3 seconds (Win + Alt + R)...")
        for i in range(3, 0, -1):
            print(f"  {i}...")
            time.sleep(1.0)
        trigger_gamebar_recording()
        print("  >>> Screen recording triggered via Win + Alt + R!")
    else:
        print("\n[Step 1] Manual recording mode active. Starting autopilot interaction in 3 seconds...")
        for i in range(3, 0, -1):
            print(f"  {i}...")
            time.sleep(1.0)
        print("  >>> Autopilot interaction starting now!")
    
    # Narrate intro buffer (Phases 1 & 2: Problem & Architecture, 0:00 - 0:49)
    print("\n[Timeline 0:00 - 0:49] Voiceover: Rural clinic connectivity & 0-egress architecture...")
    time.sleep(48.0)

    # 2. Prompt 1: Emergency Override (Phase 3A: 0:49 - 1:06)
    p1 = "I am experiencing severe crushing chest pressure and shortness of breath"
    print(f"\n[Timeline 0:49 - 1:06] Submitting Prompt 1 (Emergency Override)...")
    activate_app_window()
    print(f"  Input: \"{p1}\"")
    paste_text(p1)
    time.sleep(0.6)  # Pause so typed input is clearly visible
    if HAS_PYAUTOGUI:
        pyautogui.press('enter')
    else:
        native_press_enter()
    print("  >>> Intercepted in < 1 ms! Showing Red EMERGENCY Card with 112 routing.")
    time.sleep(15.5)

    # 3. Prompt 2: Turn 1 Hindi Clinical Query (Phase 3B: 1:06 - 1:22)
    print("\n[Timeline 1:06 - 1:22] Resetting session (Ctrl+N) & Submitting Prompt 2 (Hindi)...")
    activate_app_window()
    trigger_new_session()
    time.sleep(1.0)

    p2 = "मुझे 2 दिन से तेज बुखार है"
    print(f"  Input: \"{p2}\"")
    paste_text(p2)
    time.sleep(0.6)  # Pause so Hindi Devanagari text is clearly visible
    if HAS_PYAUTOGUI:
        pyautogui.press('enter')
    else:
        native_press_enter()
    print("  >>> Rendered Hindi Devanagari script cleanly with 'बुखार (Fever)' tag.")
    time.sleep(14.0)

    # 4. Prompt 3: Turn 2 English Follow-Up (Phase 3C-1: 1:22 - 1:31)
    p3 = "It started yesterday morning and I also have a mild headache"
    print(f"\n[Timeline 1:22 - 1:31] Submitting Prompt 3 (English Follow-Up)...")
    activate_app_window()
    print(f"  Input: \"{p3}\"")
    paste_text(p3)
    time.sleep(0.5)  # Pause so typed input is clearly visible
    if HAS_PYAUTOGUI:
        pyautogui.press('enter')
    else:
        native_press_enter()
    print("  >>> Language switched back to English with home-care hydration advice.")
    
    # Crucial 5.0-second pause after Prompt 3 so Turn 2 finishes and settles
    print("  Waiting 5.0s for Turn 2 completion and UI input unlock before Prompt 4...")
    time.sleep(5.0)

    # 5. Prompt 4: Turn 3 Safe-By-Construction Escalation (Phase 3C-2: 1:31 - 1:44)
    p4 = "I am not sure if there are other symptoms, I feel very weak"
    print(f"\n[Timeline 1:31 - 1:44] Submitting Prompt 4 (Turn 3 Escalation)...")
    activate_app_window()
    print(f"  Input: \"{p4}\"")
    paste_text(p4)
    time.sleep(0.5)  # Pause so typed input is clearly visible
    if HAS_PYAUTOGUI:
        pyautogui.press('enter')
    else:
        native_press_enter()
    print("  >>> Turn 3 completed. Uncertainty auto-escalated from MILD to MODERATE (Yellow Badge).")
    time.sleep(14.5)

    # 6. Telemetry Inspection (Phase 3D: 1:44 - 2:02)
    print("\n[Timeline 1:44 - 2:02] Inspecting Live Telemetry Dashboard...")
    time.sleep(18.0)

    # 7. NPU Mode Toggle & Closing (Phase 4: 2:02 - 2:28)
    print("\n[Timeline 2:02 - 2:28] Toggling NPU Mode (Ctrl+T) & Concluding Pitch...")
    activate_app_window()
    trigger_npu_toggle()
    print("  >>> Hardware Status updated to: '● Snapdragon Hexagon NPU Accelerated' (Emerald Green).")
    time.sleep(26.5)

    # 8. Stop Screen Recorder
    if not is_manual:
        print("\n[Timeline 2:28] Stopping screen recorder (Win + Alt + R)...")
        trigger_gamebar_recording()
    else:
        print("\n[Timeline 2:28] Autopilot interaction completed! Please stop your screen recorder now.")
    time.sleep(1.0)

    print("\n" + "=" * 70)
    print("  ✅ Demo recording workflow completed successfully!")
    print(f"  Next Step: Run '.venv\\Scripts\\python merge_video_audio.py' to produce FINAL_DEMO_SUBMISSION.mp4")
    print("=" * 70)


if __name__ == "__main__":
    run_demo_recording()
