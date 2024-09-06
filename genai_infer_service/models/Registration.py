import re
from pydantic import BaseModel, Field,field_validator,ValidationInfo
from typing import List, Literal, Optional,Any,TypeVar,Generic

from genai_infer_service.lib.genai import get_available_ids

class PromptRegisEntryInput(BaseModel):
    type: Literal['string', 'file', 'files']
    file_types: List[str]=Field(default=[])
    required: bool = Field(default=False)
    max_length: Optional[int] = Field(default=None)
    description: Optional[str] = Field(default=None)
    max_file_size: Optional[int] = Field(default=None)

    @field_validator("file_types")
    def valid_file_types(cls, v: list[ str ], info: ValidationInfo) -> list[ str ]:
        if len(v)>0 and info.data['type'] not in ['file', 'files']:
            raise ValueError("Only file can have this")
        for fileExt in v:
            if fileExt == "*":
                continue
            elif re.match(r'^\.\w+', fileExt, re.IGNORECASE):
                continue
            else:
                raise ValueError(f"Invalid extension '{fileExt}' do you have '.' ?")
        return v

T = TypeVar('T')
class PromptRegisEntryConfig(BaseModel, Generic[T]):
    required: bool = Field(default=False)
    # enforce default, we don't want default value flying around in server
    # we also use this to infer type.
    default:  T  
    description: Optional[str] = Field(default=None)

# Define more config as needed.
class PromptRegisAiConfig(BaseModel):
    temperature: Optional[PromptRegisEntryConfig[float]] = Field(
        default=None
    )
    top_p: Optional[PromptRegisEntryConfig[float]] = Field(
        default=None
    )


class PromptRegisInput(BaseModel):
    prompt: dict[str, PromptRegisEntryInput ]
    configurable: PromptRegisAiConfig

    @field_validator("prompt")
    def valid_name(cls, v: dict[str,PromptRegisEntryInput], info: ValidationInfo) -> dict[str,PromptRegisEntryInput]:
        for key in v.keys():
            if not key:
                raise ValueError("Name cannot be empty")
            if not re.match(r'^[a-zA-Z0-9_]+$', key):
                raise ValueError("Name can only contain letters, numbers, and underscores")
        return v

class PromptRegisMessage(BaseModel):
    system_msg:str
    human_msg:str

class PromptRegisFull(BaseModel): 
    input:PromptRegisInput
    genai_models: List[str]
    prompt_template:PromptRegisMessage

    # TODO : validate valid models? likely not
    @field_validator("genai_models")
    def validate_genai_models(cls,v:list[str])->list[str]:
        if len(v) < 1:
            raise ValueError("Must have atleast one model")
        return v
