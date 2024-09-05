from fastapi import FastAPI
from genai_infer_service.routers.infer import router as infer_router
from genai_infer_service.routers.model import router as model_router
from genai_infer_service.routers.genai import router as genai_router

app = FastAPI()

# Include routes from infer.py
app.include_router(infer_router, prefix="")

# Include routes from model.py
app.include_router(model_router, prefix="")

app.include_router(genai_router, prefix="")

# Optionally, add a root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI app"}
