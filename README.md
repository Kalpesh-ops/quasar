# Quasar: Autonomous Defense Against Adversarial Data Poisoning

![Quasar AI Defense](https://img.shields.io/badge/OpenEnv-Compliant-success) ![Task Complexity](https://img.shields.io/badge/Tasks-3_Tiers-blue)

## The Real-World Problem (Why Quasar Exists)
As enterprise systems increasingly integrate Large Language Models (LLMs) and Continuous Learning pipelines, they become vulnerable to a silent threat: **Adversarial Data Poisoning**. 

Malicious actors inject syntactically valid but semantically manipulative payloads into continuous data streams (like user feedback logs or API requests). The goal is to silently corrupt the AI's training weights, trigger prompt injections, or bypass alignment safeguards. Traditional WAFs and signature-based firewalls fail here because the payloads look like normal JSON text.

**Quasar** is an OpenEnv simulation that trains autonomous AI security agents to act as next-generation SOC analysts. The agent must monitor a continuous enterprise data pipeline, maintain backend database integrity, and accurately isolate adversarial anomalies without disrupting legitimate business data.

## Environment Design

### Observation Space (What the Agent Sees)
The agent receives a `QuasarObservation` containing:
* `recent_traffic`: A batch of the 5 most recent JSON API requests hitting the pipeline.
* `database_integrity_score`: The current health of the backend model (0.0 - 100.0). Drops heavily if poisoned data is allowed through.
* `active_firewall_rules`: A list of currently isolated IPs.

### Action Space (What the Agent Can Do)
The agent responds with a strictly typed `QuasarAction`:
* `command`: Must be one of `allow_packet`, `flag_packet`, `isolate_ip`, or `pass`.
* `target_id`: The specific `packet_id` to flag or `source_ip` to isolate.

## The 3 Tasks (Difficulty Progression)

1. **Task 1: Volumetric Flood (Easy)**
   * **Scenario:** A noisy IP is flooding the pipeline with identical prompt-injection payloads.
   * **Objective:** The agent must identify the repetitive source and use `isolate_ip` to block it at the firewall level.

2. **Task 2: Contextual Prompt Injection (Medium)**
   * **Scenario:** Adversarial instructions (e.g., system prompt overrides) are hidden within normal-looking user queries from varying IPs.
   * **Objective:** The agent must inspect the payload bodies and use `flag_packet` to drop specific malicious requests while allowing benign traffic through.

3. **Task 3: Stealth Data Poisoning (Hard)**
   * **Scenario:** Payloads contain subtle statistical anomalies (e.g., impossible income brackets or skewed gradient data) designed to slowly drift and corrupt the backend model's weights over time. 
   * **Objective:** The agent must detect these deep semantic anomalies and quarantine them, balancing a high catch rate with a low false-positive rate.

## Setup & Reproducibility

### Local Validation
Ensure you have `uv` installed, then run the OpenEnv validator:
```bash
openenv validate