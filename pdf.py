try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
from pdf2image import convert_from_path


def ocr(filepath):
    images = convert_from_path(filepath, dpi=200)

    for image in images:
        with open(filepath.replace('pdf', 'txt'), "a") as file_object:
            file_object.write(pytesseract.image_to_string(image, lang='rus', config='--oem 3 --psm 6'))
