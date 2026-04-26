class LoveEmotionException(Exception):
    """Base exception for Love Emotion API"""
    pass

class InvalidInputException(LoveEmotionException):
    """Raised when input is invalid"""
    pass

class UnsafeContentException(LoveEmotionException):
    """Raised when content is unsafe"""
    pass

class AIServiceException(LoveEmotionException):
    """Raised when AI service fails"""
    pass

class DatabaseException(LoveEmotionException):
    """Raised when database operation fails"""
    pass
