from googletrans import Translator
import time

# Tạo một đối tượng Translator dùng chung cho toàn bộ chương trình
translator = Translator()

def translate_texts(texts, src='ja', dest='vi'):
    """
    Dịch một danh sách các đoạn văn bản với xử lý tốt hơn.
    :param texts: list of str - danh sách văn bản cần dịch
    :param src: str - ngôn ngữ nguồn (mặc định: 'ja')
    :param dest: str - ngôn ngữ đích (mặc định: 'vi')
    :return: list of str - danh sách văn bản đã dịch
    """
    try:
        translated_texts = []
        
        for i, text in enumerate(texts):
            if not text or text.isspace():
                # Nếu text rỗng, giữ nguyên
                translated_texts.append(text)
                continue
            
            try:
                # Dịch từng đoạn riêng biệt
                # API googletrans chuẩn: translate(text, src, dest)
                result = translator.translate(text, src_lang=src, dest_lang=dest)
                
                # Xử lý kết quả
                if hasattr(result, 'text'):
                    translated_text = result.text
                elif isinstance(result, dict):
                    translated_text = result.get('text', text)
                else:
                    translated_text = str(result)
                
                translated_texts.append(translated_text)
                
                # Thêm delay nhỏ để tránh bị rate limit
                if i < len(texts) - 1:
                    time.sleep(0.05)
                    
            except TypeError:
                # Nếu API không nhận src_lang/dest_lang, thử cách khác (dùng src/dest)
                try:
                    result = translator.translate(text, src=src, dest=dest)
                    translated_text = result.text if hasattr(result, 'text') else str(result)
                    translated_texts.append(translated_text)
                    if i < len(texts) - 1:
                        time.sleep(0.05)
                except Exception as e:
                    print(f"Lỗi khi dịch đoạn {i+1}: {str(e)}")
                    translated_texts.append(text)
                    
            except Exception as e:
                print(f"Lỗi khi dịch đoạn {i+1}: {str(e)}")
                # Nếu dịch lỗi, giữ nguyên text gốc
                translated_texts.append(text)
        
        return translated_texts
        
    except Exception as e:
        print(f"Lỗi chung khi dịch: {e}")
        return texts  # Trả về text gốc nếu có lỗi
