# TerraHerb Engineering Improvements Log

Following a critical failure where a wheat image was misidentified as Orange/Huanglongbing and enriched with unrelated lichen data, the following improvements have been implemented.

## implemented: Priority 0 — Critical Failure Path

- [x] **Confidence Thresholding:** Increased `LOW_CONFIDENCE_THRESHOLD` from 0.55 to 0.70 to reduce false positives.
- [x] **Top-K Predictions:** Expanded inference output from top-3 to top-5 to provide better visibility into model uncertainty.
- [x] **Knowledge Retrieval Gating:** The API now blocks remote botanical lookups if the prediction confidence is below 0.70.
- [x] **Uncertainty Feedback:** Added an "uncertain" status in the API response when confidence is low, providing generic safety advice instead of potentially misleading specific data.

## Implemented: Priority 1 — Knowledge Retrieval Repair

- [x] **Canonical Mapping:** Added `CROP_SCIENTIFIC_NAME_MAP` to map common crop names (e.g., "Orange") to their specific botanical names (e.g., "Citrus sinensis"). This prevents name collisions with people or unrelated fungi/lichens (e.g., "Alan Orange").
- [x] **Taxonomy Validation:** Added kingdom-level validation (`Plantae`) to GBIF retrieval. Any non-plant results are now rejected by the pipeline.
- [x] **Unit Testing:** Added new test cases to verify:
    - Low-confidence gating logic.
    - Canonical name lookup.
    - Non-plant taxonomy rejection.

## Implemented: Priority 1 & 2 — OOD Detection & Scope Transparency

- [x] **Explicit OOD Detection:** The API now distinguishes between `uncertain` (low confidence) and `unsupported` (extremely low confidence, likely Out-of-Distribution crop) results.
- [x] **Scope API:** Added `/identify/scope` endpoint that returns a structured map of all 38 supported crop/disease pairs.
- [x] **UI Scope Visibility:** The frontend now displays "Supported Crops" pills in the hero section, clearly defining the system's operational boundaries.
- [x] **Failure Mode UI:** Implemented specific warning banners for "Unsupported Crop" and "Uncertain Identification," providing better user guidance and preventing misinformation.
- [x] **Internal Debugging Visibility:** Low-confidence results still show the "Best Statistical Guess" but dim the main result and provide a strong warning, preserving transparency without sacrificing trust.

## Next Steps (Planned Priorities)

- [ ] **Priority 2 (Dataset Quality):** Build a confusion matrix and add wheat-specific validation sets to address the core misclassification.
- [ ] **Priority 4 (Architecture):** Separate the Crop Classifier from the Disease Classifier into a two-stage pipeline.
- [ ] **Priority 6 (UX):** Implement a "User Correction" workflow (e.g., "This is Wheat") to collect active learning data.
