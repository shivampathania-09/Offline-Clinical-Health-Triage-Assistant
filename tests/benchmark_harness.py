import os
import time
import json
import psutil
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Any, Optional, Callable, Tuple
from dotenv import load_dotenv

import sys

# Configure UTF-8 output encoding for Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Always verify active models on console.groq.com/docs/models
GROQ_MODEL = "llama-3.1-8b-instant"


class BenchmarkHarness:
    def __init__(
        self,
        sample_file: str = "tests/sample_symptoms.json",
        npu_inference_fn: Optional[Callable[[str], float]] = None,
    ):
        """
        npu_inference_fn: A callable taking a prompt string and returning latency in ms.
        Should be wired to the actual NPUInferenceSession. If None, the harness
        labels outputs as SIMULATED to avoid false hardware claims.
        """
        self.sample_file = sample_file
        self.num_runs = 5
        self.results: List[Dict[str, Any]] = []
        self.npu_inference_fn = npu_inference_fn
        self.npu_mode = "REAL" if npu_inference_fn else "SIMULATED"

        if self.npu_mode == "SIMULATED":
            print(
                "[WARNING] No real NPU inference function provided. "
                "Results will be labeled SIMULATED. "
                "Do not present these as hardware-measured numbers."
            )

    def load_samples(self) -> List[str]:
        if os.path.exists(self.sample_file):
            with open(self.sample_file, "r") as f:
                return json.load(f)
        return [f"Sample patient symptom description {i}." for i in range(1, 31)]

    def _run_npu_inference(self, text: str) -> float:
        if self.npu_inference_fn:
            return self.npu_inference_fn(text)
        
        # Fallback simulation only - clearly flagged in outputs
        start = time.perf_counter()
        time.sleep(0.12 + (len(text) % 5) * 0.02)
        return (time.perf_counter() - start) * 1000

    def _query_live_groq_api(self, text: str) -> Tuple[float, bool]:
        """
        Queries live Groq API endpoint.
        Returns (latency_ms, was_live). was_live=False indicates fallback execution.
        """
        if not GROQ_API_KEY:
            sim_ms = (0.85 + (len(text) % 7) * 0.1) * 1000
            return sim_ms, False

        try:
            import requests
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": GROQ_MODEL,
                "messages": [{"role": "user", "content": text}],
                "max_tokens": 150,
            }
            start = time.perf_counter()
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=10,
            )
            response.raise_for_status()
            latency_ms = (time.perf_counter() - start) * 1000
            time.sleep(0.25)  # Pause to avoid rate limits across repeated runs
            return latency_ms, True
        except Exception as e:
            print(f"  Groq API call failed ({e}); using fallback latency for this sample.")
            return 1100.0, False

    def run_benchmark(self):
        samples = self.load_samples()
        os.makedirs("artifacts", exist_ok=True)
        print(
            f"Benchmarking {len(samples)} prompts × {self.num_runs} runs "
            f"(NPU mode: {self.npu_mode})..."
        )

        for idx, prompt in enumerate(samples, 1):
            npu_times, cloud_times, cloud_live_flags = [], [], []
            cpu_npu, cpu_cloud = [], []

            for _ in range(self.num_runs):
                npu_ms = self._run_npu_inference(prompt)
                cpu_npu.append(psutil.cpu_percent(interval=0.05))

                cloud_ms, was_live = self._query_live_groq_api(prompt)
                cloud_times.append(cloud_ms)
                cloud_live_flags.append(was_live)
                cpu_cloud.append(psutil.cpu_percent(interval=0.05))

                npu_times.append(npu_ms)

            self.results.append({
                "prompt_id": idx,
                "npu_mode": self.npu_mode,
                "npu_latency_mean_ms": np.mean(npu_times),
                "npu_latency_std_ms": np.std(npu_times),
                "cloud_latency_mean_ms": np.mean(cloud_times),
                "cloud_latency_std_ms": np.std(cloud_times),
                "cloud_all_live": all(cloud_live_flags),
                "npu_cpu_load_percent": np.mean(cpu_npu),
                "cloud_cpu_load_percent": np.mean(cpu_cloud),
            })

        df = pd.DataFrame(self.results)
        df.to_csv("artifacts/benchmark_results.csv", index=False)
        self.generate_plots(df)
        print(
            f"Done. NPU mode: {self.npu_mode}. "
            f"Live cloud calls succeeded for {df['cloud_all_live'].sum()}/{len(df)} prompts."
        )

    def generate_plots(self, df: pd.DataFrame):
        x = np.arange(len(df))

        # Plot 1: Latency Comparison with Error Bars
        plt.figure(figsize=(10, 5))
        plt.bar(
            x - 0.2,
            df["npu_latency_mean_ms"],
            0.4,
            yerr=df["npu_latency_std_ms"],
            label=f"Snapdragon NPU ({df['npu_mode'].iloc[0]})",
            color="#32CD32",
            capsize=3,
        )
        plt.bar(
            x + 0.2,
            df["cloud_latency_mean_ms"],
            0.4,
            yerr=df["cloud_latency_std_ms"],
            label="Cloud API Baseline",
            color="#FF4500",
            capsize=3,
        )
        plt.xlabel("Prompt Index")
        plt.ylabel("Latency (ms)")
        plt.title("On-Device NPU vs Cloud API Latency (Mean ± SD, 5 runs)")
        plt.legend()
        plt.tight_layout()
        plt.savefig("artifacts/latency_comparison.png")
        plt.close()

        # Plot 2: CPU Offload Comparison
        plt.figure(figsize=(10, 5))
        plt.bar(x - 0.2, df["npu_cpu_load_percent"], 0.4, label="NPU Pipeline", color="#32CD32")
        plt.bar(x + 0.2, df["cloud_cpu_load_percent"], 0.4, label="Cloud Pipeline", color="#FF4500")
        plt.xlabel("Prompt Index")
        plt.ylabel("CPU Load (%)")
        plt.title("CPU Utilization: NPU Offload vs Cloud Round-Trip")
        plt.legend()
        plt.tight_layout()
        plt.savefig("artifacts/cpu_utilization.png")
        plt.close()


if __name__ == "__main__":
    # Wire the real NPUInferenceSession here when executing on hardware:
    # from src.models.npu_engine import NPUInferenceSession
    # session = NPUInferenceSession(...)
    # harness = BenchmarkHarness(npu_inference_fn=session.timed_inference)

    harness = BenchmarkHarness()  # Fallback to SIMULATED mode until wired
    harness.run_benchmark()
