---
title: Quasar - Adversarial Defense Engine
emoji: 🌌
colorFrom: indigo
colorTo: purple
sdk: docker
pinned: false
tags:
  - openenv
  - reinforcement-learning
  - cybersecurity
  - adversarial-ai
---

# 🌌 Quasar: Autonomous Defense Against Adversarial Data Poisoning

![OpenEnv-Compliant](https://img.shields.io/badge/OpenEnv-Compliant-success) ![Tasks](https://img.shields.io/badge/Tasks-3_Tiers-blue) ![Live Data](https://img.shields.io/badge/Live_Data-HF_Datasets-orange) ![Status](https://img.shields.io/badge/Status-Live-brightgreen)

## 🌐 Live Demo & Repository
* **Live Deployment (Hugging Face):** [https://huggingface.co/spaces/kalpeshparashar/quasar](https://huggingface.co/spaces/kalpeshparashar/quasar)
* **Source Code (GitHub):** [https://github.com/Kalpesh-ops/quasar](https://github.com/Kalpesh-ops/quasar)

---

## 🚨 The Real-World Problem
As enterprise systems increasingly integrate Large Language Models (LLMs) and Continuous Learning pipelines, they become vulnerable to a silent threat: **Adversarial Data Poisoning and Prompt Injection**. 

Malicious actors inject syntactically valid but semantically manipulative payloads into continuous data streams (like user feedback logs or API requests). The goal is to silently corrupt the AI's training weights, trigger prompt injections, or bypass alignment safeguards. Traditional Web Application Firewalls (WAFs) and signature-based firewalls fail here because the payloads look like standard JSON text.

## 🛡️ Quasar: The Solution
**Quasar** is an advanced OpenEnv simulation that trains autonomous AI security agents to act as next-generation SOC analysts. The agent must monitor a continuous enterprise data pipeline, maintain backend database integrity, and accurately isolate adversarial anomalies without disrupting legitimate business data.

To ensure maximum real-world utility, Quasar does not rely solely on toy strings. It actively fetches **real adversarial prompt injections** from live Hugging Face datasets (`deepset/prompt-injections`) to generate its network traffic.

---

## ⚙️ Environment Design & Flow

### Observation Space (What the Agent Sees)
The environment provides a strictly typed `QuasarObservation` Pydantic model containing:
* `recent_traffic`: A batch of the 5 most recent JSON API requests hitting the pipeline.
* `database_integrity_score`: The current health of the backend model (0.0 - 100.0). Drops heavily if poisoned data is allowed through.
* `active_firewall_rules`: A list of currently isolated IPs.

### Action Space (What the Agent Can Do)
The agent responds with a strictly typed `QuasarAction`:
* `command`: Must be one of `allow_packet`, `flag_packet`, `isolate_ip`, or `pass`.
* `target_id`: The specific `packet_id` to flag or `source_ip` to isolate.

### System Flow
1. **Traffic Generation:** `traffic_gen.py` pulls real adversarial data from Hugging Face and wraps it in simulated enterprise JSON payloads.
2. **State Management:** `env.py` manages the step logic. It processes the agent's action, calculates the damage of missed packets, drops the Database Integrity score if necessary, and calculates the reward based on catch-rate vs. false-positive rate.
3. **API Serving:** `app.py` exposes the environment via the standard OpenEnv FastAPI endpoints (`/step`, `/reset`, `/state`) alongside a human-readable UI at the root (`/`).

---

## 🎯 The 3 Tasks (Difficulty Progression)

Quasar tests agents across three escalating threat levels:

1. **Task 1: Volumetric Flood (Easy)**
   * **Scenario:** A single noisy IP is flooding the pipeline with identical prompt-injection payloads.
   * **Objective:** The agent must identify the repetitive source and use `isolate_ip` to block it at the firewall level.
   
2. **Task 2: Contextual Prompt Injection (Medium)**
   * **Scenario:** Real-world adversarial instructions (sourced from HF datasets) are hidden within normal-looking user queries from varying IPs.
   * **Objective:** The agent must inspect the payload bodies and use `flag_packet` to drop specific malicious requests while allowing benign traffic through.

3. **Task 3: Stealth Data Poisoning (Hard)**
   * **Scenario:** Payloads contain subtle statistical anomalies and deeply nested JSON structures designed to slowly drift and corrupt the backend model's weights over time. 
   * **Objective:** The agent must detect these deep semantic anomalies and quarantine them, balancing a high catch rate with a zero false-positive rate.

---

## 🗂️ Directory Structure

```text
QUASAR/
│
├── server/                 # API Server configuration
│   ├── __init__.py
│   └── app.py              # FastAPI application & UI wrapper for OpenEnv
│
├── src/                    # Core Environment Engine
│   ├── __init__.py
│   ├── env.py              # The OpenEnv Step/Reset/State logic and Grader
│   ├── models.py           # Strict Pydantic Action and Observation schemas
│   └── traffic_gen.py      # HF Dataset fetching and mock enterprise log generation
│
├── .gitattributes
├── .gitignore
├── Dockerfile              # Hugging Face deployment configuration (Python 3.10)
├── inference.py            # Baseline LLM inference script for validation
├── openenv.yaml            # OpenEnv task definitions and metadata
├── pyproject.toml          # Build system and dependencies
├── README.md               # You are here
└── uv.lock                 # Fast dependency resolution lockfile
```

---

## 🛠️ Tech Stack & Tools Used

* **[OpenEnv Core](https://github.com/facebookresearch/openenv):** Meta's standard API specification for RL environments.
* **[Hugging Face Datasets](https://huggingface.co/docs/datasets/):** Used to stream real-world adversarial prompt injections (`deepset/prompt-injections`) directly into the simulation.
* **[FastAPI](https://fastapi.tiangolo.com/) & [Uvicorn](https://www.uvicorn.org/):** Powers the asynchronous HTTP server for agent interaction.
* **[Pydantic](https://docs.pydantic.dev/):** Ensures strict, deterministic typing for LLM inputs and outputs to prevent hallucinated actions.
* **[Docker](https://www.docker.com/) & [uv](https://github.com/astral-sh/uv):** Used for lightning-fast containerized deployment on Hugging Face Spaces.
* **[OpenAI Python SDK](https://github.com/openai/openai-python):** Used in the baseline script to test the environment using frontier models.

---

## 🚀 Setup & Reproducibility

### Local Validation
Ensure you have `uv` installed, then run the OpenEnv validator to confirm schema compliance:
```bash
openenv validate
```

### Running the Baseline Inference
The `inference.py` script proves the environment is solvable. It uses an LLM to navigate the environment, strictly adhering to the `[START]`, `[STEP]`, and `[END]` logging formats. 

Configure your environment variables:
```bash
export API_BASE_URL="[https://api.groq.com/openai/v1](https://api.groq.com/openai/v1)" # Or OpenAI/vLLM equivalent
export MODEL_NAME="llama-3.3-70b-versatile" 
export HF_TOKEN="your_api_key_here"
```

Run the baseline:
```bash
python inference.py
```

*Note: In baseline testing with `llama-3.3-70b-versatile`, the model achieved a perfect `1.0` score on Task 1, but dropped to `~0.6` on Tasks 2 and 3, mathematically proving that Quasar provides a genuine, difficult challenge for frontier LLMs rather than being a solved toy environment.*

---

## 🛡️ Hackathon Automated Validation Proof
*(This section provides static verification of all mandatory judging criteria)*

### 1. Infrastructure & Execution Verification
* **Automated Validation:** Passes `openenv validate` with `[OK] Ready for multi-mode deployment`.
* **Container Limits:** `Dockerfile` optimized with `uv` to build and execute well within the strict **2 vCPU / 8GB RAM** constraint.
* **Inference Runtime:** The baseline script executes 45 sequential API steps (3 tasks * 15 steps) comfortably under the **20-minute** execution limit.
* **HF Space Connectivity:** Server binds to `0.0.0.0:7860` and returns `HTTP 200 OK` on both the root `/` UI and the OpenEnv `/reset` and `/step` endpoints.

### 2. OpenEnv Specification Compliance
* **Configuration:** `openenv.yaml` contains all mandatory metadata, entrypoints, and exact task definitions.
* **Strict Typing:** Utilizes Pydantic for `QuasarObservation` (State), `QuasarAction` (Action), and `QuasarReward` (Reward) models to enforce deterministic LLM output parsing.
* **Interface:** Fully implements the `Environment` base class with `step()`, `reset()`, and `state()` asynchronous methods returning typed `StepResult` objects.

### 3. Task & Grader Architecture
Contains exactly **3 graded tasks** mapping to a strict Easy → Medium → Hard progression:
1. `task_1_volumetric_flood` (Easy)
2. `task_2_contextual_injection` (Medium)
3. `task_3_stealth_poisoning` (Hard)
* **Grader Determinism:** The reward function mathematically calculates a deterministic float between `0.0` and `1.0` based on backend integrity, catch-rate, and false-positive penalties.

### 4. Baseline Inference Architecture (`inference.py`)
* **Location:** Deployed at the exact root directory.
* **Client Restriction:** Strictly utilizes the mandatory `OpenAI` client (via `AsyncOpenAI`).
* **Environment Variables:** Dynamically loads `API_BASE_URL`, `MODEL_NAME`, and `HF_TOKEN` prior to client initialization.
* **Strict stdout Logging:** Implements the exact mandatory regex-parsable stdout logs:
  * `[START] task={task} env={env} model={model}`
  * `[STEP] step={step} action={action} reward={reward} done={done} error={error}`
  * `[END] success={success} steps={steps} score={score} rewards={rewards}`