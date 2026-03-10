"""
Botanical knowledge retrieval client.

Sources (in priority order):
  1. Local UCI Plants CSV  — fast, offline, regional distribution data
  2. GBIF REST API         — authoritative taxonomy + occurrence records
  3. Wikipedia REST API    — human-readable descriptions + uses

All remote calls are cached in-memory for the process lifetime to avoid
hammering external APIs during a single server run.
"""

from __future__ import annotations

import csv
import functools
import logging
import os
import time
from pathlib import Path
from typing import Optional

import requests

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

GBIF_API_BASE = "https://api.gbif.org/v1"
WIKIPEDIA_REST_BASE = "https://en.wikipedia.org/api/rest_v1/page/summary"
DEFAULT_UCI_PATH = "datasets_substrate/external/uci_plants/plants.data"
FALLBACK_UCI_PATHS = [
    "datasets_substrate/external/uci_plants/plants.data",
    "datasets_substrate/external/uci_plants/plants.csv",
    "data/external/uci_plants/plants.csv",
]
REQUEST_TIMEOUT = 8  # seconds

# Disease → treatment mapping (curated subset; extend as needed)
DISEASE_TREATMENT_MAP: dict[str, dict] = {
    "early blight": {
        "organic": ["Copper-based fungicide spray", "Neem oil application", "Remove infected leaves immediately"],
        "chemical": ["Chlorothalonil (Daconil)", "Mancozeb-based fungicide"],
        "prevention": ["Crop rotation (3-year cycle)", "Avoid overhead irrigation", "Mulch base of plant"],
    },
    "late blight": {
        "organic": ["Copper hydroxide spray", "Remove and destroy infected material"],
        "chemical": ["Metalaxyl + Mancozeb", "Dimethomorph-based systemic fungicide"],
        "prevention": ["Plant resistant varieties", "Ensure good air circulation", "Avoid wetting foliage"],
    },
    "black rot": {
        "organic": ["Bordeaux mixture (copper + lime)", "Remove mummified fruit"],
        "chemical": ["Captan fungicide", "Thiophanate-methyl"],
        "prevention": ["Prune for air circulation", "Sanitize pruning tools"],
    },
    "powdery mildew": {
        "organic": ["Baking soda spray (1 tsp / litre water)", "Diluted milk spray (40% milk)", "Potassium bicarbonate"],
        "chemical": ["Myclobutanil", "Trifloxystrobin"],
        "prevention": ["Avoid nitrogen over-fertilisation", "Plant in full sun"],
    },
    "bacterial spot": {
        "organic": ["Copper bactericide at first symptom", "Avoid working plants when wet"],
        "chemical": ["Streptomycin sulfate (where permitted)", "Copper-based bactericides"],
        "prevention": ["Use certified disease-free seed", "Crop rotation"],
    },
    "leaf scorch": {
        "organic": ["Remove and destroy affected leaves", "Apply balanced fertiliser"],
        "chemical": ["Captan fungicide"],
        "prevention": ["Ensure adequate soil moisture", "Mulch to retain moisture"],
    },
    "healthy": {
        "organic": [],
        "chemical": [],
        "prevention": ["Maintain regular watering schedule", "Monitor for early signs of stress", "Balanced NPK fertilisation"],
    },
}


def _get_treatment(condition: str) -> dict:
    """Return treatment recommendations for a disease condition."""
    condition_lower = condition.lower()
    for key, treatment in DISEASE_TREATMENT_MAP.items():
        if key in condition_lower:
            return treatment
    return {
        "organic": ["Consult local agricultural extension office"],
        "chemical": ["Consult a licensed agronomist"],
        "prevention": ["Monitor closely; isolate from other plants"],
    }


# ---------------------------------------------------------------------------
# UCI Plants local data
# ---------------------------------------------------------------------------

