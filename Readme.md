# Real-Time On-Screen Translator for Desktop (Python)
Phát triển một phần mềm chạy trên máy tính (Windows) có chức năng tương tự Google Ống Kính (Google Lens - Live Translate), cho phép:

- Quét văn bản hiển thị trên **màn hình máy tính (không dùng camera)**, ví dụ như nội dung trong game, web, video hoặc phần mềm khác.
- Nhận diện văn bản (OCR), ví dụ: tiếng Nhật, Anh.
- Dịch sang ngôn ngữ đích (ví dụ: tiếng Việt).
- Hiển thị bản dịch **ngay trên màn hình**, đè lên vị trí gốc bằng overlay.

Ứng dụng chạy nền, cho phép người dùng bật/tắt bằng phím nóng, và tự động cập nhật bản dịch theo thời gian thực.

---

## 🧱 Kiến trúc hệ thống

Luồng hoạt động:

[Screen Capture] → [OCR] → [Translate] → [Overlay Translated Text]

### Các thành phần chính:

| Module | Mô tả |
|--------|------|
| `capture.py` | Chụp ảnh màn hình hoặc một vùng cụ thể |
| `ocr.py` | Xử lý nhận dạng chữ bằng Tesseract OCR |
| `translate.py` | Gửi yêu cầu dịch văn bản |
| `overlay.py` | Tạo lớp phủ hiển thị bản dịch trên màn hình |
| `offline_translator.py` | Mô hình dịch thuật offline |
| `utils.py` | Chứa các import cần thiết  |
| `floating_control.py` | Các nút điều khiển chính |
---

## 🛠️ Công nghệ & thư viện

- `pytesseract`: wrapper cho Tesseract OCR
- `mss` hoặc `PIL.ImageGrab`: chụp màn hình
- `googletrans`: sử dụng Google Translate không chính thức
- `tkinter`: hiển thị overlay đơn giản (hoặc `pyqt5`, `pystray` nếu cần nâng cao)

Cần cài đặt phần mềm OCR:

- **Tesseract OCR**: https://github.com/UB-Mannheim/tesseract/wiki

---

##  Chức năng cần hỗ trợ

- Chụp ảnh màn hình định kỳ (hoặc theo phím nóng)
- OCR nhận diện chữ từ ảnh
- Dịch văn bản từ tiếng Nhật sang tiếng Việt
- Hiển thị bản dịch bằng overlay (giao diện trong suốt)
- Tùy chọn bật/tắt app bằng phím tắt
- Cho phép chọn vùng màn hình để quét (tùy chọn nâng cao)

---

## Các lưu ý
- Phải tải riêng thư mục Tesseract và đặt theo đường dẫn cố định như sau: C:\Program Files\
- Chức năng dịch offline chỉ hoạt động khi đã tải trước lúc có mạng và mô hình lưu trong thư mục temp
- lệnh khởi động py -3.10 main.py