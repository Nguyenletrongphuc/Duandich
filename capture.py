# capture.py
import time
import mss
import mss.tools
from PIL import Image

def capture_screen(region=None):
    """
    Chụp ảnh màn hình.
    :param region: dict (left, top, width, height) hoặc None (toàn màn hình)
    :return: PIL.Image
    """
    with mss.mss() as sct:
        screenshot = sct.grab(region if region else sct.monitors[1])
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        return img

# Demo chạy riêng
if __name__ == "__main__":
    print("Chờ 2 giây trước khi chụp màn hình...")
    time.sleep(2)
    img = capture_screen()
    img.show()  # Hiển thị ảnh chụp
