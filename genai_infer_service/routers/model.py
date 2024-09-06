from fastapi import APIRouter, Request, UploadFile
from genai_infer_service.lib.openapi import create_openapi_spec, get_swag_input_fields
from genai_infer_service.lib.prompt_template import query_model, save_model
from genai_infer_service.models.Registration import PromptRegisFull
from fastapi.templating import Jinja2Templates
from genai_infer_service.routers.infer import openapi_infer_responses_schema

router = APIRouter(tags=['prompt'])

@router.get("/genai/prompts/{name}/versions/{version}")
def get_model_regular(name:str, version:str) -> PromptRegisFull :
    return query_model(name,version)

@router.put("/genai/prompts/{name}/versions/{version}")
def put_model_regular(name:str, version:str, template:PromptRegisFull):
    save_model(name,version,template)
    return {}

@router.get("/genai/prompts/{name}/versions/{version}/openapi")
def get_model_openapi(name:str, version:str):
    model = query_model(name,version)
    fields = get_swag_input_fields(model)
    return create_openapi_spec(
        f"/genai/prompts/{name}/versions/{version}/infer",
        "post",
        fields,
        openapi_infer_responses_schema
    )

templates = Jinja2Templates(directory="templates")
@router.get("/genai/prompts/{name}/versions/{version}/playground")
def playground(request:Request, name:str, version:str):
    return templates.TemplateResponse(
        "swagger_custom.html",
        {"request": request, "name": name, "version":version}
    )

