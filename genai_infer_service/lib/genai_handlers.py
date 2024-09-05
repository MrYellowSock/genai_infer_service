import os
from genai_infer_service.models.Infer import EasyUrlFile, PromptInferAiConfig, PromptInferMessage
import google.generativeai as genai
from genai_infer_service.models.decorators import genai_handler

# TODO: use file api if size is >20MB or is video.
@genai_handler(id="google-gemini-1.5-flash", vendor="google", vendor_model='gemini-1.5-flash')
def handler1(prompt:PromptInferMessage, config:PromptInferAiConfig):
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    def convert(item:str|EasyUrlFile):
        if isinstance(item,str):
            return item
        else:
            return {
                "mime_type": item.mime_type,
                "data": item.bytes
            }

    #This doesn't need system message?

    model = genai.GenerativeModel('models/gemini-1.5-flash')
    return model.generate_content(
        contents=[convert(msg) for msg in (prompt.human_msg)],
        generation_config=genai.GenerationConfig(
            temperature=config.temperature,
            top_p=config.top_p
        )
    ).text


@genai_handler(id="dummy", vendor="suppanut", vendor_model='promaster64')
def handler2(prompt:PromptInferMessage, config:PromptInferAiConfig):
    return {
        "text":"Hooray"
    }
