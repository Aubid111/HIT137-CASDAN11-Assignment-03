from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, Canvas, Button, Label, Scale, HORIZONTAL, Frame

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processor")

        # Adjust background color and scheme to be aesthetically appealing
        self.root.configure(bg="#ECF0F1")

        # Stacks for Undo/Redo (store PIL.Image objects)
        self.undo_stack = []
        self.redo_stack = []

        # 
        top_frame = Frame(self.root, bg="#ECF0F1")
        top_frame.pack(pady=10)

        # First Step -  Define 'Load Image Button'
        self.load_button = Button(
            top_frame,
            text="Load Image",
            command=self.load_image,
            font=("Helvetica", 11, "bold"),
            bg="#27AE60",
            fg="#FFFFFF",
            activebackground="#2ECC71",
            activeforeground="#FFFFFF",
            bd=0,
            padx=12,
            pady=6,
            relief="flat"
        )
        self.load_button.pack(side=tk.LEFT, padx=10)

        #Define 'Save Cropped Image' Button
        self.save_button = Button(
            top_frame,
            text="Save Cropped Image",
            command=self.save_image,
            state="disabled",
            font=("Helvetica", 11, "bold"),
            bg="#2980B9",
            fg="#FFFFFF",
            activebackground="#3498DB",
            activeforeground="#FFFFFF",
            bd=0,
            padx=12,
            pady=6,
            relief="flat"
        )
        self.save_button.pack(side=tk.LEFT, padx=10)

        # Define 'Rotate' Buttons - this will allow users to rotate the cropped image (either Clockwise or AntiClockwise by 90 deg.) prior to saving if needed
        # Rotate Clockwise Button
        self.rotate_cw_button = Button(
            top_frame,
            text="Rotate 90° Anti-Clockwise",
            command=lambda: self.rotate_cropped_image(90),
            font=("Helvetica", 11, "bold"),
            bg="#9B59B6",
            fg="#FFFFFF",
            activebackground="#B370CF",
            activeforeground="#FFFFFF",
            bd=0,
            padx=12,
            pady=6,
            relief="flat"
        )
        self.rotate_cw_button.pack(side=tk.LEFT, padx=10)

        # Rotate Anticlockwise Button
        self.rotate_ccw_button = Button(
            top_frame,
            text="Rotate 90° Clockwise",
            command=lambda: self.rotate_cropped_image(-90),
            font=("Helvetica", 11, "bold"),
            bg="#9B59B6",
            fg="#FFFFFF",
            activebackground="#B370CF",
            activeforeground="#FFFFFF",
            bd=0,
            padx=12,
            pady=6,
            relief="flat"
        )
        self.rotate_ccw_button.pack(side=tk.LEFT, padx=10)

        # Resize Cropped Image Button
        self.resize_label = Label(
            top_frame,
            text="Resize Cropped Image:",
            bg="#ECF0F1",
            font=("Helvetica", 11)
        )
        self.resize_label.pack(side=tk.LEFT, padx=(20, 5))

        self.resize_slider = Scale(
            top_frame,
            from_=10,
            to=200,
            orient=HORIZONTAL,
            command=self.resize_image,
            state="disabled",
            bg="#ECF0F1",
            highlightthickness=0,  # Remove extra highlight border
            troughcolor="#BDC3C7",
            font=("Helvetica", 10)
        )
        self.resize_slider.pack(side=tk.LEFT, padx=5)

        #  MIDDLE FRAME FOR IMAGES
        images_frame = Frame(self.root, bg="#ECF0F1")
        images_frame.pack()

        # Window to show original loaded image
        original_frame = Frame(images_frame, bg="#ECF0F1")
        original_frame.pack(side=tk.LEFT, padx=20, pady=20)

        self.canvas_original = Canvas(
            original_frame,
            width=400,
            height=600,
            bg="white",
            bd=0,
            highlightthickness=0
        )
        self.canvas_original.pack()

        self.label_original = Label(
            original_frame,
            text="Original Image",
            font=("Helvetica", 12, "bold"),
            bg="#ECF0F1"
        )
        self.label_original.pack(pady=5)

       # Window to show cropped image
        cropped_frame = Frame(images_frame, bg="#ECF0F1")
        cropped_frame.pack(side=tk.RIGHT, padx=20, pady=20)

        self.canvas_resized = Canvas(
            cropped_frame,
            width=400,
            height=600,
            bg="white",
            bd=0,
            highlightthickness=0
        )
        self.canvas_resized.pack()

        self.label_cropped = Label(
            cropped_frame,
            text="Cropped Image",
            font=("Helvetica", 12, "bold"),
            bg="#ECF0F1"
        )
        self.label_cropped.pack(pady=5)

        # Internal state
        self.original_image = None
        self.display_image = None  # Shown on the Original canvas
        self.cropped_image = None  # Cropped from display_image
        self.resized_image = None  # Possibly resized or rotated version of cropped_image
        self.start_x = self.start_y = 0
        self.rect_id = None

        # Bind mouse events for cropping on the original canvas
        self.canvas_original.bind("<ButtonPress-1>", self.start_crop)
        self.canvas_original.bind("<B1-Motion>", self.update_crop)
        self.canvas_original.bind("<ButtonRelease-1>", self.finish_crop)

        # Bonus Sections - Siam can you please come up with a list of additional keyboard shortcuts we can use
        root.bind("<Control-o>", lambda e: self.load_image())
        root.bind("<Control-s>", lambda e: self.save_image())
        root.bind("<Control-z>", lambda e: self.undo())
        root.bind("<Control-y>", lambda e: self.redo())
        root.bind("<Control-r>", lambda e: self.rotate_cropped_image(90))  # Rotate +90
        root.bind("<Shift-Control-R>", lambda e: self.rotate_cropped_image(-90))  # Rotate -90

    
    # UNDO / REDO Capabilities
   
    undo_stack = []
    redo_stack = []

    def get_current_final_image(self):
        """Return the current final image in the pipeline."""
        return self.resized_image or self.cropped_image or self.display_image

    def push_state(self):
        """Push current final image onto undo stack and clear redo stack."""
        current = self.get_current_final_image()
        if current:
            self.undo_stack.append(current.copy())
            self.redo_stack.clear()

    def undo(self):
        """Undo the last action if possible."""
        if not self.undo_stack:
            return

        # Move current image to redo stack
        current = self.get_current_final_image()
        if current:
            self.redo_stack.append(current.copy())

        # Restore the last state from undo stack
        last_state = self.undo_stack.pop()
        self.resized_image = last_state
        self.cropped_image = None
        self.show_image(self.resized_image, self.canvas_resized)
        # Also refresh the original canvas
        if self.display_image:
            self.show_image(self.display_image, self.canvas_original)

    def redo(self):
        """Redo the previously undone action."""
        if not self.redo_stack:
            return

        # Move current image to undo stack
        current = self.get_current_final_image()
        if current:
            self.undo_stack.append(current.copy())

        # Restore the image from redo stack
        next_state = self.redo_stack.pop()
        self.resized_image = next_state
        self.cropped_image = None
        self.show_image(self.resized_image, self.canvas_resized)
        # Also refresh the original canvas
        if self.display_image:
            self.show_image(self.display_image, self.canvas_original)

    #  LOAD / SAVE Capabilities for user to load/save the cropped image
    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")]
        )
        if file_path:
            self.push_state()  # Save current state for undo
            self.original_image = Image.open(file_path)
            self.display_image = self.original_image.copy()
            self.display_image = self.display_image.resize((400, 600), Image.LANCZOS)
            self.show_image(self.display_image, self.canvas_original)
            self.cropped_image = None
            self.resized_image = None
            self.resize_slider.set(100)

    def save_image(self):
        final_img = self.get_current_final_image()
        if final_img is None:
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        if file_path:
            final_img.save(file_path)


    # Cropping Capability - for Siam to do please.
    # 
    def start_crop(self, event):
        if self.display_image is None:
            return
        self.start_x, self.start_y = event.x, event.y
        self.rect_id = self.canvas_original.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y, outline="red"
        )

    def update_crop(self, event):
        if self.rect_id is not None:
            self.canvas_original.coords(
                self.rect_id,
                self.start_x,
                self.start_y,
                event.x,
                event.y
            )

    def finish_crop(self, event):
        if self.display_image is None:
            return
        self.push_state()  # Save current state before cropping

        x0, y0, x1, y1 = self.start_x, self.start_y, event.x, event.y
        x0, x1 = sorted([x0, x1])
        y0, y1 = sorted([y0, y1])

        self.cropped_image = self.display_image.crop((x0, y0, x1, y1))
        self.show_image(self.display_image, self.canvas_original)

        if self.cropped_image:
            self.save_button["state"] = "normal"
            self.resize_slider["state"] = "normal"
            self.show_cropped_image()

    def show_cropped_image(self):
        if self.cropped_image is None:
            return
        # Resize to 400x600 to fill the canvas
        cropped = self.cropped_image.resize((400, 600), Image.LANCZOS)
        self.resized_image = cropped
        self.show_image(cropped, self.canvas_resized)

    # 
    #Re-sizing capability for user to adjust the scale of the cropped image. 
    # 
    def resize_image(self, scale_value):
        if self.cropped_image is None:
            return
        self.push_state()  # Save state before resizing

        scale = int(scale_value) / 100
        new_width = int(self.cropped_image.width * scale)
        new_height = int(self.cropped_image.height * scale)
        resized = self.cropped_image.resize((new_width, new_height), Image.LANCZOS)
        self.resized_image = resized
        self.show_image(resized, self.canvas_resized)

    # 
    # Rotation capabilities either clockwise or anticlockwisee by 90 degrees prior to saving cropped image.
    # 
    def rotate_cropped_image(self, angle):
        """
        Rotates the current final image (cropped or resized) by `angle` degrees.
        Positive angles rotate clockwise, negative angles rotate anticlockwise.
        """
        final_img = self.get_current_final_image()
        if final_img is None:
            return

        self.push_state()  # Save state before rotating
        rotated = final_img.rotate(angle, expand=True)
        self.resized_image = rotated
        self.cropped_image = None
        self.show_image(rotated, self.canvas_resized)


    # Image Rendering - needs more work 
    # 
    def show_image(self, image, canvas):
        img = ImageTk.PhotoImage(image)
        canvas.image = img
        # Clear any existing image
        canvas.delete("all")
        canvas.create_image(0, 0, anchor=tk.NW, image=img)

# Test application and all capabilities prior to submitting assignment please. Includes shortcuts and all rotation and undo capabilities.
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()
