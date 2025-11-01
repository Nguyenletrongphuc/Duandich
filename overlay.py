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

        # Font để tính toán kích thước
        font = ('Segoe UI', 12)

        # Thông tin màn hình và khoảng cách an toàn
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        margin_right = 12
        margin_left = 8
        margin_top = 12
        margin_bottom = 12

        # Tạo label tạm để đo kích thước trước khi đặt
        temp_label = tk.Label(self.root, font=font)

        # Nhóm các item theo đoạn văn dựa trên khoảng cách y
        paragraph_groups = []
        current_group = []
        last_y = None

        # Sắp xếp items theo y để xử lý theo thứ tự từ trên xuống
        sorted_items = sorted(items, key=lambda item: item[1])

        for x, y, text in sorted_items:
            if last_y is not None and abs(y - last_y) > 48:  # Ngưỡng cho đoạn mới
                if current_group:
                    paragraph_groups.append(current_group)
                current_group = []
            current_group.append((x, y, text))
            last_y = y

        if current_group:
            paragraph_groups.append(current_group)

        # Xử lý từng đoạn văn; sử dụng hệ cột khi gặp overflow dọc
        global_current_y = margin_top
        for paragraph in paragraph_groups:
            # Xác định vị trí bắt đầu đoạn (dựa trên min y của các dòng nếu hợp lý)
            min_x = min(item[0] for item in paragraph)
            paragraph_start_y = max(global_current_y, min(item[1] for item in paragraph))

            # Column layout state for this paragraph
            column_x = min_x
            column_width = 0
            current_y = paragraph_start_y

            for x, y, text in paragraph:
                # Tính wraplength tối đa dựa trên không gian còn lại của màn hình
                available_width = screen_width - column_x - margin_right
                if available_width < 120:
                    # Nếu không đủ chỗ bên phải, đặt column mới ở vị trí an toàn
                    column_x = margin_left
                    available_width = screen_width - column_x - margin_right

                wraplength = min(max(300, int(available_width * 0.9)), 1200)

                # Tạo label tạm để đo yêu cầu kích thước
                temp_label.config(text=text, wraplength=wraplength, justify='left')
                temp_label.update_idletasks()
                # Dùng giá trị ước tính từ temp_label
                req_h = temp_label.winfo_reqheight()
                req_w = min(temp_label.winfo_reqwidth(), available_width)

                # Nếu chồng xuống dưới màn hình, bắt đầu cột mới (sang phải)
                if current_y + req_h + margin_bottom > screen_height:
                    # Start new column to the right of current column
                    next_column_x = column_x + max(column_width, req_w) + 24
                    # Nếu next column vượt quá màn hình, fallback: dời lên đầu màn hình
                    if next_column_x + 120 > screen_width - margin_right:
                        # Không còn chỗ ngang, bắt đầu từ top nhưng giữ bên trong màn hình
                        current_y = margin_top
                        column_x = margin_left
                    else:
                        column_x = next_column_x
                        current_y = paragraph_start_y

                    # Recompute available and wraplength for new column
                    available_width = screen_width - column_x - margin_right
                    wraplength = min(max(200, int(available_width * 0.9)), 1200)

                # Tạo label chính
                label = tk.Label(
                    self.root,
                    text=text,
                    bg='white',
                    fg='black',
                    font=font,
                    bd=1,
                    relief='solid',
                    padx=8,
                    pady=4,
                    wraplength=wraplength,
                    justify='left'
                )
                # Đặt tạm label để tính kích thước chính xác
                label.place(x=column_x, y=current_y)
                label.update_idletasks()

                real_w = label.winfo_width()
                real_h = label.winfo_height()

                # Nếu label vẫn vượt phải màn hình, nén wraplength và cập nhật
                if column_x + real_w + margin_right > screen_width:
                    # Giảm wraplength để bắt buộc xuống dòng nhiều hơn
                    new_wrap = max(120, wraplength - (column_x + real_w + margin_right - screen_width))
                    label.config(wraplength=new_wrap)
                    label.update_idletasks()
                    real_w = label.winfo_width()
                    real_h = label.winfo_height()

                # Cập nhật chiều rộng cột
                column_width = max(column_width, real_w)

                # Cập nhật y cho dòng tiếp theo
                current_y += real_h + 6

            # Sau một đoạn, di chuyển global_current_y xuống dưới nếu cột vẫn nằm ở cạnh trái
            global_current_y = max(global_current_y, current_y + 12)

            
            # Cập nhật last_y cho dòng tiếp theo
            last_y = current_y

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
