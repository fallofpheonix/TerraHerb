#!/usr/bin/env python3
"""
Terraherb — root entry point.

Launches the FastAPI application via uvicorn.

Usage:
    python main.py
    # or via uvicorn directly:
    uvicorn terraherb.api.main:app --reload --host 0.0.0.0 --port 8000
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "terraherb.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
