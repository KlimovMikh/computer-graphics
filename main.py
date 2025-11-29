import tkinter as tk
from tkinter import ttk
import time
import math

class RasterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа №3: Растровые алгоритмы")
        self.root.geometry("1100x700")

        self.pixel_size = 20 
        self.canvas_width = 700
        self.canvas_height = 660
        self.center_x = self.canvas_width // (2 * self.pixel_size)
        self.center_y = self.canvas_height // (2 * self.pixel_size)

        
        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)

        control_frame = tk.Frame(root)
        control_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        input_frame = tk.LabelFrame(control_frame, text="Координаты")
        input_frame.pack(fill=tk.X, pady=5)

        tk.Label(input_frame, text="X1 / Xc:").grid(row=0, column=0)
        self.entry_x1 = tk.Entry(input_frame, width=5)
        self.entry_x1.grid(row=0, column=1)
        self.entry_x1.insert(0, "-5")

        tk.Label(input_frame, text="Y1 / Yc:").grid(row=0, column=2)
        self.entry_y1 = tk.Entry(input_frame, width=5)
        self.entry_y1.grid(row=0, column=3)
        self.entry_y1.insert(0, "-5")

        tk.Label(input_frame, text="X2 / R:").grid(row=1, column=0)
        self.entry_x2 = tk.Entry(input_frame, width=5)
        self.entry_x2.grid(row=1, column=1)
        self.entry_x2.insert(0, "10")

        tk.Label(input_frame, text="Y2:").grid(row=1, column=2)
        self.entry_y2 = tk.Entry(input_frame, width=5)
        self.entry_y2.grid(row=1, column=3)
        self.entry_y2.insert(0, "8")
        
        tk.Label(input_frame, text="(Для окружности используйте поле R)").grid(row=2, column=0, columnspan=4)

        btn_frame = tk.LabelFrame(control_frame, text="Алгоритмы")
        btn_frame.pack(fill=tk.X, pady=5)

        tk.Button(btn_frame, text="Пошаговый", command=self.run_step_by_step).pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="ЦДА (DDA)", command=self.run_dda).pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="Брезенхем (Линия)", command=self.run_bresenham_line).pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="Брезенхем (Окружность)", command=self.run_bresenham_circle).pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="Очистить", command=self.clear_canvas).pack(fill=tk.X, pady=10)

        log_frame = tk.LabelFrame(control_frame, text="Лог вычислений и Время")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = tk.Text(log_frame, height=20, width=40, font=("Consolas", 9))
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

        self.draw_grid()


    def draw_grid(self):
        self.canvas.delete("all")
        w, h = self.canvas_width, self.canvas_height
        ps = self.pixel_size

        for x in range(0, w, ps):
            self.canvas.create_line(x, 0, x, h, fill="#e0e0e0")
        for y in range(0, h, ps):
            self.canvas.create_line(0, y, w, y, fill="#e0e0e0")

        cx_screen = self.center_x * ps
        cy_screen = self.center_y * ps
        
        self.canvas.create_line(0, cy_screen, w, cy_screen, fill="black", width=2, arrow=tk.LAST)
        self.canvas.create_text(w-10, cy_screen+15, text="X")
        
        self.canvas.create_line(cx_screen, h, cx_screen, 0, fill="black", width=2, arrow=tk.LAST)
        self.canvas.create_text(cx_screen+15, 10, text="Y")

        for i in range(-20, 21, 5):
            if i == 0: continue
            sx = (self.center_x + i) * ps
            if 0 <= sx <= w:
                self.canvas.create_line(sx, cy_screen-3, sx, cy_screen+3, fill="black")
                self.canvas.create_text(sx, cy_screen+15, text=str(i), font=("Arial", 8))
            
            sy = (self.center_y - i) * ps
            if 0 <= sy <= h:
                self.canvas.create_line(cx_screen-3, sy, cx_screen+3, sy, fill="black")
                self.canvas.create_text(cx_screen-15, sy, text=str(i), font=("Arial", 8))

    def plot_pixel(self, x, y, color="blue"):
        
        screen_x = (self.center_x + x) * self.pixel_size
        screen_y = (self.center_y - y) * self.pixel_size 

        self.canvas.create_rectangle(
            screen_x, screen_y,
            screen_x + self.pixel_size, screen_y - self.pixel_size,
            fill=color, outline="gray"
        )
        # self.canvas.create_oval(screen_x+8, screen_y-8, screen_x+12, screen_y-12, fill="white")

    def clear_canvas(self):
        self.draw_grid()
        self.log_text.delete(1.0, tk.END)

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def get_coords(self):
        try:
            x1 = int(self.entry_x1.get())
            y1 = int(self.entry_y1.get())
            x2 = int(self.entry_x2.get())
            try:
                y2 = int(self.entry_y2.get())
            except ValueError:
                y2 = 0
            return x1, y1, x2, y2
        except ValueError:
            self.log("Ошибка: Введите целые числа!")
            return None

    def run_step_by_step(self):
        coords = self.get_coords()
        if not coords: return
        x1, y1, x2, y2 = coords
        
        self.clear_canvas()
        self.log(f"--- Пошаговый алгоритм: ({x1},{y1}) -> ({x2},{y2}) ---")
        
        start_time = time.perf_counter_ns()
        
        if x1 == x2 and y1 == y2:
            self.plot_pixel(x1, y1)
            return

        dx = x2 - x1
        dy = y2 - y1
        
        steps = max(abs(dx), abs(dy))

        self.log(f"dx={dx}, dy={dy}, steps={steps}")
        
        if abs(dx) >= abs(dy):
            k = dy / dx if dx != 0 else 0
            b = y1 - k * x1
            self.log(f"Ось X ведущая. k={k:.2f}, b={b:.2f}")
            
            step = 1 if x2 > x1 else -1
            for x in range(x1, x2 + step, step):
                y = k * x + b
                y_round = round(y)
                self.plot_pixel(x, y_round, "red")
                self.log(f"x={x}, y={y:.2f} -> round({y_round})")
        else: 
            k = dx / dy
            b = x1 - k * y1
            self.log(f"Ось Y ведущая. 1/k={k:.2f}")
            
            step = 1 if y2 > y1 else -1
            for y in range(y1, y2 + step, step):
                x = k * y + b
                x_round = round(x)
                self.plot_pixel(x_round, y, "red")
                self.log(f"y={y}, x={x:.2f} -> round({x_round})")

        end_time = time.perf_counter_ns()
        self.log(f"Время выполнения: {(end_time - start_time) / 1000:.2f} мкс")

    def run_dda(self):
        coords = self.get_coords()
        if not coords: return
        x1, y1, x2, y2 = coords

        self.clear_canvas()
        self.log(f"--- Алгоритм ЦДА: ({x1},{y1}) -> ({x2},{y2}) ---")
        
        start_time = time.perf_counter_ns()

        dx = x2 - x1
        dy = y2 - y1
        
        length = max(abs(dx), abs(dy))
        
        if length == 0:
            self.plot_pixel(x1, y1, "green")
            return

        dx_step = dx / length
        dy_step = dy / length
        
        self.log(f"Length={length}, dx_step={dx_step:.2f}, dy_step={dy_step:.2f}")

        x = x1
        y = y1
        
        for i in range(length + 1):
            self.plot_pixel(round(x), round(y), "green")
            if i < 3 or i > length - 3:
                self.log(f"i={i}: x={x:.2f}, y={y:.2f} -> ({round(x)}, {round(y)})")
            
            x += dx_step
            y += dy_step

        end_time = time.perf_counter_ns()
        self.log(f"Время выполнения: {(end_time - start_time) / 1000:.2f} мкс")

    def run_bresenham_line(self):
        coords = self.get_coords()
        if not coords: return
        x1, y1, x2, y2 = coords

        self.clear_canvas()
        self.log(f"--- Брезенхем (Линия): ({x1},{y1}) -> ({x2},{y2}) ---")
        
        start_time = time.perf_counter_ns()

        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        
        err = dx - dy
        
        x, y = x1, y1
        
        self.log(f"Init: dx={dx}, dy={dy}, sx={sx}, sy={sy}, err={err}")

        while True:
            self.plot_pixel(x, y, "blue")
            if x == x2 and y == y2:
                break
            
            e2 = 2 * err
            prev_err = err 
            
            if e2 > -dy:
                err -= dy
                x += sx
            
            if e2 < dx:
                err += dx
                y += sy
            
            if dx < 20 or (x - x1) % 5 == 0:
                 self.log(f"P({x},{y}), err_was={prev_err}, new_err={err}")

        end_time = time.perf_counter_ns()
        self.log(f"Время выполнения: {(end_time - start_time) / 1000:.2f} мкс")

    def run_bresenham_circle(self):
        try:
            xc = int(self.entry_x1.get())
            yc = int(self.entry_y1.get())
            r = int(self.entry_x2.get())
        except ValueError:
            self.log("Ошибка: Для окружности нужны Xc, Yc и R (в поле X2)")
            return

        self.clear_canvas()
        self.log(f"--- Брезенхем (Окружность): Центр({xc},{yc}), R={r} ---")
        
        start_time = time.perf_counter_ns()

        x = 0
        y = r
        d = 3 - 2 * r
        
        self.log(f"Init: x={x}, y={y}, d={d}")

        def plot_circle_points(xc, yc, x, y):
            points = [
                (xc+x, yc+y), (xc-x, yc+y), (xc+x, yc-y), (xc-x, yc-y),
                (xc+y, yc+x), (xc-y, yc+x), (xc+y, yc-x), (xc-y, yc-x)
            ]
            for px, py in points:
                self.plot_pixel(px, py, "purple")

        plot_circle_points(xc, yc, x, y)

        while y >= x:
            x += 1
            if d > 0:
                y -= 1
                d = d + 4 * (x - y) + 10
            else:
                d = d + 4 * x + 6
            
            plot_circle_points(xc, yc, x, y)
            self.log(f"Step: x={x}, y={y}, d={d}")

        end_time = time.perf_counter_ns()
        self.log(f"Время выполнения: {(end_time - start_time) / 1000:.2f} мкс")

if __name__ == "__main__":
    root = tk.Tk()
    app = RasterApp(root)
    root.mainloop()