class UCIPlantsClient:
    """
    Reader for the UCI Plants dataset.

    Expected rows:
        plant_name, state_1, state_2, ... state_N
    Each column after the first is a US state where the plant occurs.
    """

    def __init__(self, csv_path: str = DEFAULT_UCI_PATH) -> None:
        self._path = Path(csv_path)
        self._index: dict[str, list[str]] = {}
        self._loaded = False

    def _load(self) -> None:
        if self._loaded:
            return
        if not self._path.exists():
            for candidate in FALLBACK_UCI_PATHS:
                cand_path = Path(candidate)
                if cand_path.exists():
                    self._path = cand_path
                    break

        if not self._path.exists():
            logger.warning("UCI Plants data not found at '%s'. Local lookup disabled.", self._path)
            self._loaded = True
            return
        try:
            with self._path.open(newline="", encoding="latin-1") as fh:
                reader = csv.reader(fh)
                for row in reader:
                    if row:
                        name = row[0].strip().lower()
                        states = [s.strip() for s in row[1:] if s.strip()]
                        self._index[name] = states
            logger.info("UCI Plants index loaded: %d entries.", len(self._index))
        except Exception as exc:
            logger.error("Failed to load UCI CSV: %s", exc)
        self._loaded = True

    def get_distribution(self, plant_name: str) -> list[str]:
        """Return list of US states where the plant is recorded."""
        self._load()
        name_lower = plant_name.lower()
        # Exact match first, then prefix match
        if name_lower in self._index:
            return self._index[name_lower]
        for key in self._index:
            if key.startswith(name_lower.split()[0]):
                return self._index[key]
        return []


# ---------------------------------------------------------------------------
# GBIF client
# ---------------------------------------------------------------------------

class GBIFClient:
    """Lightweight GBIF REST client with simple in-process response cache."""

    def __init__(self, base_url: str = GBIF_API_BASE) -> None:
        self._base = base_url
        self._cache: dict[str, dict] = {}

    def _get(self, endpoint: str, params: dict) -> Optional[dict]:
        url = f"{self._base}/{endpoint}"
        cache_key = url + str(sorted(params.items()))
        if cache_key in self._cache:
            return self._cache[cache_key]
        try:
            resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            self._cache[cache_key] = data
            return data
        except requests.RequestException as exc:
            logger.warning("GBIF request failed: %s", exc)
            return None

    def search_species(self, name: str) -> Optional[dict]:
        """
        Search for a species by name and return the best-matching result.
        Returns the first result dict, or None if nothing was found.
        """
        data = self._get("species/search", {"q": name, "limit": 1, "status": "ACCEPTED"})
        if data and data.get("results"):
            return data["results"][0]
        # Fall back to fuzzy match
        data = self._get("species/suggest", {"q": name, "limit": 1})
        if data and isinstance(data, list) and data:
            return data[0]
        return None

    def get_occurrence_count(self, taxon_key: int) -> int:
        """Return the total number of occurrence records for a taxon."""
        data = self._get("occurrence/search", {"taxonKey": taxon_key, "limit": 0})
        if data:
            return data.get("count", 0)
        return 0


# ---------------------------------------------------------------------------
# Wikipedia client
# ---------------------------------------------------------------------------

class WikipediaClient:
    """Fetches plain-language summaries from Wikipedia."""

    def __init__(self) -> None:
        self._cache: dict[str, str] = {}

    def get_summary(self, title: str) -> Optional[str]:
        """Return the first paragraph summary for a Wikipedia article."""
        if title in self._cache:
            return self._cache[title]
        try:
            resp = requests.get(
                f"{WIKIPEDIA_REST_BASE}/{requests.utils.quote(title)}",
                timeout=REQUEST_TIMEOUT,
                headers={"User-Agent": "TerraHerb/1.0 (plant-intelligence-app)"},
            )
            if resp.status_code == 200:
                summary = resp.json().get("extract", "")
                # Trim to first 3 sentences for brevity
                sentences = summary.split(". ")
                short = ". ".join(sentences[:3]).strip()
                if short and not short.endswith("."):
                    short += "."
                self._cache[title] = short
                return short
        except requests.RequestException as exc:
            logger.warning("Wikipedia request failed for '%s': %s", title, exc)
        return None


