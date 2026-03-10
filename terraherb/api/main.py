from fastapi import FastAPI, File, UploadFile
from terraherb.inference.predict import PlantPredictor
from terraherb.knowledge.client import KnowledgeRetriever

app = FastAPI(title="Terraherb Plant Identification API")

predictor = PlantPredictor()
retriever = KnowledgeRetriever()

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "terraherb-ai-substrate"}

@app.post("/identify")
async def identify_plant(file: UploadFile = File(...)):
    """
    Endpoint to identify plant species from an uploaded image.
    """
    bytes_data = await file.read()
    species = predictor.predict(bytes_data)
    info = retriever.fetch_plant_data(species)
    
    return {
        "prediction": species,
        "details": info
    }
