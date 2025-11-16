from capture import capture_screen
from ocr import extract_text_from_image
from translate import translate_texts
from overlay import show_overlay
from floating_control import FloatingControlPanel

def perform_translation():
    """
    Thực hiện quá trình chụp, OCR và dịch thuật
    """
    print("\n" + "="*50)
    print("⏳ Đang chụp màn hình...")
    img, scale_factor = capture_screen()

    print(" Đang nhận dạng ký tự (OCR)...")
    text_blocks = extract_text_from_image(img, scale_factor)

    if not text_blocks:
        print(" Không nhận được văn bản nào.")
        return

    print(f" Phát hiện {len(text_blocks)} đoạn văn bản:")
    for i, (x, y, text) in enumerate(text_blocks):
        print(f"  {i+1}. ({x}, {y}): {text[:50]}{'...' if len(text) > 50 else ''}")

    print(" Đang dịch...")
    texts = [text for x, y, text in text_blocks]
    translated_texts = translate_texts(texts)
    translated_blocks = [
        (x, y, t) for (x, y, _), t in zip(text_blocks, translated_texts)
    ]

    print(" Kết quả dịch:")
    for i, (x, y, text) in enumerate(translated_blocks):
        print(f"  {i+1}. ({x}, {y}): {text[:50]}{'...' if len(text) > 50 else ''}")

    print(" Hiển thị kết quả lên màn hình...")
    show_overlay(translated_blocks)
    print("="*50)

def on_exit():
    """
    Hàm callback khi thoát chương trình
    """
    print("\n Đang thoát chương trình...")

def main():
    print(" Công cụ Dịch Thuật - Khởi động...")
    print(" Ghi chú: Nhấn nút 'Chụp' để bắt đầu dịch, 'Thoát' để kết thúc")
    
    # Tạo panel điều khiển nổi
    control_panel = FloatingControlPanel(perform_translation, on_exit)
    
    # Chạy vòng lặp chính
    control_panel.run()

if __name__ == '__main__':
    main()
