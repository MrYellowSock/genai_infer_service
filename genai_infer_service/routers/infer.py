from genai_infer_service.lib.genai import consume_model
from genai_infer_service.lib.openapi import create_openapi_single_path, get_swag_input_fields
from fastapi import APIRouter, UploadFile
from fastapi.requests import Request
from genai_infer_service.lib.prompt_template import create_msgs_from_template_mixed, query_model
from genai_infer_service.models.Infer import PromptInferAiConfig, PromptInferMessage

async def extract(request:Request ,model_input_fields):
    extracted = {}
    content_type = request.headers.get('content-type')
    if content_type == 'application/json':
        json_data = await request.json()
        for field in model_input_fields:
            extracted[field.name] = await field.get_value_json(json_data)
        return extracted
    elif not content_type is None and 'multipart/form-data' in content_type:
        form = await request.form()
        for field in model_input_fields:
            extracted[field.name] = await field.get_value_form(form)
        return extracted
    raise ValueError(f"Unsupported content-type {content_type}")

router = APIRouter(tags=["infer"])

# TODO : /genai/prompts/{name}/infer
@router.post("/genai/prompts/{name}/versions/{version}/infer")
async def infer(request: Request,name:str, version:str):
    model = query_model(name,version)
    model_input_fields = get_swag_input_fields(model)
    try:
        extracted = await extract(request,model_input_fields)
        # extract config
        prompt_config = PromptInferAiConfig(**extracted)
        # extract prompt
        prompt = PromptInferMessage(
            system_msg=create_msgs_from_template_mixed(model.prompt_template.system_msg ,extracted),
            human_msg=create_msgs_from_template_mixed(model.prompt_template.human_msg ,extracted)
        )
        return consume_model(prompt,prompt_config)
    except ValueError as e:
        return {"error":str(e)}
    except ModuleNotFoundError as e:
        return {"error":str(e)}

openapi_infer_responses_schema = create_openapi_single_path(router)
