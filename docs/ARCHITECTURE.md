# 🧬 Architectural Blueprint — Internal Logic

This document provides a deep-dive into the technical execution and sequence flow of the **Terraherb** AI substrate.

## 🏛️ System Topology
```mermaid
graph LR
    subgraph Frontend
        Web[React Digital Herbarium]
    end
    subgraph API_Layer
        FastAPI[FastAPI Gateway]
        Ingest[Image Ingestion]
    end
    subgraph ML_Substrate
        CNN[MobileNetV2 Engine]
        Weights[(Saved Weights .pth)]
    end
    subgraph Knowledge_Base
        UCI[UCI Plants Data]
        Remote[GBIF / Wikipedia API]
    end

    Web -- POST /identify --> FastAPI
    FastAPI --> Ingest
    Ingest --> CNN
    CNN -- Infer --> Weights
    Weights -- Class ID --> FastAPI
    FastAPI -- Enrich --> UCI
    FastAPI -- Query --> Remote
    UCI & Remote -- Metadata --> FastAPI
    FastAPI -- Structured Report --> Web
```

## 🔄 Interaction Sequence
1. **User Upload**: A raw image is submitted to the `/identify` endpoint.
2. **Preprocessing**: The image is resized to 224x224 and normalized using ImageNet statistics.
3. **Neural Inference**: The PyTorch model performs a forward pass to determine species/health class.
4. **Knowledge Retrieval**: The system queries the local UCI dataset and remote biological APIs.
5. **Response Synthesis**: Classification results and botanical metadata are merged into a single JSON response.

---
*Derived by AI. Built for Humanity.*
