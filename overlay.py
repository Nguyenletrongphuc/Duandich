import tkinter as tk

class OverlayWindow:
    def __init__(self, items):
        """
        items: danh sách các đoạn dịch, mỗi phần tử là (x, y, translated_text)
        """
        self.root = tk.Tk()
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.75)          # Độ trong suốt (0.0 - 1.0)
        self.root.overrideredirect(True)              # Ẩn viền cửa sổ
        self.root.configure(bg='white')

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")

        # Tạo các nhãn (Label) tại vị trí đã cho
        for x, y, text in items:
            label = tk.Label(
                self.root,
                text=text,
                bg='white',
                fg='black',
                font=('Segoe UI', 12),
                bd=1,
                relief='solid',
                padx=6,
                pady=3,
                wraplength=400,
                justify='left'
            )
            label.place(x=x, y=y)

        # Nút đóng overlay
        btn_close = tk.Button(
            self.root,
            text="×",
            font=('Arial', 14, 'bold'),
            bg='lightgray',
            fg='black',
            relief='raised',
            command=self.root.destroy
        )
        btn_close.place(relx=0.985, rely=0.015, anchor='ne')

    def run(self):
        self.root.mainloop()

def show_overlay(items):
    """
    items: list of (x, y, text) tuples
    """
    win = OverlayWindow(items)
    win.run()
