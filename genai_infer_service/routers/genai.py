from fastapi import APIRouter
from genai_infer_service.lib.genai import get_available_models

router = APIRouter(tags=['genai'])

@router.get("/genai/genai/")
def get_model_openapi():
    return get_available_models()
