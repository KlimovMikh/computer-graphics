import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import cv2
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class ImageProcessingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа 2 - Обработка изображений")
        self.root.geometry("1400x900")
        
        self.original_image = None
        self.processed_image = None
        self.current_image_display = None
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        control_frame = ttk.LabelFrame(main_frame, text="Управление", padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), padx=5, pady=5)
        
        ttk.Button(control_frame, text="Загрузить изображение", 
                   command=self.load_image).grid(row=0, column=0, padx=5, pady=5)
        
        ttk.Button(control_frame, text="Сохранить результат", 
                   command=self.save_image).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(control_frame, text="Сбросить", 
                   command=self.reset_image).grid(row=0, column=2, padx=5, pady=5)
        
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        self.setup_nonlinear_filters_tab()
        
        self.setup_histogram_tab()
        
        image_frame = ttk.Frame(main_frame)
        image_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        original_label = ttk.Label(image_frame, text="Оригинальное изображение")
        original_label.grid(row=0, column=0, padx=5)
        
        self.original_canvas = tk.Canvas(image_frame, width=600, height=450, bg='gray')
        self.original_canvas.grid(row=1, column=0, padx=5, pady=5)
        
        processed_label = ttk.Label(image_frame, text="Обработанное изображение")
        processed_label.grid(row=0, column=1, padx=5)
        
        self.processed_canvas = tk.Canvas(image_frame, width=600, height=450, bg='gray')
        self.processed_canvas.grid(row=1, column=1, padx=5, pady=5)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
    def setup_nonlinear_filters_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Нелинейные фильтры")
        
        desc = ttk.Label(tab, text="Фильтры на основе порядковых статистик", 
                        font=('Arial', 10, 'bold'))
        desc.grid(row=0, column=0, columnspan=3, pady=10)
        
        ttk.Label(tab, text="Тип фильтра:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.filter_type = tk.StringVar(value="median")
        
        filter_options = [
            ("Медианный фильтр", "median"),
            ("Минимальный фильтр", "min"),
            ("Максимальный фильтр", "max"),
            ("Средний фильтр (mean)", "mean"),
            ("Фильтр средней точки", "midpoint")
        ]
        
        for i, (text, value) in enumerate(filter_options):
            ttk.Radiobutton(tab, text=text, variable=self.filter_type, 
                           value=value).grid(row=2+i, column=0, padx=20, pady=2, sticky=tk.W)
        
        ttk.Label(tab, text="Размер ядра:").grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        self.kernel_size = tk.IntVar(value=3)
        
        kernel_frame = ttk.Frame(tab)
        kernel_frame.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Radiobutton(kernel_frame, text="3x3", variable=self.kernel_size, 
                       value=3).pack(anchor=tk.W)
        ttk.Radiobutton(kernel_frame, text="5x5", variable=self.kernel_size, 
                       value=5).pack(anchor=tk.W)
        ttk.Radiobutton(kernel_frame, text="7x7", variable=self.kernel_size, 
                       value=7).pack(anchor=tk.W)
        
        custom_frame = ttk.Frame(kernel_frame)
        custom_frame.pack(anchor=tk.W, pady=5)
        ttk.Label(custom_frame, text="Произвольный:").pack(side=tk.LEFT)
        self.custom_kernel = ttk.Entry(custom_frame, width=5)
        self.custom_kernel.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(tab, text="Применить фильтр", 
                  command=self.apply_nonlinear_filter).grid(row=7, column=0, 
                                                            columnspan=2, pady=20)
        
        info_text = """
        Порядковые статистики:
        • Медианный - устраняет импульсный шум
        • Минимальный - затемняет изображение
        • Максимальный - осветляет изображение
        • Средний - сглаживание
        • Средней точки - (min+max)/2
        """
        info_label = ttk.Label(tab, text=info_text, justify=tk.LEFT, 
                              background='lightyellow')
        info_label.grid(row=8, column=0, columnspan=3, padx=10, pady=10, sticky=tk.W)
        
    def setup_histogram_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Гистограмма и контрастирование")
        
        desc = ttk.Label(tab, text="Методы повышения контраста", 
                        font=('Arial', 10, 'bold'))
        desc.grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(tab, text="Метод обработки:").grid(row=1, column=0, padx=5, 
                                                     pady=5, sticky=tk.W)
        
        self.contrast_method = tk.StringVar(value="linear")
        
        methods = [
            ("Линейное контрастирование", "linear"),
            ("Эквализация гистограммы (RGB)", "equalize_rgb"),
            ("Эквализация гистограммы (HSV)", "equalize_hsv"),
            ("Эквализация гистограммы (HLS)", "equalize_hls")
        ]
        
        for i, (text, value) in enumerate(methods):
            ttk.Radiobutton(tab, text=text, variable=self.contrast_method, 
                           value=value).grid(row=2+i, column=0, padx=20, 
                                            pady=2, sticky=tk.W)
        
        linear_frame = ttk.LabelFrame(tab, text="Параметры линейного контрастирования")
        linear_frame.grid(row=1, column=1, rowspan=4, padx=10, pady=5, sticky=(tk.N, tk.W))
        
        ttk.Label(linear_frame, text="Минимум выхода:").grid(row=0, column=0, padx=5, pady=5)
        self.linear_min = ttk.Scale(linear_frame, from_=0, to=255, orient=tk.HORIZONTAL)
        self.linear_min.set(0)
        self.linear_min.grid(row=0, column=1, padx=5, pady=5)
        self.linear_min_label = ttk.Label(linear_frame, text="0")
        self.linear_min_label.grid(row=0, column=2, padx=5)
        self.linear_min.configure(command=lambda v: self.linear_min_label.configure(
            text=f"{int(float(v))}"))
        
        ttk.Label(linear_frame, text="Максимум выхода:").grid(row=1, column=0, padx=5, pady=5)
        self.linear_max = ttk.Scale(linear_frame, from_=0, to=255, orient=tk.HORIZONTAL)
        self.linear_max.set(255)
        self.linear_max.grid(row=1, column=1, padx=5, pady=5)
        self.linear_max_label = ttk.Label(linear_frame, text="255")
        self.linear_max_label.grid(row=1, column=2, padx=5)
        self.linear_max.configure(command=lambda v: self.linear_max_label.configure(
            text=f"{int(float(v))}"))
        
        ttk.Button(tab, text="Применить метод", 
                  command=self.apply_histogram_method).grid(row=6, column=0, 
                                                            pady=20, padx=5)
        
        ttk.Button(tab, text="Показать гистограммы", 
                  command=self.show_histograms).grid(row=6, column=1, 
                                                     pady=20, padx=5)
        
        info_text = """
        Методы контрастирования:
        • Линейное - растяжение диапазона яркости
        • RGB - эквализация каждого канала отдельно
        • HSV/HLS - эквализация только канала яркости
        """
        info_label = ttk.Label(tab, text=info_text, justify=tk.LEFT, 
                              background='lightyellow')
        info_label.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W)
        
    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[("Изображения", "*.png *.jpg *.jpeg *.bmp *.tiff"), 
                      ("Все файлы", "*.*")]
        )
        
        if file_path:
            self.original_image = cv2.imread(file_path)
            self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
            self.processed_image = self.original_image.copy()
            
            self.display_image(self.original_image, self.original_canvas)
            self.display_image(self.processed_image, self.processed_canvas)
            
    def save_image(self):
        if self.processed_image is None:
            messagebox.showwarning("Предупреждение", "Нет обработанного изображения для сохранения")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("Все файлы", "*.*")]
        )
        
        if file_path:
            image_to_save = cv2.cvtColor(self.processed_image, cv2.COLOR_RGB2BGR)
            cv2.imwrite(file_path, image_to_save)
            messagebox.showinfo("Успех", "Изображение сохранено")
            
    def reset_image(self):
        if self.original_image is not None:
            self.processed_image = self.original_image.copy()
            self.display_image(self.processed_image, self.processed_canvas)
            
    def display_image(self, image, canvas):
        height, width = image.shape[:2]
        max_width, max_height = 600, 450
        
        scale = min(max_width/width, max_height/height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        image_pil = Image.fromarray(resized)
        photo = ImageTk.PhotoImage(image_pil)
        
        canvas.delete("all")
        canvas.create_image(max_width//2, max_height//2, image=photo, anchor=tk.CENTER)
        canvas.image = photo
        
    
    def apply_nonlinear_filter(self):
        if self.original_image is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение")
            return
        
        if self.custom_kernel.get():
            try:
                ksize = int(self.custom_kernel.get())
                if ksize < 3 or ksize % 2 == 0:
                    messagebox.showerror("Ошибка", "Размер ядра должен быть нечетным и >= 3")
                    return
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный размер ядра")
                return
        else:
            ksize = self.kernel_size.get()
        
        filter_type = self.filter_type.get()
        
        if filter_type == "median":
            self.processed_image = self.median_filter(self.original_image, ksize)
        elif filter_type == "min":
            self.processed_image = self.min_filter(self.original_image, ksize)
        elif filter_type == "max":
            self.processed_image = self.max_filter(self.original_image, ksize)
        elif filter_type == "mean":
            self.processed_image = self.mean_filter(self.original_image, ksize)
        elif filter_type == "midpoint":
            self.processed_image = self.midpoint_filter(self.original_image, ksize)
        
        self.display_image(self.processed_image, self.processed_canvas)
        
    def median_filter(self, image, ksize):
        return cv2.medianBlur(image, ksize)
    
    def min_filter(self, image, ksize):
        kernel = np.ones((ksize, ksize), np.uint8)
        return cv2.erode(image, kernel)
    
    def max_filter(self, image, ksize):
        kernel = np.ones((ksize, ksize), np.uint8)
        return cv2.dilate(image, kernel)
    
    def mean_filter(self, image, ksize):
        return cv2.blur(image, (ksize, ksize))
    
    def midpoint_filter(self, image, ksize):
        min_filtered = self.min_filter(image, ksize)
        max_filtered = self.max_filter(image, ksize)
        return ((min_filtered.astype(np.float32) + max_filtered.astype(np.float32)) / 2).astype(np.uint8)
    
    
    def apply_histogram_method(self):
        if self.original_image is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение")
            return
        
        method = self.contrast_method.get()
        
        if method == "linear":
            min_out = int(self.linear_min.get())
            max_out = int(self.linear_max.get())
            
            if min_out >= max_out:
                messagebox.showerror("Ошибка", "Минимум должен быть меньше максимума")
                return
                
            self.processed_image = self.linear_contrast(self.original_image, min_out, max_out)
            
        elif method == "equalize_rgb":
            self.processed_image = self.equalize_histogram_rgb(self.original_image)
            
        elif method == "equalize_hsv":
            self.processed_image = self.equalize_histogram_hsv(self.original_image)
            
        elif method == "equalize_hls":
            self.processed_image = self.equalize_histogram_hls(self.original_image)
        
        self.display_image(self.processed_image, self.processed_canvas)
        
    def linear_contrast(self, image, min_out=0, max_out=255):
        """Линейное контрастирование"""
        result = np.zeros_like(image, dtype=np.float32)
        
        for i in range(3): 
            channel = image[:, :, i].astype(np.float32)
            min_in = np.min(channel)
            max_in = np.max(channel)
            
            if max_in > min_in:
                result[:, :, i] = (channel - min_in) * (max_out - min_out) / (max_in - min_in) + min_out
            else:
                result[:, :, i] = channel
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    def equalize_histogram_rgb(self, image):
        result = np.zeros_like(image)
        
        for i in range(3):
            result[:, :, i] = cv2.equalizeHist(image[:, :, i])
        
        return result
    
    def equalize_histogram_hsv(self, image):
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        hsv[:, :, 2] = cv2.equalizeHist(hsv[:, :, 2])
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    
    def equalize_histogram_hls(self, image):
        hls = cv2.cvtColor(image, cv2.COLOR_RGB2HLS)
        hls[:, :, 1] = cv2.equalizeHist(hls[:, :, 1])
        return cv2.cvtColor(hls, cv2.COLOR_HLS2RGB)
    
    def show_histograms(self):
        if self.original_image is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение")
            return
        
        fig = Figure(figsize=(12, 8))
        
        ax1 = fig.add_subplot(2, 2, 1)
        self.plot_histogram(self.original_image, ax1, "Оригинальное изображение")
        
        if self.processed_image is not None:
            ax2 = fig.add_subplot(2, 2, 2)
            self.plot_histogram(self.processed_image, ax2, "Обработанное изображение")
        
        if self.processed_image is not None:
            ax3 = fig.add_subplot(2, 1, 2)
            colors = ('r', 'g', 'b')
            for i, color in enumerate(colors):
                hist_orig = cv2.calcHist([self.original_image], [i], None, [256], [0, 256])
                hist_proc = cv2.calcHist([self.processed_image], [i], None, [256], [0, 256])
                ax3.plot(hist_orig, color=color, alpha=0.5, linestyle='--', label=f'{color.upper()} (ориг.)')
                ax3.plot(hist_proc, color=color, alpha=0.7, label=f'{color.upper()} (обраб.)')
            ax3.set_title("Сравнение гистограмм")
            ax3.set_xlabel("Значение яркости")
            ax3.set_ylabel("Количество пикселей")
            ax3.legend()
            ax3.grid(True, alpha=0.3)
        
        hist_window = tk.Toplevel(self.root)
        hist_window.title("Гистограммы изображений")
        hist_window.geometry("1200x800")
        
        canvas = FigureCanvasTkAgg(fig, master=hist_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def plot_histogram(self, image, ax, title):
        colors = ('r', 'g', 'b')
        for i, color in enumerate(colors):
            hist = cv2.calcHist([image], [i], None, [256], [0, 256])
            ax.plot(hist, color=color, label=f'{color.upper()} канал')
        
        ax.set_title(title)
        ax.set_xlabel("Значение яркости")
        ax.set_ylabel("Количество пикселей")
        ax.legend()
        ax.grid(True, alpha=0.3)


def main():
    root = tk.Tk()
    app = ImageProcessingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()