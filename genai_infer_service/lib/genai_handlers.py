import time
import tempfile
import os
from genai_infer_service.models.Infer import EasyUrlFile, PromptInferAiConfig, PromptInferMessage
import google.generativeai as genai
from genai_infer_service.models.decorators import genai_handler

# TODO : intensive testing
# some gif just doesn't work
# If file is sent before text prompt This also happens!
# "I cannot see or analyze any image. I am only a text-based chat assistant. \n"
@genai_handler(id="google-gemini-1.5-flash", vendor="google", vendor_model='gemini-1.5-flash')
def handler1(prompt:PromptInferMessage, config:PromptInferAiConfig):
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    def convert(item:str|EasyUrlFile):
        if isinstance(item,str):
            return item
        else:
            if item.file_size > 20000000 or item.mime_type.startswith('video'):
                with tempfile.NamedTemporaryFile(delete=True) as tmp_file:
                    tmp_file.write(item.bytes)
                    tmp_file_path = tmp_file.name
                    cloud_file = genai.upload_file(path=tmp_file_path, mime_type=item.mime_type)
                    # Wait until the uploaded video is available
                    while cloud_file.state.name == "PROCESSING":
                        print('.', end='')
                        time.sleep(5)
                        cloud_file = genai.get_file(cloud_file.name)

                    if cloud_file.state.name == "FAILED":
                        raise ValueError(cloud_file.state.name)
                    return cloud_file
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
    return "hooray"
