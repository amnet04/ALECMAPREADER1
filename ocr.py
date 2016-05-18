from tesserwrap import Tesseract
from PIL import Image
import re

def ocr(img,idioma):
    ocr_img = Image.fromarray(img)
    ocr = Tesseract(lang=idioma)
    ocr.set_image(ocr_img)
    pattern = re.compile('[a-zA-Z0-9]')
    text = ocr.get_utf8_text()
    text = text.splitlines()
    text = [x for x in text if x != '']
    text = [x for x in text if pattern.search(x)]
    ocr.clear()
    return (text)
