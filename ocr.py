import os
import pytesseract
from PIL import Image
from typing import List, Tuple
import mss

# Đường dẫn tới tesseract.exe và tessdata
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'

def capture_screen() -> Image.Image:
    with mss.mss() as sct:
        screenshot = sct.grab(sct.monitors[0])
        img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
        return img

def extract_text_from_image(img: Image.Image) -> List[Tuple[int, int, str]]:
    # Sử dụng OCR đa ngôn ngữ (ví dụ: Nhật + Anh)
    ocr_data = pytesseract.image_to_data(img, lang='jpn+eng', output_type=pytesseract.Output.DICT)

    results = []
    n_boxes = len(ocr_data['level'])
    for i in range(n_boxes):
        text = ocr_data['text'][i].strip()
        if text:
            x = ocr_data['left'][i]
            y = ocr_data['top'][i]
            results.append((x, y, text))

    return results

# Dùng để test riêng file này
if __name__ == "__main__":
    print("⏳ Đang chụp màn hình và nhận dạng...")
    img = capture_screen()
    results = extract_text_from_image(img)
    if not results:
        print("❌ Không phát hiện văn bản.")
    else:
        for i, (x, y, text) in enumerate(results):
            print(f"{i+1}. ({x}, {y}): {text}")
