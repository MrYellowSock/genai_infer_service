from starlette.routing import BaseRoute
from genai_infer_service.models.Registration import PromptRegisFull
from genai_infer_service.models.Swag import InputConfigEntrySwag, InputPromptEntrySwag, SelectableSwag, Swag
from fastapi import APIRouter, FastAPI, responses
from fastapi.openapi.utils import get_openapi

def create_openapi_single_path(router:APIRouter):
    app = FastAPI()
    app.include_router(router)
    openapi_schema = get_openapi(
        title="Custom API",
        version="1.0.0",
        description="This is a custom OpenAPI schema",
        routes=app.routes
    )
    paths = list(openapi_schema["paths"].values())
    first_path = paths[0]
    responses = list(first_path.values())[0]["responses"]
    return { "responses":responses, "components":openapi_schema["components"] }


# Pretty much just adding name and combine them.
def get_swag_input_fields(fulltemplate:PromptRegisFull) -> list[Swag]:
    results = []
    for field_name,field_prop in fulltemplate.input.prompt.items():
        b = InputPromptEntrySwag(name=field_name,**vars(field_prop))
        results.append(b)

    for field_name,field_prop in fulltemplate.input.configurable:
        b = InputConfigEntrySwag(name=field_name,**vars(field_prop))
        results.append(b)

    # additional field for selecting models
    results.append(SelectableSwag(name="genai_model",required=False,enum=fulltemplate.genai_models))

    return results
        

def create_openapi_spec(
        request_path:str,
        method:str,
        fields:list[Swag],
        schema:dict
):
    formSchema = {
        "type": "object",
        "properties": {
        },
        "required": [
        ]
    }
    jsonSchema = {
        "type": "object",
        "properties": {
        }
    }

    for field in fields:
        formSchema["properties"][field.name] = field.get_schema_form()
        jsonSchema["properties"][field.name] = field.get_schema_json()
        if field.required:
            formSchema["required"].append(field.name)

    return {
      "openapi": "3.0.0",
      "info": {
          "title": "Generated api", "version": "1.0.0"
        },
      "paths": {
        request_path: {
          method: {
            "summary": "inference",
            "requestBody": {
              "content": {
                "multipart/form-data": {
                  "schema": formSchema
                },
                "application/json":{
                    "schema": jsonSchema
                }
              },
              "required": True
            },
            "responses": schema[ "responses"]
          }
        },
      },
      "components":schema[ "components"]
    }
