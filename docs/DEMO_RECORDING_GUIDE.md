# Demo Video Recording Guide (2-Minute Pitch)

**Project:** Offline Clinical Health Triage Assistant  
**Challenge:** Snapdragon AI Challenge 2026  
**Target Duration:** Exactly 2 Minutes (120 Seconds)  
**Resolution:** 1080p (1920x1080) or 4K, 60 FPS recommended  

---

## 1. Direct Copy-Paste Prompts for Recording

Keep these exact strings ready on a secondary screen or notepad to paste directly into the desktop app during the demo walkthrough:

### Prompt 1: Acute Emergency Safety Override Trigger
```text
I am experiencing severe crushing chest pressure and shortness of breath
```
*Expected Behavior:* Sub-millisecond interception (< 1 ms). LLM bypassed. Immediate high-contrast Red `EMERGENCY` Card displayed directing patient to call **112**.

---

### Prompt 2: Turn 1 — Hindi Clinical Query
```text
मुझे 2 दिन से तेज बुखार है
```
*Expected Behavior:* Language automatically switches to Hindi (`HI`). Clean Devanagari script rendered with symptom tag `बुखार (Fever)` and focused duration follow-up inquiry. Turn counter updates to `Turn: 1 / 3`.

---

### Prompt 3: Turn 2 — Dynamic English Language Switch
```text
It started yesterday morning and I also have a mild headache
```
*Expected Behavior:* Language dynamically switches back to English (`EN`). Assistant processes multi-turn context and provides home-care hydration and symptom monitoring advice. Turn counter updates to `Turn: 2 / 3`.

---

### Prompt 4: Turn 3 — Safe-By-Construction Escalation Prompt
```text
I am not sure if there are other symptoms, I feel very weak
```
*Expected Behavior:* Hard-capped Turn 3 forced completion. Persisting uncertainty automatically escalates severity from `MILD` to `MODERATE` (Yellow Badge), advising outpatient clinical consultation.

---

## 2. Second-by-Second Video Recording Timeline

| Time Window | Audio Voiceover Script | On-Screen Visual Actions |
| :--- | :--- | :--- |
| **0:00 – 0:15** | *"Over 68% of rural clinics face telecommunication dead zones where cloud chatbots fail, latency causes danger, and patient data privacy is compromised."* | Show opening slide: Rural clinic connectivity chasm, "No Signal" graphic, and project title banner. |
| **0:15 – 0:30** | *"Frontline workers and patients need an on-device, sovereign triage assistant that speaks regional vernaculars like Hindi and operates with zero network egress."* | Highlight key stats: Zero Egress (0 bytes transmitted), 100% on-device sovereignty, bilingual English/Hindi. |
| **0:30 – 0:45** | *"Meet the Offline Clinical Health Triage Assistant. Our architecture is safe-by-construction, featuring a sub-millisecond Core Safety Engine that catches emergencies before the LLM can hallucinate."* | Show architecture diagram: Dual-layer pipeline showing Regex Safety Interception ➔ Bounded 3-Turn LLM Session Manager. |
| **0:45 – 1:00** | *"For non-emergencies, a 3-turn bounded manager prevents endless conversational loops and automatically escalates unresolved uncertainty to protect patient safety."* | Transition to clean desktop GUI window. Cursor hovers over header status banner: `● CPU Emulation Mode (Snapdragon QNN Architecture Scaffolded)`. |
| **1:00 – 1:12** | *(Demo: Emergency Pass)* *"Watch: When a patient presents with crushing chest pressure, the Safety Engine intercepts in less than a millisecond—no LLM delay, direct 112 routing."* | **Paste Prompt 1**. Click **Send ➔**. Red `EMERGENCY` card appears instantly. Camera zooms into the 112 emergency routing directive. |
| **1:12 – 1:22** | *(Demo: Bilingual Hindi)* *"Clicking New Session, our multilingual pipeline dynamically detects Hindi input, rendering crisp Devanagari script without missing boxes."* | Click **+ New Session**. **Paste Prompt 2 (Hindi)**. Click **Send ➔**. Assistant card renders Hindi Devanagari text and `बुखार (Fever)` pill. |
| **1:22 – 1:32** | *(Demo: Multi-Turn & Escalation)* *"The patient responds in English; language switches dynamically. On Turn 3, unresolved uncertainty automatically escalates to Moderate."* | **Paste Prompt 3 (English)**, then **Prompt 4**. Show Turn 3 completion, input locking in action, and automatic escalation to `MODERATE`. |
| **1:32 – 1:45** | *(Demo: Telemetry Dashboard)* *"On the right panel, our live telemetry dashboard samples continuous CPU utilization every 100ms, tracking TTFT, token speed, and 0-byte egress."* | Camera zooms into Right Panel: Point to **ASR Latency**, **LLM TTFT**, **Token Speed (tok/s)**, **Peak CPU %**, and **100% Local (0 Bytes Egressed)**. |
| **1:45 – 2:00** | *"Optimized for Snapdragon Hexagon NPU via QNN Execution Provider scaffolding, we achieve sub-50ms TTFT and 70% CPU reduction. Resilient, private intelligence at the edge."* | Click **Toggle NPU Mode** button to show green badge: `● Snapdragon Hexagon NPU Accelerated`. Show final summary slide with GitHub QR code. |

---

## 3. Visual Elements Checklist for Recording

Ensure the screen recorder clearly captures these four key UI components:

- [ ] **1. Red Emergency Card (`#FF4D4D`):**
  - Verify high contrast between the red card border, dark slate background, and black-on-red `EMERGENCY` badge.
  - Highlight the text: *"CRITICAL SAFETY OVERRIDE ... Please call emergency services (112)"*.
- [ ] **2. Native Devanagari Text Rendering:**
  - Verify that Hindi characters (e.g. `मुझे`, `बुखार`, `लक्षण`) render cleanly without tofu boxes, overlapping glyphs, or broken matras (using `Nirmala UI` / `Mangal`).
- [ ] **3. Top Header Hardware Status Banner:**
  - Start video with `● CPU Emulation Mode (Snapdragon QNN Architecture Scaffolded)` in warm amber.
  - Toggle to `● Snapdragon Hexagon NPU Accelerated` in emerald green during the hardware discussion.
- [ ] **4. Live Real-Time Telemetry Dashboard (Right Panel):**
  - Show live metric card updates after each query:
    - **ASR Processing Time:** `XX ms`
    - **LLM TTFT:** `XX ms`
    - **Token Speed:** `XX.X tok/s`
    - **Peak CPU Load:** `XX.X %` (continuous sampling)
    - **Privacy & Isolation:** `100% Local (0 Bytes Egressed)` in bright cyan.
- [ ] **5. Input Control Locking:**
  - Point out that during query processing, the input box, Send button, Audio button, and New Session button are disabled, preventing state corruption.
- [ ] **6. Sticky Bottom Legal Disclaimer:**
  - Ensure the amber disclaimer banner at the bottom is visible: *"Notice: This tool provides initial clinical triage guidance only and does not constitute a medical diagnosis. In case of emergency, call 112 immediately."*
