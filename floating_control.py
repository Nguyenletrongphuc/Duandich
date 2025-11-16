import tkinter as tk
from tkinter import font
import threading

class FloatingControlPanel:
    def __init__(self, on_capture_callback, on_exit_callback):
        """
        Tạo panel nổi với hai nút Chụp và Thoát
        :param on_capture_callback: hàm callback khi click nút Chụp
        :param on_exit_callback: hàm callback khi click nút Thoát
        """
        self.on_capture = on_capture_callback
        self.on_exit = on_exit_callback
        self.is_capturing = False
        
        # Tạo cửa sổ chính
        self.root = tk.Tk()
        self.root.title("Translation Tool")
        self.root.attributes('-topmost', True)  # Luôn ở trên cùng
        self.root.attributes('-alpha', 0.9)     # Độ trong suốt
        self.root.configure(bg='#2c3e50')
        
        # Loại bỏ viền cửa sổ
        self.root.overrideredirect(True)
        
        # Tạo frame chính
        main_frame = tk.Frame(self.root, bg='#2c3e50', padx=10, pady=10)
        main_frame.pack()
        
        # Tạo tiêu đề
        title_label = tk.Label(
            main_frame,
            text="Công cụ Dịch Thuật",
            bg='#2c3e50',
            fg='white',
            font=('Arial', 10, 'bold')
        )
        title_label.pack(pady=(0, 10))
        
        # Tạo frame cho các nút
        button_frame = tk.Frame(main_frame, bg='#2c3e50')
        button_frame.pack()
        
        # Nút Chụp
        self.btn_capture = tk.Button(
            button_frame,
            text="📸 Chụp",
            bg='#3498db',
            fg='white',
            font=('Arial', 11, 'bold'),
            padx=20,
            pady=12,
            relief='raised',
            bd=2,
            cursor='hand2',
            command=self.on_capture_clicked,
            activebackground='#2980b9'
        )
        self.btn_capture.pack(pady=5)
        
        # Nút Thoát
        self.btn_exit = tk.Button(
            button_frame,
            text="✕ Thoát",
            bg='#e74c3c',
            fg='white',
            font=('Arial', 11, 'bold'),
            padx=20,
            pady=12,
            relief='raised',
            bd=2,
            cursor='hand2',
            command=self.on_exit_clicked,
            activebackground='#c0392b'
        )
        self.btn_exit.pack(pady=5)
        
        # Đặt vị trí cửa sổ ở bên phải giữa màn hình
        self.set_window_position()
        
        # Cho phép kéo cửa sổ
        self.setup_dragging()
    
    def set_window_position(self):
        """
        Đặt vị trí cửa sổ ở bên phải giữa màn hình
        """
        self.root.update_idletasks()
        
        # Lấy kích thước màn hình
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Lấy kích thước cửa sổ
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        
        # Tính toán vị trí (bên phải giữa màn hình)
        x = screen_width - window_width - 20  # 20 pixel từ cạnh phải
        y = (screen_height - window_height) // 2  # Giữa chiều cao
        
        # Đặt vị trí cửa sổ
        self.root.geometry(f"+{x}+{y}")
    
    def setup_dragging(self):
        """
        Cho phép kéo cửa sổ
        """
        self.root.bind('<Button-1>', self.start_drag)
        self.root.bind('<B1-Motion>', self.drag_window)
        
        self.drag_data = {'x': 0, 'y': 0}
    
    def start_drag(self, event):
        """
        Bắt đầu kéo cửa sổ
        """
        self.drag_data['x'] = event.x_root - self.root.winfo_x()
        self.drag_data['y'] = event.y_root - self.root.winfo_y()
    
    def drag_window(self, event):
        """
        Kéo cửa sổ
        """
        x = event.x_root - self.drag_data['x']
        y = event.y_root - self.drag_data['y']
        self.root.geometry(f"+{x}+{y}")
    
    def on_capture_clicked(self):
        """
        Xử lý khi click nút Chụp
        """
        if self.is_capturing:
            return
        
        self.is_capturing = True
        self.btn_capture.config(state='disabled', text="⏳ Đang chụp...")
        self.btn_exit.config(state='disabled')
        
        # Chạy hàm callback trong thread riêng để không block UI
        def run_capture():
            try:
                self.on_capture()
            finally:
                self.is_capturing = False
                self.btn_capture.config(state='normal', text="📸 Chụp")
                self.btn_exit.config(state='normal')
        
        thread = threading.Thread(target=run_capture, daemon=True)
        thread.start()
    
    def on_exit_clicked(self):
        """
        Xử lý khi click nút Thoát
        """
        self.on_exit()
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """
        Chạy vòng lặp chính của Tkinter
        """
        self.root.mainloop()
    
    def close(self):
        """
        Đóng cửa sổ
        """
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass
