import inspect
import genai_infer_service.lib.genai_handlers as genai_handlers
from genai_infer_service.models.Infer import PromptInferMessage,PromptInferAiConfig

# Get all functions from the imported module
functions = inspect.getmembers(genai_handlers, inspect.isfunction)

def get_available_models():
    return [
        {
            "id":func.id,
            "vendor":func.vendor,
            "vendor_model":func.vendor_model
        }
        for name,func in functions if hasattr(func,'id')
    ]

def consume_model(prompt:PromptInferMessage, config:PromptInferAiConfig):
    for name,func in functions:
        if hasattr(func,'id') and func.id == config.genai_model:
            # TODO : What else should we return.
            return func(prompt,config)
    raise ModuleNotFoundError(f"no genai with id {config.genai_model}")
