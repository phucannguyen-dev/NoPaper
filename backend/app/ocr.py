import pytesseract
from PIL import Image
import io

def run_ocr(image_bytes: bytes) -> str:
    image = Image.open(io.BytesIO(image_bytes))
    text = pytesseract.image_to_string(image, lang="eng+vie")
    return text.strip()