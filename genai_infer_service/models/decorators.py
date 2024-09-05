def genai_handler(id:str, vendor:str, vendor_model:str):
    def decorator(func):
        func.id = id
        func.vendor = vendor
        func.vendor_model = vendor_model
        # if file type is bad just forward error from genai provider?
        return func
    return decorator


