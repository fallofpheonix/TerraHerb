# 🤝 CONTRIBUTING.md (AI/ML Edition)

Welcome to the **Terraherb** group. We value technical precision, data integrity, and model reproducibility.

## 🏛️ Contribution Philosophy
We follow a **"Reproducibility-First"** approach. Whether you are tuning a hyperparameter or updating a preprocessing script, ensure the process is documented and repeatable.

## 🛠️ Development Workflow
1. **Fork/Branch**: Create a feature branch off `main`.
2. **Implement**: 
   - Write clean, PEP 8 compliant Python code.
   - Use `notebooks/` for exploration, but move stable logic to `src/terraherb/`.
3. **Document**: Update relevant `.md` files in `docs/` if your change affects model architecture or data pipelines.
4. **Test**: Ensure all `pytest` suites pass.
5. **PR**: Submit a pull request with a summary of the approach and any relevant metric improvements.

## 🎨 Styling Standards
- **Python**: Adhere to PEP 8. Use standard docstrings for all modules and functions.
- **Notebooks**: Clear all outputs before committing unless the experiment visuals are required for review.
- **Markdown**: Use GH-flavored markdown with premium formatting.

## 🤖 AI Assistance
If you are using AI tools, you MUST abide by the ML-specific protocols in [AGENTS.md](AGENTS.md).

---

*Thank you for helping us advance herbal intelligence.*
