import os
import pytesseract
from PIL import Image
from typing import List, Tuple
import mss
from capture import get_screen_scaling_factor

# Đường dẫn tới tesseract.exe và tessdata
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'

def capture_screen() -> Tuple[Image.Image, float]:
    """
    Chụp màn hình và trả về ảnh cùng với tỉ lệ scale của màn hình
    """
    with mss.mss() as sct:
        screenshot = sct.grab(sct.monitors[0])
        img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
        scale_factor = get_screen_scaling_factor()
        return img, scale_factor

def is_browser_ui_text(text: str, y: int, height: int) -> bool:
    """
    Kiểm tra xem text có phải là phần UI của trình duyệt không
    """
    # Danh sách các từ khóa thường xuất hiện trong UI trình duyệt
    browser_keywords = {
        'new tab', 'tab', 'search', 'http', 'https', 'www', '.com', '.net', '.org',
        'reload', 'refresh', 'home', 'settings', 'menu', 'bookmark', 'history',
        'downloads', 'extensions', 'chrome', 'firefox', 'edge', 'browser', 'file',
        'edit', 'view', 'window', 'help', 'tools', 'favorites', '⋮', '☰', '×', '+',
    }
    
    # Kiểm tra xem text có chứa từ khóa của UI trình duyệt không
    text_lower = text.lower()
    if any(keyword in text_lower for keyword in browser_keywords):
        return True
    
    # Kiểm tra vị trí y (thường UI trình duyệt nằm ở phần trên)
    if y < height * 0.1:  # 10% đầu màn hình
        return True
        
    return False

def is_valid_text(text: str, conf: float, area: int, y: int, height: int) -> bool:
    """
    Kiểm tra xem text có hợp lệ không dựa trên các tiêu chí
    """
    if conf < 35:  # Lọc bỏ những nhận dạng có độ tin cậy thấp
        return False
        
    # Nếu text quá ngắn và chỉ chứa ký tự đặc biệt, có thể là icon
    if len(text) <= 2:
        # Kiểm tra xem có chứa ít nhất một chữ cái hoặc số không
        has_alphanumeric = any(c.isalnum() for c in text)
        if not has_alphanumeric:
            return False
            
    # Lọc bỏ chuỗi chỉ chứa ký tự đặc biệt
    special_chars = set('!@#$%^&*()_+-=[]{}|\\;:\'",.<>?/~`')
    if all(c in special_chars for c in text):
        return False
        
    # Lọc bỏ chuỗi chỉ chứa khoảng trắng
    if text.isspace():
        return False
        
    # Lọc bỏ vùng quá nhỏ (có thể là icon)
    if area < 100:  # Điều chỉnh ngưỡng này tùy theo kích thước icon trên màn hình
        return False
        
    # Kiểm tra xem có phải UI của trình duyệt không
    if is_browser_ui_text(text, y, height):
        return False
    
    # Lọc bỏ text quá dài nếu confidence thấp (có thể là noise)
    if len(text) > 200 and conf < 50:
        return False
        
    return True

def extract_text_from_image(img: Image.Image, scale_factor: float = 1.0) -> List[Tuple[int, int, str]]:
    # Đảm bảo scale_factor hợp lệ
    if not scale_factor or scale_factor <= 0:
        print(f"Warning: Tỉ lệ màn hình không hợp lệ ({scale_factor}), sử dụng giá trị mặc định 1.0")
        scale_factor = 1.0
    
    # Lấy kích thước ảnh
    img_width, img_height = img.size
    
    # Tối ưu hóa ảnh trước khi OCR
    from PIL import ImageEnhance
    # Tăng độ tương phản
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.2)
    
    # Sử dụng OCR đa ngôn ngữ (ví dụ: Nhật + Anh) với cấu hình tốt hơn
    ocr_config = r'--oem 3 --psm 6'  # OEM 3: sử dụng cả legacy và neural, PSM 6: giả định khối text
    ocr_data = pytesseract.image_to_data(img, lang='jpn+eng', config=ocr_config, output_type=pytesseract.Output.DICT)
    
    # Điều chỉnh tọa độ theo tỉ lệ màn hình
    def adjust_coordinates(x: int, y: int) -> Tuple[int, int]:
        return (int(x / scale_factor), int(y / scale_factor))

    # Nhóm text theo đoạn và dòng dựa trên tọa độ y
    paragraphs = []
    current_para = []
    last_y = None
    y_tolerance = 5  # Độ dung sai cho cùng một dòng
    line_spacing_threshold = 20  # Ngưỡng khoảng cách giữa các dòng để xác định đoạn mới

    # Sắp xếp các box theo y trước
    boxes = []
    for i in range(len(ocr_data['level'])):
        text = ocr_data['text'][i].strip()
        if text:
            x = ocr_data['left'][i]
            y = ocr_data['top'][i]
            width = ocr_data['width'][i]
            height = ocr_data['height'][i]
            conf = float(ocr_data['conf'][i])
            area = width * height
            
            # Điều chỉnh tọa độ và kích thước theo tỉ lệ màn hình
            scaled_x, scaled_y = adjust_coordinates(x, y)
            scaled_width = int(width / scale_factor)
            scaled_height = int(height / scale_factor)
            scaled_area = scaled_width * scaled_height
            
            # Chỉ thêm text hợp lệ
            if is_valid_text(text, conf, scaled_area, y, img_height):
                boxes.append({
                    'x': scaled_x,
                    'y': scaled_y,
                    'width': scaled_width,
                    'text': text
                })
    boxes.sort(key=lambda b: (b['y'], b['x']))

    # Nhóm text thành các dòng và đoạn
    current_line = []
    current_line_y = None
    results = []

    for box in boxes:
        x, y = box['x'], box['y']
        
        # Kiểm tra xem có phải dòng mới không
        if current_line_y is None or abs(y - current_line_y) > y_tolerance:
            # Nếu có nội dung trong dòng hiện tại, lưu lại
            if current_line:
                # Sắp xếp từ theo thứ tự từ trái qua phải
                sorted_words = sorted(current_line, key=lambda w: w['x'])
                line_text = ' '.join(word['text'] for word in sorted_words)
                line_x = sorted_words[0]['x']
                
                # Loại bỏ các dòng không có ý nghĩa (quá ngắn sau khi ghép)
                if len(line_text.strip()) > 1:
                    results.append((line_x, current_line_y, line_text))
            
            # Bắt đầu dòng mới
            current_line = [box]
            current_line_y = y
        else:
            # Thêm từ vào dòng hiện tại
            current_line.append(box)

    # Xử lý dòng cuối cùng
    if current_line:
        sorted_words = sorted(current_line, key=lambda w: w['x'])
        line_text = ' '.join(word['text'] for word in sorted_words)
        line_x = sorted_words[0]['x']
        
        if len(line_text.strip()) > 1:
            results.append((line_x, current_line_y, line_text))

    return results

# Dùng để test riêng file này
if __name__ == "__main__":
    print(" Đang chụp màn hình và nhận dạng...")
    img, scale_factor = capture_screen()
    results = extract_text_from_image(img, scale_factor)
    if not results:
        print(" Không phát hiện văn bản.")
    else:
        for i, (x, y, text) in enumerate(results):
            print(f"{i+1}. ({x}, {y}): {text}")
