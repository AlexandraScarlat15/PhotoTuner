import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk, ImageDraw
import cv2
import numpy as np
from phototuner.processing import enhance_image, enhance_image_accurate


class PhotoTunerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PhotoTuner")
        self.root.geometry("1000x750")
        self.root.configure(bg="#1e1e1e")

        self.original_image = None
        self.processed_image = None
        self.preview_size = (600, 400)

        self.mode = tk.StringVar(value="standard")
        self.crop_mode = False
        self.crop_points = []
        self.pre_crop_image = None

        self.image_label = tk.Label(self.root, bg="#2b2b2b")
        self.image_label.pack(pady=10)
        self.image_label.bind("<Button-1>", self.on_image_click)
        self.show_placeholder()

        mode_frame = tk.Frame(self.root, bg="#1e1e1e")
        mode_frame.pack(pady=5)
        tk.Radiobutton(mode_frame, text="Standard Mode", variable=self.mode, value="standard",
                       command=self.update_controls, bg="#1e1e1e", fg="white", selectcolor="#2b2b2b").pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(mode_frame, text="Advanced Mode", variable=self.mode, value="advanced",
                       command=self.update_controls, bg="#1e1e1e", fg="white", selectcolor="#2b2b2b").pack(side=tk.LEFT, padx=10)

        self.controls_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.controls_frame.pack(pady=10)

        self.sharpen_var = tk.DoubleVar(value=30)
        self.contrast_var = tk.DoubleVar(value=50)
        self.color_var = tk.DoubleVar(value=10)

        self.update_controls()

    def show_placeholder(self):
        w, h = self.preview_size
        placeholder = Image.new("RGB", (w, h), color="#2b2b2b")
        draw = ImageDraw.Draw(placeholder)
        draw.rectangle((10, 10, w - 10, h - 10), outline="#888", width=2)
        draw.text((w // 2 - 50, h // 2 - 10), "Load an Image", fill="#888")
        img_tk = ImageTk.PhotoImage(placeholder)
        self.image_label.configure(image=img_tk)
        self.image_label.image = img_tk

    def update_controls(self):
        for widget in self.controls_frame.winfo_children():
            widget.destroy()

        if self.mode.get() == "standard":
            
            left = tk.Frame(self.controls_frame, bg="#1e1e1e")
            right = tk.Frame(self.controls_frame, bg="#1e1e1e")
            left.pack(side=tk.LEFT, padx=30)
            right.pack(side=tk.LEFT, padx=30)

            for text, cmd in [("Load Image", self.load_image), ("Save Image", self.save_image)]:
                tk.Button(left, text=text, command=cmd, width=20, bg="#2b2b2b", fg="white").pack(pady=5)

            for name in ["Natural", "Vivid", "Pro"]:
                tk.Button(right, text=name, width=20, command=lambda m=name.lower(): self.apply_preset(m),
                          bg="#3c3c3c", fg="white").pack(pady=5)
        else:
           
            left = tk.Frame(self.controls_frame, bg="#1e1e1e")
            right = tk.Frame(self.controls_frame, bg="#1e1e1e")
            left.pack(side=tk.LEFT, padx=30)
            right.pack(side=tk.LEFT, padx=30)

            self._add_slider(left, "Sharpen Strength", self.sharpen_var)
            self._add_slider(left, "Contrast", self.contrast_var)
            self._add_slider(left, "Color Boost", self.color_var)

            for text, cmd in [
                ("Load Image", self.load_image),
                ("Save Image", self.save_image),
                ("Enable Crop Mode", self.enable_crop_mode),
                ("Apply Crop", self.apply_crop),
                ("Undo Crop", self.undo_crop)
            ]:
                tk.Button(right, text=text, command=cmd, width=20, bg="#2b2b2b", fg="white").pack(pady=4)

    def _add_slider(self, parent, label, var):
        frame = tk.Frame(parent, bg="#1e1e1e")
        frame.pack(pady=6)

        tk.Label(frame, text=label, width=20, anchor='w', fg="white", bg="#1e1e1e").pack(side=tk.LEFT)
        value_label = tk.Label(frame, text=f"{var.get():.2f}", width=6, fg="white", bg="#1e1e1e")
        value_label.pack(side=tk.RIGHT, padx=5)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TScale", background="#1e1e1e", troughcolor="#333", sliderthickness=14)

        slider = ttk.Scale(frame, from_=0, to=100, variable=var,
                           orient=tk.HORIZONTAL, length=280, style="TScale")
        slider.pack(side=tk.LEFT)

        def on_slide(_):
            value_label.config(text=f"{var.get():.2f}")
            self.update_preview()

        def jump_to_click(event):
            width = event.widget.winfo_width()
            rel_x = event.x / width
            new_val = rel_x * 100
            var.set(round(new_val, 2))
            value_label.config(text=f"{var.get():.2f}")
            self.update_preview()

        slider.bind("<Button-1>", jump_to_click)
        slider.bind("<B1-Motion>", on_slide)

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png")])
        if not path:
            return
        bgr = cv2.imread(path)
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        self.original_image = rgb
        self.processed_image = rgb.copy()
        self.show_result(rgb)

    def update_preview(self):
        if self.original_image is None or self.mode.get() != "advanced":
            return
        sharpen = self.sharpen_var.get() / 100.0
        contrast = 0.7 + (self.contrast_var.get() / 100.0) * 0.6
        color = self.color_var.get()
        enhanced = enhance_image_accurate(self.original_image.copy(), sharpen, contrast, color)
        self.processed_image = enhanced
        self.show_result(enhanced)

    def apply_preset(self, mode):
        if self.original_image is None:
            return
        self.processed_image = enhance_image(self.original_image.copy(), mode)
        self.show_result(self.processed_image)

    def show_result(self, img):
        h, w = img.shape[:2]
        target_w, target_h = self.preview_size

        scale = min(target_w / w, target_h / h)
        new_w, new_h = int(w * scale), int(h * scale)
        resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        preview = np.full((target_h, target_w, 3), 30, dtype=np.uint8)
        offset_x = (target_w - new_w) // 2
        offset_y = (target_h - new_h) // 2
        preview[offset_y:offset_y + new_h, offset_x:offset_x + new_w] = resized

        if self.crop_mode and len(self.crop_points) >= 1:
            for pt in self.crop_points:
                x = int(pt[0] * scale) + offset_x
                y = int(pt[1] * scale) + offset_y
                cv2.circle(preview, (x, y), 5, (0, 255, 255), -1)

            if len(self.crop_points) == 2:
                pt1 = (int(self.crop_points[0][0] * scale) + offset_x, int(self.crop_points[0][1] * scale) + offset_y)
                pt2 = (int(self.crop_points[1][0] * scale) + offset_x, int(self.crop_points[1][1] * scale) + offset_y)
                cv2.rectangle(preview, pt1, pt2, (0, 128, 255), 2)

        img_pil = Image.fromarray(preview)
        img_tk = ImageTk.PhotoImage(img_pil)
        self.image_label.configure(image=img_tk)
        self.image_label.image = img_tk

    def on_image_click(self, event):
        if self.crop_mode:
            self.record_crop_point(event)
        else:
            self.load_image()

    def record_crop_point(self, event):
        if self.processed_image is None:
            return
        scale = min(self.preview_size[0] / self.processed_image.shape[1],
                    self.preview_size[1] / self.processed_image.shape[0])
        offset_x = (self.preview_size[0] - int(self.processed_image.shape[1] * scale)) // 2
        offset_y = (self.preview_size[1] - int(self.processed_image.shape[0] * scale)) // 2
        x_real = int((event.x - offset_x) / scale)
        y_real = int((event.y - offset_y) / scale)

        self.crop_points.append((x_real, y_real))
        self.show_result(self.processed_image)

    def enable_crop_mode(self):
        self.crop_mode = True
        self.crop_points = []

    def apply_crop(self):
        if len(self.crop_points) != 2:
            print("Select 2 points")
            return
        self.pre_crop_image = self.processed_image.copy()
        x1, y1 = self.crop_points[0]
        x2, y2 = self.crop_points[1]
        x_min, x_max = sorted([x1, x2])
        y_min, y_max = sorted([y1, y2])
        cropped = self.processed_image[y_min:y_max, x_min:x_max]
        self.original_image = cropped
        self.processed_image = cropped
        self.crop_points.clear()
        self.crop_mode = False
        self.show_result(cropped)

    def undo_crop(self):
        if self.pre_crop_image is not None:
            self.original_image = self.pre_crop_image.copy()
            self.processed_image = self.pre_crop_image.copy()
            self.crop_points.clear()
            self.crop_mode = False
            self.show_result(self.processed_image)

    def save_image(self):
        if self.processed_image is None:
            return
        path = filedialog.asksaveasfilename(defaultextension=".jpg",
                                            filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")])
        if not path:
            return
        bgr = cv2.cvtColor(self.processed_image, cv2.COLOR_RGB2BGR)
        cv2.imwrite(path, bgr)


if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoTunerApp(root)
    root.mainloop()
