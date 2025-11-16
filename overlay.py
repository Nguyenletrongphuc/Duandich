import tkinter as tk

class OverlayWindow:
    def __init__(self, items):
        """
        items: danh sách các đoạn dịch, mỗi phần tử là (x, y, translated_text)
        """
        self.root = tk.Tk()
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.8)           # Độ trong suốt (0.0 - 1.0)
        self.root.overrideredirect(True)              # Ẩn viền cửa sổ
        self.root.configure(bg='#f0f0f0')             # Màu nền nhạt hơn

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")

        # Font để tính toán kích thước
        font = ('Segoe UI', 11)
        font_bold = ('Segoe UI', 11, 'bold')

        # Thông tin màn hình và khoảng cách an toàn
        margin_right = 10
        margin_left = 8
        margin_top = 10
        margin_bottom = 10

        # Tạo label tạm để đo kích thước trước khi đặt
        temp_label = tk.Label(self.root, font=font)

        # Nhóm các item theo đoạn văn dựa trên khoảng cách y
        paragraph_groups = []
        current_group = []
        last_y = None

        # Sắp xếp items theo y để xử lý theo thứ tự từ trên xuống
        sorted_items = sorted(items, key=lambda item: item[1])

        for x, y, text in sorted_items:
            # Điều chỉnh threshold để nhóm tốt hơn
            if last_y is not None and abs(y - last_y) > 40:  # Ngưỡng cho đoạn mới
                if current_group:
                    paragraph_groups.append(current_group)
                current_group = []
            current_group.append((x, y, text))
            last_y = y

        if current_group:
            paragraph_groups.append(current_group)

        # Xử lý từng đoạn văn
        global_current_y = margin_top
        for paragraph in paragraph_groups:
            # Xác định vị trí bắt đầu đoạn
            min_x = min(item[0] for item in paragraph)
            paragraph_start_y = max(global_current_y, min(item[1] for item in paragraph))

            # Column layout state for this paragraph
            column_x = min_x
            column_width = 0
            current_y = paragraph_start_y
            max_col_height = 0

            for idx, (x, y, text) in enumerate(paragraph):
                # Tính wraplength tối đa dựa trên không gian còn lại của màn hình
                available_width = screen_width - column_x - margin_right
                if available_width < 150:
                    # Nếu không đủ chỗ bên phải, reset column
                    column_x = margin_left
                    available_width = screen_width - column_x - margin_right

                # Tính wraplength động dựa trên độ dài text
                text_length = len(text)
                if text_length < 30:
                    wraplength = min(int(available_width * 0.8), 600)
                elif text_length < 100:
                    wraplength = min(int(available_width * 0.9), 800)
                else:
                    wraplength = min(int(available_width * 0.95), 1000)

                # Tạo label tạm để đo yêu cầu kích thước
                temp_label.config(text=text, wraplength=wraplength, justify='left')
                temp_label.update_idletasks()
                req_h = temp_label.winfo_reqheight()
                req_w = temp_label.winfo_reqwidth()

                # Nếu chồng xuống dưới màn hình, bắt đầu cột mới
                if current_y + req_h + margin_bottom > screen_height and idx > 0:
                    # Start new column to the right
                    next_column_x = column_x + max(column_width, req_w) + 20
                    if next_column_x + 150 > screen_width - margin_right:
                        # Không còn chỗ ngang, reset
                        current_y = margin_top
                        column_x = margin_left
                    else:
                        column_x = next_column_x
                        current_y = paragraph_start_y
                    column_width = 0
                    
                    # Recompute wraplength for new column
                    available_width = screen_width - column_x - margin_right
                    if text_length < 30:
                        wraplength = min(int(available_width * 0.8), 600)
                    elif text_length < 100:
                        wraplength = min(int(available_width * 0.9), 800)
                    else:
                        wraplength = min(int(available_width * 0.95), 1000)

                # Tạo label chính với styling
                label = tk.Label(
                    self.root,
                    text=text,
                    bg='#f0f0f0',
                    fg='#1a1a1a',
                    font=font,
                    bd=1,
                    relief='solid',
                    padx=8,
                    pady=5,
                    wraplength=wraplength,
                    justify='left',
                    anchor='nw',  # Anchor top-left
                    highlightthickness=0
                )
                # Đặt label
                label.place(x=column_x, y=current_y)
                label.update_idletasks()

                real_w = label.winfo_width()
                real_h = label.winfo_height()

                # Nếu label vẫn vượt phải màn hình, nén wraplength
                if column_x + real_w + margin_right > screen_width:
                    new_wrap = max(100, wraplength - (column_x + real_w + margin_right - screen_width))
                    label.config(wraplength=new_wrap)
                    label.update_idletasks()
                    real_w = label.winfo_width()
                    real_h = label.winfo_height()

                # Cập nhật chiều rộng cột
                column_width = max(column_width, real_w)

                # Cập nhật y cho dòng tiếp theo
                current_y += real_h + 5
                max_col_height = max(max_col_height, real_h)

            # Cập nhật global_current_y cho đoạn tiếp theo
            global_current_y = max(global_current_y, current_y + 15)

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
