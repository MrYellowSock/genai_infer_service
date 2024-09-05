from typing import Any
from jinja2 import Environment, Template, meta,DebugUndefined

from genai_infer_service.models.Registration import PromptRegisFull

def classify_inputs(inputs:dict[str,Any]):
    text_input = {}
    file_input = {}
    for key,value in inputs.items():
        if isinstance(value,str) or (isinstance(value,list) and len(value) >0 and isinstance(value[0],str)):
            text_input[key] = value
        else:
            file_input[key] = value
    return {
        "text_input":text_input,
        "file_input":file_input
    }

def insert_at_odd_indices(arr, item):
    i = 1
    while i < len(arr):
        arr.insert(i, item)
        i += 2  # Move two steps forward to insert at the next odd index
    return arr

flatten=lambda l: sum(map(flatten,l),[]) if isinstance(l,list) else [l]

#  - subtitute the file variable with SPECIAL string
#  - split them with SPECIAL unique string (instead of actual variable string for extra safety)
#       - such as #file1# #file2#
def create_msgs_from_template(template_string:str,text_input:dict[str,str], file_input:dict[str,Any]):
    template = Template(template_string,undefined=DebugUndefined)
    
    special_input = {}
    for key in file_input.keys():
        special_input[key] = '{{' + key + '}}'

    template2 = Template(template.render(**text_input),undefined=DebugUndefined)
    file_clean_str:str = template2.render(**special_input)

    result:list[Any] = [file_clean_str]
    for key,value in file_input.items():
        split_keyword = special_input[key]

        for i in range(len(result)):
            if isinstance(result[i],str):
                contents = result[i].split(split_keyword)
                mixed = insert_at_odd_indices(contents,value)
                result[i] = mixed

        result = flatten(result)
    return result

def create_msgs_from_template_mixed(template_string:str,inputs:dict[str,Any]):
    classified = classify_inputs(inputs)
    return create_msgs_from_template(template_string, classified["text_input"], classified["file_input"])

def query_model(name:str, version:str) -> PromptRegisFull:
    # TODO : pull stuff out of db
    # Return dummy for now.

    # Example JSON string
    # TODO : pull stuff out of db
    # Return dummy for now.
    import json
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
            "type": "string",
            "required":true
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
        "openai-gpt4",
        "dummy"
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
    return input_data
