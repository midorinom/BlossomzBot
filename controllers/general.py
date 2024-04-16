async def make_api_call(controller_function, payload):
    try:
        response = await controller_function(payload)
        return response
    
    except Exception:
        print(f"An error occurred while trying to make an api call using {controller_function}.")
        raise
    