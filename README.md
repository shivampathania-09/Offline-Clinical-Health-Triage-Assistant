# Offline Clinical Health Triage Assistant (100% On-Device, Zero Egress Privacy)

[![Snapdragon AI Challenge](https://img.shields.io/badge/Snapdragon%20AI%20Challenge-Submission%20Ready-red.svg)](https://www.qualcomm.com/developer)
[![Privacy 100% Local](https://img.shields.io/badge/Privacy-100%25%20Local%20(0%20Bytes%20Egressed)-brightgreen.svg)]()
[![Hardware Architecture](https://img.shields.io/badge/Hardware-Snapdragon%20Hexagon%20NPU%20(QNN%20Scaffolded)-blue.svg)]()
[![Tests Passing](https://img.shields.io/badge/tests-34%2F34%20passing-success.svg)]()
[![Bilingual](https://img.shields.io/badge/Languages-English%20%7C%20%E0%A4%B9%E0%A4%BF%E0%A4%82%E0%A4%A6%E0%A4%8 need-orange.svg)]()

> **Medical Disclaimer:** This tool provides preliminary clinical triage guidance only and does not constitute a medical diagnosis. In case of emergency, call **112** immediately.

---

## Executive Summary

The **Offline Clinical Health Triage Assistant** is a sovereign, zero-network desktop application built for frontline health workers, rural primary health centers (PHCs), and disconnected communities. Designed to bridge the critical gap in regions with intermittent or absent internet connectivity, the assistant performs 100% on-device clinical symptom triage, dynamic English ↔ Hindi bilingual dialogue, and sub-millisecond emergency intervention.

### Core Pillars
1. **100% On-Device Privacy & Zero Egress:** Zero bytes are transmitted across any network. Patient medical history, symptoms, and voice recordings remain strictly within local RAM.
2. **Dual-Layer Safety Architecture:** Deterministic regex pattern matching with 5-token lookback/lookahead negation analysis catches life-threatening emergencies before LLM execution, complemented by a Pydantic-validated bounded dialogue engine.
3. **Snapdragon NPU Acceleration Scaffolding:** Software architecture designed and optimized for Snapdragon Hexagon NPU via QNN Execution Provider scaffolding, with verified CPU fallback execution for cross-platform evaluation.
4. **Bilingual Accessibility:** Real-time dynamic language detection for English, Hindi (Devanagari Unicode), and Hinglish transliterations, rendered via a native Devanagari font stack (`Nirmala UI`, `Mangal`, `Noto Sans Devanagari`).

---

## Snapdragon Acceleration & Hardware Architecture

### Hardware Transparency & Execution Status Audit
* **Target Hardware:** Qualcomm Snapdragon X Elite / Copilot+ PC (Hexagon NPU, 45+ TOPS).
* **Execution Status Disclosure:** 
  > *"Software architecture designed and optimized for Snapdragon Hexagon NPU via QNN Execution Provider scaffolding, with verified CPU fallback execution for cross-platform evaluation."*
* **Dynamic Hardware Detection (`src/models/npu_engine.py`):**
  - **On Native Snapdragon NPU Hardware:** The engine detects Qualcomm drivers via ONNX Runtime `QNNExecutionProvider`, configuring Hexagon Tensor Processor (HTP) performance bursts and context cache binaries. The GUI displays the green badge: `● Snapdragon Hexagon NPU Accelerated`.
  - **On x86_64 / Non-Qualcomm Development Machines:** The runtime transparently declares `CPUExecutionProvider` fallback, setting the GUI header to:
    `● CPU Emulation Mode (Snapdragon QNN Architecture Scaffolded)`.
  - **Benchmark Harness Reporting:** The benchmark suite explicitly labels execution as `[SIMULATED NPU]` when run without physical Hexagon hardware to prevent false performance claims.

```
                           [ Clinical Input Stream ]
                                      │
                                      ▼
                      ┌───────────────────────────────┐
                      │    NPU Runtime Session Audit  │
                      │  (src/models/npu_engine.py)   │
                      └───────────────────────────────┘
                                      │
                 ┌────────────────────┴────────────────────┐
                 ▼                                         ▼
   [Snapdragon NPU Hardware Detected]       [x86 / Non-Qualcomm Dev Hardware]
                 │                                         │
                 ▼                                         ▼
   ┌───────────────────────────┐             ┌───────────────────────────┐
   │ QNN Execution Provider    │             │ Verified CPU Fallback     │
   │ (Hexagon HTP Burst Mode)  │             │ (Snapdragon QNN Scaffold) │
   │ Status: 'NPU Accelerated' │             │ Status: 'CPU Emulation'   │
   └───────────────────────────┘             └───────────────────────────┘
```

---

## Dual-Layer Safety Architecture

```
                                [ Patient Input ]
                                        │
                                        ▼
                       ┌────────────────────────────────┐
                       │   Dynamic Language Detector    │
                       │    (Devanagari & Hinglish)     │
                       └────────────────────────────────┘
                                        │
                                        ▼
                       ┌────────────────────────────────┐
                       │    Layer 1: Safety Engine      │
                       │ (Regex & Token Negation Guard) │
                       └────────────────────────────────┘
                                  │           │
                 [Emergency Match]│           │[No Emergency / Negated]
                                  ▼           ▼
                   ┌────────────────────┐   ┌───────────────────────────┐
                   │ Immediate 112      │   │ Layer 2: Triage Session   │
                   │ Safety Override    │   │ (Bounded 3-Turn LLM Loop) │
                   └────────────────────┘   └───────────────────────────┘
                                                          │
                                                          ▼
                                            ┌───────────────────────────┐
                                            │ Robust Triage Parser      │
                                            │ (Pydantic + 1-Shot Retry) │
                                            └───────────────────────────┘
                                                          │
                                                          ▼
                                            ┌───────────────────────────┐
                                            │ Thread-Safe PySide6 GUI   │
                                            │ (Inputs Locked + Signals) │
                                            └───────────────────────────┘
```

### Layer 1: Core Safety Regex & Negation Engine
* **Deterministic Keyword Interception:** Evaluates 10 acute emergency categories (`chest pain`, `slurred speech`, `facial drooping`, `sudden weakness`, `worst headache`, `severe shortness of breath`, `uncontrolled bleeding`, `blue lips`, `stroke`).
* **5-Token Lookback & Lookahead Negation Analysis:** Avoids substring false-negatives (e.g. `"nonspecific chest pain"` is correctly caught as an emergency, while `"no chest pain"` or `"chest pain resolved"` safely passes to dialogue).
* **Zero-Latency Bypass:** Bypasses LLM inference completely when an emergency is detected, delivering an immediate `< 1 ms` override instruction directing the patient to call **112**.

### Layer 2: Multi-Turn Bounded LLM Triage
* **Safe-by-Construction 3-Turn Hard Cap:** Limits interaction to 3 turns to prevent endless loop chatter.
* **Forced Escalation:** If the model remains uncertain (`followup_needed=True` or empty symptoms) at Turn 3, severity is automatically escalated from `MILD` to `MODERATE`, instructing an in-person clinical visit.
* **Capped Self-Healing Parser (`RobustTriageParser`):** Sanitizes markdown code blocks, extracts structured JSON, and enforces schema compliance. Hard-capped at 1 retry before falling back to a deterministic, safe response.

---

## Setup & Verification Instructions

### 1. Environment Setup
```powershell
# Clone repository
git clone https://github.com/your-username/Offline-Clinical-Health-Triage-Assistant.git
cd "Offline-Clinical-Health-Triage-Assistant"

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -e .
pip install pytest psutil pandas numpy matplotlib python-dotenv requests PySide6
```

### 2. Secrets & Configuration (`.env.example`)
Copy `.env.example` to `.env`:
```powershell
copy .env.example .env
```
> [!NOTE]
> The application operates 100% offline. The `GROQ_API_KEY` is strictly optional and used exclusively by `tests/benchmark_harness.py` for cloud baseline comparisons. Never commit `.env` or API keys to version control.

### 3. Regression Test Suite Execution
Run the full 34-test regression suite verifying safety overrides, multi-turn escalation, and UI thread safety:
```powershell
.venv\Scripts\pytest -v

# Run targeted core safety and session escalation tests
.venv\Scripts\pytest tests/test_session.py tests/test_safety.py -v
```

### 4. Latency Benchmark Execution (with CLI Argument Parsing)
Execute the benchmark harness comparing on-device inference against cloud baselines:
```powershell
# Run standard 5-iteration evaluation
.venv\Scripts\python tests/benchmark_harness.py --eval-runs 5

# Custom prompt dataset execution
.venv\Scripts\python tests/benchmark_harness.py --eval-runs 3 --sample-file tests/sample_symptoms.json
```
Benchmark outputs are exported to `artifacts/`:
* `artifacts/benchmark_results.csv`: Tabular latency, standard deviation, and CPU metrics.
* `artifacts/latency_comparison.png`: Graphical latency comparison bar chart.
* `artifacts/cpu_utilization.png`: Side-by-side CPU load offload comparison.

### 5. Launch the Desktop GUI Application
```powershell
# Primary entry point
.venv\Scripts\python -m src.ui.main_window

# Or root launcher
.venv\Scripts\python main.py
```

---

## Known Limitations & Medical Disclaimer

### Known Limitations & Hardware Scoping
1. **Target Architecture Context Binaries:** Compiled QNN context binaries target specific Qualcomm Hexagon HTP core architectures. When executed on non-Snapdragon x86/dev hardware, the application executes in verified CPU Emulation Mode with active telemetry.
2. **Benchmark Reporting:** On non-Qualcomm systems, latency outputs are labeled `[SIMULATED NPU]` to ensure transparent hardware reporting.
3. **Clinical Scope:** Intended solely for pre-diagnostic clinical routing and symptom prioritization. It cannot perform biochemical blood analysis, physical palpation, or diagnostic imaging.

### Medical Disclaimer
> **CRITICAL MEDICAL DISCLAIMER:**  
> This software is intended strictly for preliminary triage assistance and informational guidance. It does not constitute medical advice, diagnosis, or treatment. In case of acute symptoms or a medical emergency, immediately contact national emergency services (**112** in India/EU, **911** in North America) or visit the nearest hospital emergency department.