# ---------------------------------------------------------------------------
# Main KnowledgeRetriever
# ---------------------------------------------------------------------------

class KnowledgeRetriever:
    """
    Unified botanical knowledge client.

    Orchestrates UCI local data, GBIF taxonomy, Wikipedia descriptions,
    and the built-in disease treatment database to produce a rich metadata
    response for any predicted PlantVillage class.
    """

    def __init__(
        self,
        uci_path: str = DEFAULT_UCI_PATH,
        enable_remote: bool = True,
    ) -> None:
        self._uci = UCIPlantsClient(csv_path=uci_path)
        self._gbif = GBIFClient() if enable_remote else None
        self._wiki = WikipediaClient() if enable_remote else None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fetch_plant_data(self, species_label: str) -> dict:
        """
        Retrieve full botanical metadata for a PlantVillage class label.

        Args:
            species_label: Raw class label, e.g. "Tomato___Early_blight".

        Returns:
            Structured dict with taxonomy, treatment, distribution, and
            descriptive text fields.
        """
        crop, condition = self._parse_label(species_label)
        is_healthy = "healthy" in condition.lower()

        result: dict = {
            "raw_label": species_label,
            "crop": crop,
            "condition": condition,
            "is_healthy": is_healthy,
            "taxonomy": {},
            "description": None,
            "distribution_states": [],
            "occurrence_count": None,
            "treatment": _get_treatment(condition),
            "sources": [],
        }

        # --- Local UCI lookup ---
        distribution = self._uci.get_distribution(crop)
        if distribution:
            result["distribution_states"] = distribution
            result["sources"].append("UCI Plants Dataset")

        # --- Remote enrichment ---
        if self._gbif:
            gbif_data = self._gbif.search_species(crop)
            if gbif_data:
                result["taxonomy"] = {
                    "kingdom": gbif_data.get("kingdom", "Plantae"),
                    "phylum": gbif_data.get("phylum"),
                    "class": gbif_data.get("class"),
                    "order": gbif_data.get("order"),
                    "family": gbif_data.get("family"),
                    "genus": gbif_data.get("genus"),
                    "species": gbif_data.get("species"),
                    "scientific_name": gbif_data.get("scientificName", crop),
                    "canonical_name": gbif_data.get("canonicalName", crop),
                    "gbif_key": gbif_data.get("key"),
                    "conservation_status": gbif_data.get("threatStatuses", ["Not Evaluated"])[0]
                    if gbif_data.get("threatStatuses")
                    else "Not Evaluated",
                }
                if gbif_data.get("key"):
                    result["occurrence_count"] = self._gbif.get_occurrence_count(gbif_data["key"])
                result["sources"].append("GBIF (Global Biodiversity Information Facility)")

        if self._wiki:
            # Try crop name first, then scientific name if available
            wiki_title = result["taxonomy"].get("canonical_name", crop)
            description = self._wiki.get_summary(wiki_title)
            if not description and wiki_title != crop:
                description = self._wiki.get_summary(crop)
            if description:
                result["description"] = description
                result["sources"].append("Wikipedia")

        # Ensure taxonomy has at least a fallback scientific_name
        if not result["taxonomy"]:
            result["taxonomy"] = {
                "scientific_name": crop,
                "canonical_name": crop,
                "kingdom": "Plantae",
            }

        return result

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_label(label: str) -> tuple[str, str]:
        """Split 'Tomato___Early_blight' into ('Tomato', 'Early blight')."""
        parts = label.split("___", 1)
        crop = parts[0].replace("_", " ").strip()
        condition = parts[1].replace("_", " ").strip() if len(parts) > 1 else "Unknown"
        return crop, condition
