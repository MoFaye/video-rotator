import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil
import time
from moviepy.editor import VideoFileClip
from PIL import Image, ImageTk
import re

class VideoRotatorApp:
    def __init__(self, root):
        self.root = root
        self.filepath = None
        self.preview_frame = None
        self.overwrite = tk.BooleanVar()
        self.video_name_var = tk.StringVar(value="No video selected")
        self.setup_ui()

    def setup_ui(self):
        self.root.title("Video Rotator Tool")
        control_frame = tk.Frame(self.root)
        control_frame.pack(side=tk.LEFT, padx=10, pady=10)
        preview_frame = tk.Frame(self.root)
        preview_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        tk.Label(control_frame, textvariable=self.video_name_var).pack(pady=10)

        self.select_button = tk.Button(control_frame, text="Select Video", command=self.select_video)
        self.select_button.pack(pady=10)
        self.angle_var = tk.StringVar(control_frame)
        self.angle_var.set("0")  # Default value
        self.angles = ["0", "90", "180", "270"]
        self.angle_menu = tk.OptionMenu(control_frame, self.angle_var, *self.angles, command=self.update_preview)
        self.angle_menu.pack(pady=20)
        self.angle_menu.config(state="disabled")
        self.overwrite_check = tk.Checkbutton(control_frame, text="Overwrite Original", variable=self.overwrite)
        self.overwrite_check.pack(pady=10)
        self.rotate_button = tk.Button(control_frame, text="Rotate Video", command=self.rotate_video, state="disabled")
        self.rotate_button.pack(pady=10)
        self.preview_label = tk.Label(preview_frame)
        self.preview_label.pack(pady=10)

    def select_video(self):
        filepath = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.mov;*.avi")])
        if not filepath:
            messagebox.showinfo("Video Rotator", "No video selected.")
            self.video_name_var.set("No video selected")
        else:
            self.filepath = filepath
            self.video_name_var.set(f"Selected: {os.path.basename(self.filepath)}")
            self.angle_menu.config(state="normal")
            self.rotate_button.config(state="normal")
            self.show_preview()

    def show_preview(self):
        with VideoFileClip(self.filepath) as clip:
            frame = clip.get_frame(0)
            self.preview_frame = Image.fromarray(frame)
        self.update_preview(self.angle_var.get())

    def update_preview(self, angle):
        if self.preview_frame:
            rotated_image = self.preview_frame.rotate(int(angle), expand=True)
            tk_image = ImageTk.PhotoImage(rotated_image)
            self.preview_label.configure(image=tk_image)
            self.preview_label.image = tk_image

    def rotate_video(self):
        if not self.filepath:
            messagebox.showinfo("Video Rotator", "Please select a video first.")
            return
        angle = int(self.angle_var.get())
        original_path = self.filepath  # Preserve original path
        if not self.overwrite.get():
            moved_path = self.move_original_to_unrotated()
            if moved_path is None:  # If moving the file failed
                return
            self.filepath = moved_path  # Update filepath for the operation

        with VideoFileClip(self.filepath) as clip:
            rotated_clip = clip.rotate(angle)
            save_path = original_path if self.overwrite.get() else self.get_incremented_filename(original_path)
            rotated_clip.write_videofile(save_path, codec="libx264", audio_codec="aac")

        messagebox.showinfo("Video Rotator", f"Video rotated successfully and saved as {os.path.basename(save_path)}.")

    def move_original_to_unrotated(self):
        unrotated_dir = os.path.join(os.path.dirname(self.filepath), "unrotated")
        if not os.path.exists(unrotated_dir):
            os.makedirs(unrotated_dir)
        original_filename = os.path.basename(self.filepath)
        unrotated_path = os.path.join(unrotated_dir, original_filename)

        moved = False
        attempts = 0
        while not moved and attempts < 5:
            try:
                shutil.move(self.filepath, unrotated_path)
                moved = True
            except PermissionError:
                time.sleep(1)
                attempts += 1

        if not moved:
            messagebox.showerror("Error", "Failed to move the original file. It might be in use.")
            return None
        return unrotated_path

    def get_incremented_filename(self, filepath):
        base_path, extension = os.path.splitext(filepath)
        match = re.search(r"(.*)_(\d+)$", base_path)
        if match:
            base_path = match.group(1)
            counter = int(match.group(2)) + 1
        else:
            counter = 1
        new_filepath = f"{base_path}_{counter}{extension}"
        while os.path.exists(new_filepath):
            counter += 1
            new_filepath = f"{base_path}_{counter}{extension}"
        return new_filepath

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoRotatorApp(root)
    root.mainloop()
