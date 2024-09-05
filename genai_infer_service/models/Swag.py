# json/toml -> validate -> python model -> openapi json
                         # python model + input -> prompt

# json/toml to valid python object
from abc import ABC, abstractmethod
from typing import Optional,List,Union,Any,Literal
from fastapi.datastructures import FormData
from pydantic import BaseModel 

from starlette.datastructures import UploadFile
from genai_infer_service.lib.file import uploadfile_to_base64, validate_and_get_file
from genai_infer_service.models.Registration import PromptRegisEntryConfig, PromptRegisEntryInput

class Swag(BaseModel,ABC):
    name: str
    required: bool

    @abstractmethod
    def get_schema_form(self) -> dict:
        """Abstract method to get schema form."""
        pass

    @abstractmethod
    def get_schema_json(self) -> dict:
        """Abstract method to get schema JSON."""
        pass

    @abstractmethod
    async def get_value_form(self,form:FormData) -> Any:
        """Abstract method to get field value of form"""
        pass

    @abstractmethod
    async def get_value_json(self,json:Any) -> Any:
        """Abstract method to get field value of json"""
        pass

class InputPromptEntrySwag(PromptRegisEntryInput,Swag):
    def get_schema_form(self):
        if self.type == "string":
            return {
                "type":"string",
                "description":self.description if self.description else ""
            }
        elif self.type == "file":
            return {
                "type":"string",
                "format":"binary",
                "description": f"{self.description} (accept {' '.join(self.file_types)})"
            }
        elif self.type == 'files':
            return {
                "type":"array",
                "items": {
                    "type": "string",
                    "format":"binary"                   
                },
                "description":f"{self.description} (accept list of {' '.join(self.file_types)})"
            }
    
    def get_schema_json(self):
        if self.type == 'files':
            return {
                "type":"array",
                "items": {
                    "type": "string"
                }
            }
        elif self.type == "string" or self.type == "file":
            return {
                "type":"string",
                "nullable":not self.required
            }

    async def get_value_form(self,form:FormData) -> Any:
        values = form.getlist(self.name) 
        if len(values) == 0:
            if self.required :
                raise ValueError( f"required field missing at {self.name}" )
            else:
                return None
        
        if self.type == "string" and isinstance(values[0], str):
            return values[0]
        elif self.type == "file" and isinstance(values[0], UploadFile):
            url = await uploadfile_to_base64(values[0])
            return validate_and_get_file(url,self.file_types,self.max_file_size)
        elif self.type == 'files' and all(isinstance(file, UploadFile) for file in values):
            urls = [await uploadfile_to_base64(file) for file in values]
            return [validate_and_get_file(file,self.file_types,self.max_file_size) for file in urls]
        else:
            raise ValueError(f"unexpected type for {self.type} at {self.name}")

    async def get_value_json(self,json:Any) -> Any:
        value = json[self.name]
        if value is None:
            if self.required :
                raise ValueError( f"required field missing at {self.name}" )
            else:
                return None

        if self.type == "string" and isinstance(value, str):
            return value
        elif self.type == "file" :
            return validate_and_get_file(value,self.file_types,self.max_file_size)
        elif self.type == 'files' :
            return [validate_and_get_file(file,self.file_types,self.max_file_size) for file in value]
        else:
            raise ValueError(f"unexpected type for {self.type} at {self.name}")
        

# TODO : support more
class InputConfigEntrySwag(PromptRegisEntryConfig,Swag):
    def get_schema_form(self):
        if isinstance(self.default,str):
            return {
                "type":"string",
                "description":self.description if self.description else ""
            }
        elif isinstance(self.default,float):
            return {
                "type":"number",
                "description":self.description if self.description else ""
            }
        elif isinstance(self.default,int):
            return {
                "type":"integer",
                "description":self.description if self.description else ""
            }

    def get_schema_json(self):
        if isinstance(self.default,str):
            return {
                "type":"string",
                "nullable":not self.required
            }
        elif isinstance(self.default,float):
            return {
                "type":"number",
                "nullable":not self.required
            }
        elif isinstance(self.default,int):
            return {
                "type":"integer",
                "nullable":not self.required
            }

    async def get_value_form(self,form:FormData) -> Any:
        value = form.get(self.name) 
        if not value and not self.required:
            return self.default
        if not isinstance(value,str):
            raise ValueError(f"unexpected type at {self.name}")
        if isinstance(self.default,str):
            return value
        elif isinstance(self.default,float):
            return float(value)
        elif isinstance(self.default,int):
            return int(value)
        else:
            raise ValueError(f"unexpected type at {self.name}")

    async def get_value_json(self,json:Any) -> Any:
        value = json[self.name] 
        if not value and not self.required:
            return self.default
        elif type(value) == type(self.default):
            return value
        else:
            raise ValueError(f"unexpected type at {self.name}")

# selectables
class SelectableSwag(Swag):
    enum:list[str]
    def get_schema_form(self):
        return {
            "type":"string",
            "enum":self.enum
        }

    def get_schema_json(self):
        return {
            "type":"string",
            "nullable":not self.required,
            "enum":self.enum
        }

    async def get_value_form(self,form:FormData) -> Any:
        value = form.get(self.name) 
        if not value and not self.required:
            return self.enum[0]
        elif isinstance(value,str) :
            if value in self.enum:
                return value
            else:
                raise ValueError(f"value not in enum")
        else:
            raise ValueError(f"unexpected type at {self.name}")

    async def get_value_json(self,json:Any) -> Any:
        value = json[self.name]
        if not value and not self.required:
            return self.enum[0]
        elif isinstance(value,str) :
            if value in self.enum:
                return value
            else:
                raise ValueError(f"value not in enum")
        else:
            raise ValueError(f"unexpected type at {self.name}")
