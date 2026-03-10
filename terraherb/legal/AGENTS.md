# 🤖 AGENTS.md — Autonomous Contributor Protocol (AI/ML Edition)

This protocol defines the mandatory operational standards for all AI agents, LLMs, and autonomous systems contributing to the **Terraherb** repository.

## 🏛️ 1. Philosophical Grounding
Agents are treated as high-trust, low-privileged collaborators. Every action taken by an agent must be observable, reversible, and technically justified.

## 🛡️ 2. ML-Specific Operational Guards
1. **Experiment Tracking**: Agents must log all training runs using established tools (e.g., MLflow, W&B) if configured.
2. **Dataset Integrity**: Agents shall not modify `data/raw/` once a version is established. All changes must happen in `data/processed/`.
3. **Model Versioning**: Serialized weights must be committed to the `models/` registry using descriptive version tags.
4. **Notebook Etiquette**: Jupyter notebooks must be cleared of output before commit to minimize git diff noise, unless otherwise specified.

## 📝 3. Reporting Requirements
When executing complex tasks, agents must maintain a `task.md` to track:
- **Planning**: Understanding the intent and mapping the approach.
- **Execution**: Real-time progress of file modifications.
- **Verification**: Documented proof (e.g., test metrics) that the change works.

## 🚫 4. Red Lines
- Agents shall not bypass model validation checks.
- Agents shall not overwrite model weights without explicit human approval.
- Agents shall not commit large datasets (>10MB) directly to the repository; use DVC or external storage pointers.

---

*This document is version-controlled. Any change to the agent protocol requires a peer-reviewed PR.*
