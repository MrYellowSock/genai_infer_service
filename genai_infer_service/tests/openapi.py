from genai_infer_service.lib.openapi import create_openapi_spec, create_openapi_single_path, get_swag_input_fields
from genai_infer_service.models.Registration import PromptRegisFull
import json
from fastapi import APIRouter

router = APIRouter()

@router.get("/infer", tags=["infer"])
async def read_users():
    return [{"username": "Rick"}, {"username": "Morty"}]

original_resp_scheme =create_openapi_single_path(router)
print("Creating openapi",original_resp_scheme)

# Example JSON string
json_data = '''
{
  "input": {
    "prompt": {
      "images": {
        "type": "files",
        "file_types": [".png", ".jpeg", ".tiff"],
        "required": false,
        "max_length": 4,
        "description": "sfaf"
      },
      "file2": {
        "type": "file",
        "file_types": [".pdf"],
        "max_file_size": 2000000
      },
      "msg": {
        "type": "string"
      }
    },
    "configurable": {
        "temperature": {
          "default": 0
        },
        "top_p": {
          "required": true,
          "default":0.1
        }
    }
  },
  "genai_models": [
    "google-gemini-1.5-flash",
    "openai-gpt4"
  ],
  "prompt_template": {
    "system_msg": "You are going to help us do not resist",
    "human_msg": "Task: do this, do that\\n{{images}} - is it {{msg}}?\\n{{file2}}\\nthen\\n{\\n  ref: \\"\\"\\n}"
  }
}
'''

# Parse the JSON string into a Python dictionary
data_dict = json.loads(json_data)

# Load the data into the Pydantic model
input_data = PromptRegisFull.parse_obj(data_dict)

print("Input object:",input_data)

swag_fields = get_swag_input_fields(input_data)
print("Swagging time!",swag_fields)

openapi_json = create_openapi_spec("/blablah","post",swag_fields,original_resp_scheme)
json_formatted_str = json.dumps(openapi_json, indent=2)

print(json_formatted_str)
