import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import cv2
import numpy as np

class ImageProcessingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processing App")

        self.image_path = None
        self.original_image = None
        self.cropped_image = None
        self.thumbnail = None

        self.start_x = None
        self.start_y = None
        self.rect = None

        self.setup_ui()

    def setup_ui(self):
        # Buttons to load and save images
        self.load_button = ttk.Button(self.root, text="Load Image", command=self.load_image)
        self.load_button.pack(pady=5)

        self.save_button = ttk.Button(self.root, text="Save Image", command=self.save_image, state=tk.DISABLED)
        self.save_button.pack(pady=5)

        # Canvas for image display
        self.canvas = tk.Canvas(self.root, width=600, height=400, bg="gray")
        self.canvas.pack()
        self.canvas.bind("<ButtonPress-1>", self.start_crop)
        self.canvas.bind("<B1-Motion>", self.update_crop)
        self.canvas.bind("<ButtonRelease-1>", self.end_crop)
#Part 3
        # Slider for resizing
        self.slider = ttk.Scale(self.root, from_=1, to=5, orient=tk.HORIZONTAL, command=self.resize_preview)
        self.slider.pack(pady=5)
        self.slider.set(1)
        self.slider_label = ttk.Label(self.root, text="Resize Preview")
        self.slider_label.pack()

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png *.jpeg")])
        if file_path:
            self.image_path = file_path
            self.original_image = cv2.imread(file_path)
            self.display_thumbnail()

    def display_thumbnail(self):
        # Create a thumbnail (temporary view-only image)
        image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (300, 200))
        self.thumbnail = ImageTk.PhotoImage(Image.fromarray(image))
        self.canvas.create_image(300, 200, image=self.thumbnail, anchor=tk.CENTER)

    def start_crop(self, event):
        self.start_x, self.start_y = event.x, event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = None

    def update_crop(self, event):
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline="red")

    def end_crop(self, event):
        if not self.original_image:
            return

        end_x, end_y = event.x, event.y

        # Calculate inverse cropping coordinates
        x1, y1 = min(self.start_x, end_x), min(self.start_y, end_y)
        x2, y2 = max(self.start_x, end_x), max(self.start_y, end_y)

        # Convert canvas coordinates to image coordinates
        height, width, _ = self.original_image.shape
        x1 = int(x1 * width / self.canvas.winfo_width())
        x2 = int(x2 * width / self.canvas.winfo_width())
        y1 = int(y1 * height / self.canvas.winfo_height())
        y2 = int(y2 * height / self.canvas.winfo_height())

        # Perform inverse cropping
        mask = np.zeros(self.original_image.shape[:2], dtype=np.uint8)
        mask[y1:y2, x1:x2] = 255
        self.cropped_image = cv2.bitwise_and(self.original_image, self.original_image, mask=~mask)
#Part 4
        # Show cropped result
        cropped_preview = cv2.cvtColor(self.cropped_image, cv2.COLOR_BGR2RGB)
        cropped_preview = cv2.resize(cropped_preview, (300, 200))
        self.cropped_thumbnail = ImageTk.PhotoImage(Image.fromarray(cropped_preview))
        self.canvas.create_image(300, 200, image=self.cropped_thumbnail, anchor=tk.CENTER)

        self.save_button.config(state=tk.NORMAL)

    def resize_preview(self, value):
        if not self.cropped_image:
            return

        scale = float(value)
        resized = cv2.resize(self.cropped_image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        resized_preview = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)

        preview_image = ImageTk.PhotoImage(Image.fromarray(resized_preview))
        self.canvas.create_image(300, 200, image=preview_image, anchor=tk.CENTER)
        self.canvas.image = preview_image  # Prevent garbage collection

    def save_image(self):
        if self.cropped_image is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png"), ("JPEG Files", "*.jpg")])
            if file_path:
                cv2.imwrite(file_path, self.cropped_image)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessingApp(root)
    root.mainloop()
