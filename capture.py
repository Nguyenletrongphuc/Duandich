# capture.py
import time
import mss
import mss.tools
from PIL import Image
import ctypes

def get_screen_scaling_factor():
    """
    Lấy tỉ lệ scale của màn hình Windows
    """
    try:
        user32 = ctypes.windll.user32
        try:
            # Thử set DPI awareness
            success = ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
        except Exception:
            # Fallback cho Windows 8.1 và cũ hơn
            success = user32.SetProcessDPIAware()
            
        # Lấy DPI của màn hình chính
        try:
            # Windows 10 và mới hơn
            dpi = ctypes.windll.shcore.GetScaleFactorForDevice(0)
            if dpi:
                return dpi / 100.0
        except Exception:
            pass
            
        try:
            # Cách khác cho Windows cũ hơn
            dpi = user32.GetDpiForSystem()
            if dpi:
                return dpi / 96.0
        except Exception:
            pass
            
        # Nếu các cách trên thất bại, thử lấy DPI từ DC
        screen = user32.GetDC(0)
        dpi = ctypes.windll.gdi32.GetDeviceCaps(screen, 88)  # LOGPIXELSX
        user32.ReleaseDC(0, screen)
        if dpi:
            return dpi / 96.0
            
    except Exception as e:
        print(f"Warning: Không thể lấy tỉ lệ màn hình chính xác: {str(e)}")
    
    # Giá trị mặc định an toàn nếu không lấy được DPI
    return 1.0

def capture_screen(region=None):
    """
    Chụp ảnh màn hình và trả về thông tin tỉ lệ.
    :param region: dict (left, top, width, height) hoặc None (toàn màn hình)
    :return: tuple (PIL.Image, scale_factor)
    """
    with mss.mss() as sct:
        monitor = region if region else sct.monitors[1]
        screenshot = sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        
        # Lấy tỉ lệ scale của màn hình
        scale_factor = get_screen_scaling_factor()
        
        return img, scale_factor

# Demo chạy riêng
if __name__ == "__main__":
    print("Chờ 2 giây trước khi chụp màn hình...")
    time.sleep(2)
    img = capture_screen()
    img.show()  # Hiển thị ảnh chụp
