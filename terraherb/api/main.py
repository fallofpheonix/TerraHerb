"""
Terraherb FastAPI Gateway — Plant Identification & Botanical Intelligence API.

Endpoints:
  GET  /health            — Liveness probe
  GET  /ready             — Readiness probe (checks model + knowledge base)
  POST /identify          — Upload image → species prediction + botanical metadata
  GET  /classes           — List all 38 supported plant classes
  GET  /treatment/{label} — Fetch treatment guide for a specific disease label
"""

from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from terraherb.inference.classifier import PLANT_CLASSES
from terraherb.inference.predict import PlantPredictor
from terraherb.knowledge.client import KnowledgeRetriever, _get_treatment

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App state (populated on startup)
# ---------------------------------------------------------------------------

_state: dict[str, Any] = {}

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load heavy objects once at startup, release on shutdown."""
    logger.info("🌿 Terraherb AI substrate starting up…")
    start = time.perf_counter()
    _state["predictor"] = PlantPredictor()
    _state["retriever"] = KnowledgeRetriever()
    _state["startup_time"] = time.perf_counter() - start
    logger.info("✅ Ready in %.2fs", _state["startup_time"])
    yield
    logger.info("🌿 Shutting down.")
    _state.clear()


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Terraherb Plant Identification API",
    description=(
        "Deep learning plant species and disease identification powered by "
        "MobileNetV2, enriched with GBIF taxonomy and UCI Plants data."
    ),
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    startup_time_seconds: float | None = None


class TopPrediction(BaseModel):
    label: str
    probability: float = Field(..., ge=0.0, le=1.0)


class IdentifyResponse(BaseModel):
    species: str
    crop: str
    condition: str
    is_healthy: bool
    confidence: float = Field(..., ge=0.0, le=1.0)
    low_confidence: bool
    top_predictions: list[TopPrediction]
    knowledge: dict
    latency_ms: float


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse, tags=["Ops"])
def health_check() -> HealthResponse:
    """Liveness probe — always returns 200 if the process is running."""
    return HealthResponse(
        status="healthy",
        service="terraherb-ai-substrate",
        version=app.version,
        startup_time_seconds=_state.get("startup_time"),
    )


@app.get("/ready", tags=["Ops"])
def readiness_check() -> JSONResponse:
    """Readiness probe — 200 only when the model is loaded."""
    predictor: PlantPredictor | None = _state.get("predictor")
    if predictor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not yet loaded.",
        )
    return JSONResponse({"status": "ready", "classes": len(PLANT_CLASSES)})


@app.post(
    "/identify",
    response_model=IdentifyResponse,
    status_code=status.HTTP_200_OK,
    tags=["Inference"],
    summary="Identify plant species/disease from an image",
)
async def identify_plant(file: UploadFile = File(...)) -> IdentifyResponse:
    """
    Upload a plant leaf / crop image to receive:
    - Species / disease classification
    - Confidence score + top-3 predictions
    - Full botanical metadata (taxonomy, treatment, distribution)
    """
    # --- Validation ---
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type '{file.content_type}'. Accepted: {ALLOWED_MIME_TYPES}",
        )

    image_bytes = await file.read()
    if len(image_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large ({len(image_bytes) / 1e6:.1f} MB). Max: 10 MB.",
        )
    if len(image_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Empty file received.",
        )

    # --- Inference ---
    predictor: PlantPredictor = _state["predictor"]
    retriever: KnowledgeRetriever = _state["retriever"]

    t0 = time.perf_counter()
    try:
        prediction = predictor.predict(image_bytes)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Image processing error: {exc}",
        )

    # --- Knowledge enrichment ---
    knowledge = retriever.fetch_plant_data(prediction["species"])
    latency_ms = (time.perf_counter() - t0) * 1000

    logger.info(
        "Identified '%s' (conf=%.2f) in %.1fms",
        prediction["species"],
        prediction["confidence"],
        latency_ms,
    )

    return IdentifyResponse(
        species=prediction["species"],
        crop=prediction["crop"],
        condition=prediction["condition"],
        is_healthy=prediction["is_healthy"],
        confidence=prediction["confidence"],
        low_confidence=prediction["low_confidence"],
        top_predictions=[TopPrediction(**p) for p in prediction["top_predictions"]],
        knowledge=knowledge,
        latency_ms=round(latency_ms, 2),
    )


@app.get("/classes", tags=["Metadata"])
def list_classes() -> JSONResponse:
    """Return the full list of 38 supported PlantVillage class labels."""
    return JSONResponse({"count": len(PLANT_CLASSES), "classes": PLANT_CLASSES})


@app.get("/treatment/{label:path}", tags=["Knowledge"])
def get_treatment(label: str) -> JSONResponse:
    """
    Fetch treatment recommendations for a disease label.

    The label can be a PlantVillage class string (e.g. 'Tomato___Early_blight')
    or a plain condition name (e.g. 'early blight').
    """
    # Normalise PlantVillage format
    if "___" in label:
        condition = label.split("___", 1)[1].replace("_", " ")
    else:
        condition = label

    treatment = _get_treatment(condition)
    return JSONResponse({"condition": condition, "treatment": treatment})


# ---------------------------------------------------------------------------
# Global exception handler
# ---------------------------------------------------------------------------

@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc: Exception):
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error. Please try again."},
    )
