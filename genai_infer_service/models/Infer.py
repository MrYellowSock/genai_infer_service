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
    def get_preview(self):
        def convert(item:str|EasyUrlFile):
            if isinstance(item,str):
                return item
            else:
                return f'{item.mime_type} {item.file_size} bytes'
        return {
            "system_msg":[convert(msg) for msg in self.system_msg],
            "human_msg":[convert(msg) for msg in self.human_msg]
        }

# Define more config as needed.
class PromptInferAiConfig(BaseModel):
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    genai_model:str
    class Config:
        extra = "ignore" 
