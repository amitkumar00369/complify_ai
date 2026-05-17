class HttpStatusCode:
    OK =  200
    CREATED =  201
    BAD_REQUEST= 400
    UNAUTHORIZED= 401
    FORBIDDEN= 403
    NOT_FOUND= 404
    INTERNAL_SERVER_ERROR= 500



class SuccessMessage:
    CREATED = "Resource created successfully"
    FETCHED = "Data fetched successfully"
    UPDATED = "Resource updated successfully"
    DELETED = "Resource deleted successfully"
    LOGIN = "Login successful"
    LOGOUT = "Logout successful"

class ErrorMessage:
    NOT_FOUND = "Resource not found"
    BAD_REQUEST = "Invalid request data"
    UNAUTHORIZED = "Unauthorized access"
    FORBIDDEN = "Access forbidden"
    SERVER_ERROR = "Internal server error"
