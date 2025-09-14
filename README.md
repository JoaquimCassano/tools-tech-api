# OCR API

A FastAPI-based OCR service using Modal for serverless deployment.

## Features

- Text extraction from images using Tesseract OCR
- Image preprocessing with green background removal
- Support for multiple languages
- Base64 image input
- Health check endpoint

## Endpoints

### POST /extract_text

Extract text from an image.

**Request Body:**

```json
{
  "image_data": "base64_encoded_image_string",
  "language": "eng"
}
```

**Response:**

```json
{
  "text": "Extracted text from the image",
  "language": "eng"
}
```

### GET /health_check

Check if the API is running.

**Response:**

```json
{
  "status": "healthy",
  "message": "OCR API is running"
}
```

## Deployment

### Development

```bash
modal serve src/ocr.py
```

### Production

```bash
modal deploy src/ocr.py
```

## Usage Example

```python
import requests
import base64

with open("image.png", "rb") as f:
    image_data = base64.b64encode(f.read()).decode()

response = requests.post(
    "https://your-modal-url/extract_text",
    json={
        "image_data": image_data,
        "language": "eng"
    }
)

result = response.json()
print(result["text"])
```

## Supported Languages

- eng (English)
- por (Portuguese)
- Add more by installing additional tesseract language packages

## Image Processing

The API automatically:

- Removes green backgrounds
- Applies denoising and blur
- Scales small images for better OCR accuracy
- Applies OTSU thresholding
