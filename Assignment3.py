import tkinter as tk
from tkinter import filedialog, ttk
import cv2
from PIL import Image, ImageTk
import numpy as np

class ImageEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Editor")

        self.image_path = None
        self.original_image = None
        self.cropped_image = None
        self.rect_start = None
        self.rect_end = None
        self.rect_id = None

        self.setup_ui()

    def setup_ui(self):
        # Frame for controls
        control_frame = tk.Frame(self.root)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        load_button = tk.Button(control_frame, text="Load Image", command=self.load_image)
        load_button.pack(side=tk.LEFT, padx=5, pady=5)

        save_button = tk.Button(control_frame, text="Save Image", command=self.save_image)
        save_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.resize_slider = ttk.Scale(control_frame, from_=0.1, to=2.0, resolution=0.1, orient=tk.HORIZONTAL, command=self.resize_image)
        self.resize_slider.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        self.resize_slider.set(1.0)

        # Canvas for displaying images
        self.canvas = tk.Canvas(self.root, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<ButtonPress-1>", self.start_rectangle)
        self.canvas.bind("<B1-Motion>", self.update_rectangle)
        self.canvas.bind("<ButtonRelease-1>", self.crop_image)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff")])
        if file_path:
            self.image_path = file_path
            self.original_image = cv2.imread(self.image_path)
            self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
            self.display_image(self.original_image)

    def display_image(self, image):
        self.canvas.delete("all")
        self.tk_image = ImageTk.PhotoImage(Image.fromarray(image))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def start_rectangle(self, event):
        self.rect_start = (event.x, event.y)
        self.rect_id = self.canvas.create_rectangle(event.x, event.y, event.x, event.y, outline="red")

    def update_rectangle(self, event):
        self.rect_end = (event.x, event.y)
        self.canvas.coords(self.rect_id, self.rect_start[0], self.rect_start[1], event.x, event.y)

    def crop_image(self, event):
        if self.original_image is None or self.rect_start is None or self.rect_end is None:
            return

        x_start, y_start = map(int, self.rect_start)
        x_end, y_end = map(int, self.rect_end)

        x1, x2 = sorted([x_start, x_end])
        y1, y2 = sorted([y_start, y_end])

        scale_x = self.original_image.shape[1] / self.canvas.winfo_width()
        scale_y = self.original_image.shape[0] / self.canvas.winfo_height()

        x1 = int(x1 * scale_x)
        x2 = int(x2 * scale_x)
        y1 = int(y1 * scale_y)
        y2 = int(y2 * scale_y)

        self.cropped_image = self.original_image[y1:y2, x1:x2]
        self.display_image(self.original_image)
        self.display_cropped_image()

    def display_cropped_image(self):
        if self.cropped_image is not None:
            cropped_window = tk.Toplevel(self.root)
            cropped_window.title("Cropped Image")

            cropped_canvas = tk.Canvas(cropped_window)
            cropped_canvas.pack(fill=tk.BOTH, expand=True)

            tk_cropped_image = ImageTk.PhotoImage(Image.fromarray(self.cropped_image))
            cropped_canvas.create_image(0, 0, anchor=tk.NW, image=tk_cropped_image)
            cropped_canvas.image = tk_cropped_image

    def resize_image(self, value):
        if self.cropped_image is not None:
            scale = float(value)
            width = int(self.cropped_image.shape[1] * scale)
            height = int(self.cropped_image.shape[0] * scale)
            resized_image = cv2.resize(self.cropped_image, (width, height), interpolation=cv2.INTER_LINEAR)
            self.display_cropped_image(resized_image)

    def save_image(self):
        if self.cropped_image is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All Files", "*.*")])
            if file_path:
                cv2.imwrite(file_path, cv2.cvtColor(self.cropped_image, cv2.COLOR_RGB2BGR))

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditorApp(root)
    root.mainloop()