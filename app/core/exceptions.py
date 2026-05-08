from fastapi import HTTPException


class DocumentProcessingError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class UnsupportedDocumentTypeError(Exception):
    def __init__(self, doc_type: str):
        self.message = f"Document type '{doc_type}' is not supported"
        super().__init__(self.message)


class OCRError(Exception):
    """Raised when tesseract fails or returns empty text"""
    pass


class LLMError(Exception):
    """Raised when OpenAI call fails"""
    pass


class FileTooLargeError(Exception):
    def __init__(self, size_mb: float, max_mb: int):
        self.message = f"File size {size_mb:.1f}MB exceeds limit of {max_mb}MB"
        super().__init__(self.message)


# HTTP exception helpers
def not_found(detail: str = "Resource not found"):
    return HTTPException(status_code=404, detail=detail)


def bad_request(detail: str):
    return HTTPException(status_code=400, detail=detail)


def server_error(detail: str = "Internal server error"):
    return HTTPException(status_code=500, detail=detail)
