# utils.py
import socket
import re
import time


# --------------------------------------------------------------
# Kiểm tra mạng bằng cách thử kết nối DNS của Google (8.8.8.8)
# --------------------------------------------------------------
def has_internet(timeout=0.6) -> bool:
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        return True
    except:
        return False


# --------------------------------------------------------------
# Clean text (OCR thường cho ra ký tự thừa)
# --------------------------------------------------------------
def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\n", " ").strip()
    text = re.sub(r"\s+", " ", text)
    return text


# --------------------------------------------------------------
# Tách câu tiếng Anh/Japan để đưa vào dịch cho chính xác
# --------------------------------------------------------------
def split_sentences(text: str):
    if not text:
        return []

    # Tách theo . ! ? hoặc break xuống dòng
    parts = re.split(r'(?<=[.!?])\s+|\n+', text)
    return [p.strip() for p in parts if p.strip()]


# --------------------------------------------------------------
# Nhận diện ngôn ngữ EN / JA dựa trên ký tự
# --------------------------------------------------------------
def detect_language(text: str) -> str:
    if not text:
        return "en"

    # Đếm số ký tự tiếng Nhật
    japanese_chars = re.findall(r'[\u3040-\u30FF\u4E00-\u9FFF]', text)
    if len(japanese_chars) >= 2:
        return "ja"

    # Đếm số ký tự Latin
    latin_chars = re.findall(r'[A-Za-z]', text)
    if len(latin_chars) >= 2:
        return "en"

    # fallback
    return "en"


# --------------------------------------------------------------
# Hàm log nhẹ (tùy chọn)
# --------------------------------------------------------------
def log(msg: str):
    t = time.strftime("%H:%M:%S")
    print(f"[{t}] {msg}")
