import pytesseract
from PIL import Image
import io
from loguru import logger
from app.core.config import settings
from app.core.exceptions import OCRError


class OCRService:

    def __init__(self):
        # set tesseract path if given (needed on Windows)
        if settings.TESSERACT_PATH:
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_PATH

    def extract_text(self, image_bytes: bytes) -> str:
        """Run OCR on image bytes and return raw text"""
        try:
            image = Image.open(io.BytesIO(image_bytes))

            # convert to RGB if needed (e.g. PNG with alpha channel)
            if image.mode not in ("RGB", "L"):
                image = image.convert("RGB")

            # page segmentation mode 3 = fully automatic, no OSD
            config = "--psm 3 --oem 3"
            text = pytesseract.image_to_string(image, config=config, lang="eng")

            cleaned = text.strip()
            if not cleaned:
                logger.warning("OCR returned empty text")
                raise OCRError("No text could be extracted from the image")

            logger.debug(f"OCR extracted {len(cleaned)} characters")
            return cleaned

        except OCRError:
            raise
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            raise OCRError(f"OCR processing failed: {str(e)}")

    def extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        """Convert first page of PDF to image, then OCR it"""
        try:
            # using PIL's built-in PDF support isn't great, 
            # but avoids adding pdf2image/poppler dependency
            image = Image.open(io.BytesIO(pdf_bytes))
            image_bytes = io.BytesIO()
            image.save(image_bytes, format="PNG")
            return self.extract_text(image_bytes.getvalue())
        except Exception as e:
            logger.error(f"PDF OCR failed: {e}")
            raise OCRError(f"Could not process PDF: {str(e)}")
