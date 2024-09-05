import base64
import re
import mimetypes
from typing import Optional
from math import ceil

from genai_infer_service.models.Infer import EasyUrlFile

def is_base64_data_url(data_url: str) -> bool:
    # Regular expression to match base64 data URLs
    base64_data_url_pattern = r'^data:([a-zA-Z0-9-+/]+);base64,([a-zA-Z0-9+/]+={0,2})$'
    
    # Match the pattern
    return re.match(base64_data_url_pattern, data_url) is not None

def extract_base64_data(data_url: str) -> Optional[str]:
    if not is_base64_data_url(data_url):
        return None
    
    # Extract the base64 data (after the comma)
    return data_url.split(",")[1]

async def uploadfile_to_base64(file):
    # Read the file content as bytes
    file_bytes = await file.read()
    base64_encoded = base64.b64encode(file_bytes).decode("utf-8")
    data_url = f"data:{file.content_type};base64,{base64_encoded}"
    return data_url

def calculate_base64_file_size(base64_str):
    # Remove the data URL prefix (if present)
    if base64_str.startswith("data:"):
        base64_str = extract_base64_data(base64_str)
    if not base64_str:
        return 0
    # Calculate the size in bytes
    padding = base64_str.count('=')  # Padding characters at the end
    base64_length = len(base64_str)
    file_size = (base64_length * 3) / 4 - padding
    return ceil(file_size)

def get_content_type_from_base64(base64_str):
    # Check if the string has the data URL prefix
    if base64_str.startswith("data:"):
        # Split the string to extract the MIME type
        content_type = base64_str.split(";")[0].split(":")[1]
        return content_type
    else:
        return None

def extension_to_content_type(extension):
    if not extension.startswith('.'):
        extension = '.' + extension
    
    content_type, _ = mimetypes.guess_type('filename' + extension)
    
    return content_type if content_type else 'application/octet-stream'

def validate_and_get_file(data_url: str, allow_file_extensions: list[str], max_file_size: Optional[int] = None) -> EasyUrlFile:
    # Step 1: Check if the data URL is a valid base64-encoded string
    if not is_base64_data_url(data_url):
        raise ValueError("Invalid base64 data URL.")
    
    # Step 2: Extract the MIME type from the base64 data URL
    content_type = get_content_type_from_base64(data_url)
    if not content_type:
        raise ValueError("MIME type could not be determined from the data URL.")
    
    # Step 3: Check if the MIME type corresponds to one of the allowed file extensions
    allowed_content_types = [extension_to_content_type(ext) for ext in allow_file_extensions]
    if content_type not in allowed_content_types:
        raise ValueError(f"MIME type '{content_type}' is not allowed. Allowed types: {allowed_content_types}")
    
    # Step 4: Calculate the size of the base64-encoded file
    base64_data = extract_base64_data(data_url)
    if base64_data is None:
        raise ValueError("Invalid base64 data.")
    
    file_size = calculate_base64_file_size(data_url)
    
    # Step 5: If a max_file_size is specified, ensure the file does not exceed this size
    if max_file_size is not None and file_size > max_file_size:
        raise ValueError(f"File size exceeds the maximum allowed size of {max_file_size} bytes.")
    
    return EasyUrlFile(
            url=data_url,
            mime_type=content_type,
            file_size=file_size,
            bytes=base64.b64decode(base64_data)
    )

