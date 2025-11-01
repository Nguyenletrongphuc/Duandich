from capture import capture_screen
from ocr import extract_text_from_image
from translate import translate_texts
from overlay import show_overlay

def main():
    print("⏳ Đang chụp màn hình...")
    img, scale_factor = capture_screen()

    print("🔍 Đang nhận dạng ký tự (OCR)...")
    text_blocks = extract_text_from_image(img, scale_factor)

    if not text_blocks:
        print("❌ Không nhận được văn bản nào.")
        return

    print("🈶 Văn bản nhận được:")
    for i, (x, y, text) in enumerate(text_blocks):
        print(f"  {i+1}. ({x}, {y}): {text}")

    print("🌐 Đang dịch...")
    texts = [text for x, y, text in text_blocks]
    translated_texts = translate_texts(texts)
    translated_blocks = [
        (x, y, t) for (x, y, _), t in zip(text_blocks, translated_texts)
    ]

    print("✅ Kết quả dịch:")
    for i, (x, y, text) in enumerate(translated_blocks):
        print(f"  {i+1}. ({x}, {y}): {text}")

    print("💬 Hiển thị kết quả lên màn hình...")
    show_overlay(translated_blocks)

if __name__ == '__main__':
    main()
