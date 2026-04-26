from typing import Any, Dict

def format_success_response(data: Any, message: str = "Success") -> Dict:
    """Format success response"""
    return {
        "success": True,
        "message": message,
        "data": data
    }

def format_error_response(error: str, code: int = 500) -> Dict:
    """Format error response"""
    return {
        "success": False,
        "error": error,
        "code": code
    }
