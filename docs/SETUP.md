# 🚀 SETUP.md — AI/ML Developer Onboarding

Follow these steps to bootstrap the **Terraherb** AI ecosystem on your local machine.

## 🛠️ Prerequisites
- **Python**: v3.8+ (v3.10 recommended)
- **pip**: Latest version
- **Virtualenv**: Recommended for dependency isolation.

## 📦 Local Setup

### 1. Repository Initialization
```bash
git clone https://github.com/fallofpheonix/terraherb.git
cd terraherb
```

### 2. Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Dependency Installation
```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .  # Install the terraherb package in editable mode
```

## 🧪 Verification
Run the verification script to ensure the ML environment is healthy:
```bash
python -m pytest tests/
./scripts/check-health.sh
```

## 🤖 AI Agent Setup
Autonomous contributors must adhere to the [AGENTS.md](../../terraherb/AGENTS.md) protocol.

---

*Welcome to the future of herbal intelligence.*
