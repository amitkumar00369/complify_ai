from fastapi.responses import JSONResponse

def success_response(message, data=None, status_code=200):
    return JSONResponse(content={
        "success": True,
        "message": message,
        "data": data
    }, status_code=status_code)


def error_response(message, status_code=400):
    return JSONResponse(content={
        "success": False,
        "message": message,
        "data": None
    }, status_code=status_code)