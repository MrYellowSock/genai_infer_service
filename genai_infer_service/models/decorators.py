def genai_handler(id:str, vendor:str, vendor_model:str, accepted_mimes:list[str]):
    def decorator(func):
        func.id = id
        func.vendor = vendor
        func.vendor_model = vendor_model
        func.accepted_mimes = accepted_mimes
        return func
    return decorator


