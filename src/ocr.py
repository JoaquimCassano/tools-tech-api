import modal
import pytesseract
import cv2
import numpy as np
from PIL import Image
import subprocess
import base64
import io
from fastapi import HTTPException
from pydantic import BaseModel

modal_image = modal.Image.debian_slim(python_version="3.12").pip_install("pytesseract", "Pillow", "opencv-python-headless", "numpy", "fastapi[standard]").apt_install(['tesseract-ocr', 'tesseract-ocr-por', 'tesseract-ocr-eng', 'tesseract-ocr-spa', 'tesseract-ocr-fra'])
app = modal.App("ocr-app", image=modal_image)

class ImageRequest(BaseModel):
    image_data: str
    language: str = "auto"


def download_tesseract():
    subprocess.run(["apt-get", "update"], check=True)
    subprocess.run(["apt-get", "install", "-y", "tesseract-ocr"], check=True)
    subprocess.run(["apt-get", "install", "-y", "tesseract-ocr-eng"], check=True)

def process_image_for_ocr(image_data: str) -> np.ndarray:
    try:
        if image_data.startswith('data:'):
            image_data = image_data.split(',', 1)[1]

        image_bytes = base64.b64decode(image_data)
        pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img = np.array(pil_img)[:, :, ::-1]

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_green = np.array([35, 40, 40])
        upper_green = np.array([90, 255, 255])
        mask = cv2.inRange(hsv, lower_green, upper_green)
        img[mask > 0] = [255, 255, 255]

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        scale = 2 if max(h, w) < 1500 else 1
        if scale > 1:
            gray = cv2.resize(gray, (w * scale, h * scale), interpolation=cv2.INTER_CUBIC)

        gray = cv2.fastNlMeansDenoising(gray, None, h=10)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        return th
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")

@app.function(timeout=300)
@modal.fastapi_endpoint(method="POST")
def extract_text(request: ImageRequest) -> dict:
    try:
        pytesseract.get_tesseract_version()
    except Exception:
        download_tesseract()

    processed_image = process_image_for_ocr(request.image_data)

    custom_config = "--oem 1 --psm 3 "
    language = request.language if request.language != "auto" else None

    try:
        text = pytesseract.image_to_string(processed_image, config=custom_config, lang=language)
        return {"text": text.strip(), "language": request.language}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")

@app.function()
@modal.fastapi_endpoint(method="GET")
def health_check() -> dict:
    return {"status": "healthy", "message": "OCR API is running"}