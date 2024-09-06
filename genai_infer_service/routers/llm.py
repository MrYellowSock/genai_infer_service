from fastapi import APIRouter, HTTPException
from genai_infer_service.lib.genai import get_available_models

router = APIRouter(tags=['llm'])

@router.get("/genai/llm/")
def get_llms():
    return get_available_models()

@router.get("/genai/llm/{id}")
def get_llm(id:str):
    models = get_available_models()
    for m in models:
        if m['id'] == id:
            return m
    raise HTTPException(status_code=404, detail="Model not found")
