import tkinter as tk
from tkinter import ttk, colorchooser
import colorsys

class ColorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Color Converter: RGB - CMYK - HLS")
        self.root.geometry("800x450")
        
        self.updating = False
        
        self.current_rgb = (0, 0, 0)

        top_frame = ttk.Frame(root, padding=10)
        top_frame.pack(fill=tk.X)
        
        self.color_display = tk.Label(top_frame, bg="black", width=20, height=2, relief="sunken")
        self.color_display.pack(side=tk.LEFT, padx=10)
        
        btn_palette = ttk.Button(top_frame, text="Выбрать из палитры", command=self.open_palette)
        btn_palette.pack(side=tk.LEFT, padx=10)

        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.rgb_vars = self.create_model_panel(main_frame, "RGB", ["R", "G", "B"], (0, 255), 0)
        self.cmyk_vars = self.create_model_panel(main_frame, "CMYK", ["C", "M", "Y", "K"], (0, 100), 1)
        self.hls_vars = self.create_model_panel(main_frame, "HLS", ["H", "L", "S"], (0, 360, 100, 100), 2) # H-360, L/S-100

        self.update_all_from_rgb(0, 0, 0)

    def create_model_panel(self, parent, title, labels, limit, col_idx):
        frame = ttk.LabelFrame(parent, text=title, padding=10)
        frame.grid(row=0, column=col_idx, sticky="nsew", padx=5)
        parent.columnconfigure(col_idx, weight=1)
        
        vars_dict = {}
        
        for i, label in enumerate(labels):
            tk.Label(frame, text=label).grid(row=i, column=0, sticky="w")
            if len(limit) == 2:
                current_max = limit[1]
            else:
                current_max = limit[1] if i == 0 else limit[2]

            var = tk.DoubleVar()
            vars_dict[label] = var
            
            entry = ttk.Entry(frame, textvariable=var, width=5)
            entry.grid(row=i, column=1, padx=5)
            entry.bind('<Return>', lambda e, m=title: self.on_entry_change(m))
            entry.bind('<FocusOut>', lambda e, m=title: self.on_entry_change(m))

            scale = ttk.Scale(frame, from_=limit[0], to=current_max, orient=tk.HORIZONTAL, variable=var)
            scale.grid(row=i, column=2, sticky="ew", padx=5)
            scale.configure(command=lambda val, m=title: self.on_slider_change(m))
            
        return vars_dict

    
    def rgb_to_cmyk(self, r, g, b):
        if (r, g, b) == (0, 0, 0): return 0, 0, 0, 100
        c = 1 - r / 255
        m = 1 - g / 255
        y = 1 - b / 255
        k = min(c, m, y)
        c = (c - k) / (1 - k)
        m = (m - k) / (1 - k)
        y = (y - k) / (1 - k)
        return round(c*100), round(m*100), round(y*100), round(k*100)

    def cmyk_to_rgb(self, c, m, y, k):
        r = 255 * (1 - c/100) * (1 - k/100)
        g = 255 * (1 - m/100) * (1 - k/100)
        b = 255 * (1 - y/100) * (1 - k/100)
        return round(r), round(g), round(b)

    def rgb_to_hls_ui(self, r, g, b):
        h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
        return round(h*360), round(l*100), round(s*100)

    def hls_to_rgb_ui(self, h, l, s):
        r, g, b = colorsys.hls_to_rgb(h/360, l/100, s/100)
        return round(r*255), round(g*255), round(b*255)


    def open_palette(self):
        color = colorchooser.askcolor(title="Выберите цвет")[0]
        if color:
            self.update_all_from_rgb(int(color[0]), int(color[1]), int(color[2]))

    def on_slider_change(self, model):
        if self.updating: return
        self.process_change(model)

    def on_entry_change(self, model):
        if self.updating: return
        self.process_change(model)

    def process_change(self, model):
        self.updating = True
        try:
            if model == "RGB":
                r = self.rgb_vars["R"].get()
                g = self.rgb_vars["G"].get()
                b = self.rgb_vars["B"].get()
                self.update_all_from_rgb(r, g, b)
            
            elif model == "CMYK":
                c = self.cmyk_vars["C"].get()
                m = self.cmyk_vars["M"].get()
                y = self.cmyk_vars["Y"].get()
                k = self.cmyk_vars["K"].get()
                r, g, b = self.cmyk_to_rgb(c, m, y, k)
                self.update_all_from_rgb(r, g, b, source="CMYK")
                
            elif model == "HLS":
                h = self.hls_vars["H"].get()
                l = self.hls_vars["L"].get()
                s = self.hls_vars["S"].get()
                r, g, b = self.hls_to_rgb_ui(h, l, s)
                self.update_all_from_rgb(r, g, b, source="HLS")
        except Exception as e:
            print(f"Error calculating color: {e}")
        finally:
            self.updating = False

    def update_all_from_rgb(self, r, g, b, source="RGB"):
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        
        self.current_rgb = (int(r), int(g), int(b))
        hex_color = f"#{int(r):02x}{int(g):02x}{int(b):02x}"
        self.color_display.config(bg=hex_color)

        if source != "RGB":
            self.rgb_vars["R"].set(int(r))
            self.rgb_vars["G"].set(int(g))
            self.rgb_vars["B"].set(int(b))
        
        if source != "CMYK":
            c, m, y, k = self.rgb_to_cmyk(r, g, b)
            self.cmyk_vars["C"].set(c)
            self.cmyk_vars["M"].set(m)
            self.cmyk_vars["Y"].set(y)
            self.cmyk_vars["K"].set(k)
            
        if source != "HLS":
            h, l, s = self.rgb_to_hls_ui(r, g, b)
            self.hls_vars["H"].set(h)
            self.hls_vars["L"].set(l)
            self.hls_vars["S"].set(s)

if __name__ == "__main__":
    root = tk.Tk()
    app = ColorApp(root)
    root.mainloop()