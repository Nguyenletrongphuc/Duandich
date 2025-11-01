# Real-Time On-Screen Translator for Desktop (Python)

## 📌 Mục tiêu dự án

Phát triển một phần mềm chạy trên máy tính (Windows) có chức năng tương tự Google Ống Kính (Google Lens - Live Translate), cho phép:

- Quét văn bản hiển thị trên **màn hình máy tính (không dùng camera)**, ví dụ như nội dung trong game, video hoặc phần mềm khác.
- Nhận diện văn bản (OCR), ví dụ: tiếng Nhật.
- Dịch sang ngôn ngữ đích (ví dụ: tiếng Việt hoặc tiếng Anh).
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
| `main.py` | Giao tiếp giữa các module, điều khiển vòng lặp chính |

---

## 🛠️ Công nghệ & thư viện

- `pytesseract`: wrapper cho Tesseract OCR
- `mss` hoặc `PIL.ImageGrab`: chụp màn hình
- `googletrans`: sử dụng Google Translate không chính thức
- `tkinter`: hiển thị overlay đơn giản (hoặc `pyqt5`, `pystray` nếu cần nâng cao)

Cần cài đặt phần mềm OCR:

- **Tesseract OCR**: https://github.com/UB-Mannheim/tesseract/wiki

---

## ✅ Chức năng cần hỗ trợ

- Chụp ảnh màn hình định kỳ (hoặc theo phím nóng)
- OCR nhận diện chữ từ ảnh
- Dịch văn bản từ tiếng Nhật sang tiếng Việt
- Hiển thị bản dịch bằng overlay (giao diện trong suốt)
- Tùy chọn bật/tắt app bằng phím tắt
- Cho phép chọn vùng màn hình để quét (tùy chọn nâng cao)

---

## 🔁 Gợi ý phát triển (cho Copilot)

- Mỗi module nên được đóng gói thành class hoặc hàm riêng
- Tránh hardcode ngôn ngữ – nên khai báo biến `src_lang = "ja"` và `dst_lang = "vi"`
- Có thể viết decorator để log thời gian xử lý từng bước
- Nên hỗ trợ chạy bằng `python main.py` và xử lý ngoại lệ rõ ràng
