import modal
import pytesseract

modal_image = modal.Image.debian_slim(python_version="3.12").pip_install("pytesseract", "Pillow").apt_install(['tesseract-ocr', 'tesseract-ocr-por']).add_local_file("../foto.png", remote_path="/app/img.png")
app = modal.App("ocr-app", image=modal_image)


def download_tesseract():
    import subprocess
    subprocess.run(["apt-get", "update"], check=True)
    subprocess.run(["apt-get", "install", "-y", "tesseract-ocr"], check=True)

@app.function(gpu="T4", timeout=8000)
def ocr_image() -> str:
    try:
      pytesseract.get_tesseract_version()
    except:
      download_tesseract()
    from PIL import Image
    img = Image.open("/app/img.png")
    text = pytesseract.image_to_string(img)
    print("Extracted Text:", text)
    return text

if __name__ == "__main__":
    with app.run():
        result = ocr_image()
        print(result)