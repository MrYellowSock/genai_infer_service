from pydantic import BaseModel
from typing import List,Optional

class EasyUrlFile(BaseModel):
    url:str
    mime_type:str
    bytes:bytes
    file_size:int

class PromptInferMessage(BaseModel):
    system_msg:List[str|EasyUrlFile]
    human_msg:List[str|EasyUrlFile]

# Define more config as needed.
class PromptInferAiConfig(BaseModel):
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    genai_model:str
    class Config:
        extra = "ignore" 
