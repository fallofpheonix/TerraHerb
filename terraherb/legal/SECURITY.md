# 🛡️ SECURITY.md (AI/ML Edition)

## Security Policy

We take the security of the **Terraherb** AI substrate seriously. This document outlines our posture and how to report vulnerabilities.

## ⚡ Reporting a Vulnerability
Please do **not** open a public GitHub issue for security vulnerabilities. Instead, send a detailed report to `security@fallofpheonix.example.com`.

## 🏛️ Security Invariants
1. **Data Sanitization**: All external botanical datasets must be validated for malicious injections or adversarial triggers.
2. **Inference Hardening**: Model entry points must be sanitized to prevent prompt injection or weight-extraction attacks.
3. **Dependency Auditing**: We monitor `requirements.txt` and `pyproject.toml` for vulnerabilities in the ML stack.

## 🚫 Safe Model Loading
- Use `weights_only=True` when loading PyTorch models where possible.
- Avoid loading unsanitized `.pickle` or `.joblib` files from untrusted sources.

---

*Security is a process, not a state.*
