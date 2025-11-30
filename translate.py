# translate.py
from googletrans import Translator
from utils import has_internet, detect_language, clean_text

translator = Translator()

def translate_texts(texts, src=None, dest='vi'):
    """
    Dịch danh sách văn bản:
    - Có mạng → Google Translate
    - Không mạng → MarianMT offline
    - Tự động nhận diện EN / JA nếu src=None
    """

    cleaned_texts = [clean_text(t) for t in texts]
    if not any(cleaned_texts):
        return cleaned_texts

    # Nếu không truyền ngôn ngữ nguồn → tự nhận diện cho từng câu
    if src is None:
        src_list = [detect_language(t) for t in cleaned_texts]
    else:
        src_list = [src] * len(cleaned_texts)

    # Kiểm tra internet để quyết định mode dịch
    online = has_internet()

    results = []

    for i, (text, lang) in enumerate(zip(cleaned_texts, src_list)):
        if not text:
            results.append("")
            continue

        if online:
            try:
                # googletrans bản chuẩn
                res = translator.translate(text, src=lang, dest=dest)
                results.append(res.text)
                continue
            except Exception:
                # Nếu Google lỗi → fallback offline
                pass

        # OFFLINE fallback (lazy import: load offline translator only if needed)
        try:
            from offline_translator import translate_offline
        except Exception as e:
            # Nếu không import được mô-đun offline (thiếu pkg), thông báo và giữ nguyên text
            print(f"Warning: Không tải được offline translator: {e}")
            results.append(text)
        else:
            try:
                offline_result = translate_offline(text, lang, dest)
                results.append(offline_result)
            except Exception as e:
                print(f"Warning: Offline translator lỗi: {e}")
                results.append(text)

    return results
