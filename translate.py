from googletrans import Translator

# Tạo một đối tượng Translator dùng chung cho toàn bộ chương trình
translator = Translator()

def translate_texts(texts, src='ja', dest='vi'):
    """
    Dịch một danh sách các đoạn văn bản.
    :param texts: list of str
    :return: list of str (đã dịch)
    """
    try:
        # Gộp các đoạn lại, phân tách bằng ký tự đặc biệt (ở đây là '\n')
        joined = "\n".join(texts)
        translated = translator.translate(joined, src=src, dest=dest)
        # Nếu kết quả là một chuỗi, tách lại thành danh sách
        translated_lines = translated.text.split('\n')
        # Đảm bảo số dòng khớp với đầu vào
        if len(translated_lines) < len(texts):
            # Nếu thiếu dòng, bổ sung dòng rỗng
            translated_lines += [""] * (len(texts) - len(translated_lines))
        return translated_lines
    except Exception as e:
        print("Lỗi khi dịch:", e)
        return [""] * len(texts)
