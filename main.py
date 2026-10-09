import os
from PIL import Image
import customtkinter as ctk
from tkinter import messagebox, filedialog
from license_manager import LicenseManager
from scanner_engine import ScannerEngine
from image_processor import ImageProcessor

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class UnickScannerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Unick Scanner")
        self.geometry("1000x700")

        self.scanner = ScannerEngine()
        self.processor = ImageProcessor()
        self.scanned_images = []
        self.current_image_index = -1

        self.license_manager = LicenseManager()
        is_active, status = self.license_manager.check_trial_status()

        if not is_active:
            self.show_expired_screen()
        else:
            self.show_main_scanner_ui(status)

    def show_expired_screen(self):
        machine_id = self.license_manager.get_machine_id()
        
        label = ctk.CTkLabel(self, text="TRIAL EXPIRED", font=("Arial", 30, "bold"), text_color="red")
        label.pack(pady=60)
        
        info = ctk.CTkLabel(self, text="Please contact Admin to purchase a License Key.", font=("Arial", 16))
        info.pack(pady=10)

        # Machine ID এবং Copy বাটন রাখার জন্য একটি ফ্রেম
        id_frame = ctk.CTkFrame(self, fg_color="transparent")
        id_frame.pack(pady=15)

        id_label = ctk.CTkLabel(id_frame, text=f"Machine ID: {machine_id}", font=("Arial", 16, "bold"))
        id_label.pack(side="left", padx=10)

        btn_copy = ctk.CTkButton(id_frame, text="Copy", width=60, command=lambda: self.copy_to_clipboard(machine_id))
        btn_copy.pack(side="left")

        self.entry_key = ctk.CTkEntry(self, placeholder_text="Enter License Key", width=300)
        self.entry_key.pack(pady=20)

        btn_activate = ctk.CTkButton(self, text="Activate", font=("Arial", 14), command=self.activate_software)
        btn_activate.pack()

    def copy_to_clipboard(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()
        messagebox.showinfo("Copied", "Machine ID copied to clipboard!")

    def activate_software(self):
        key = self.entry_key.get()
        if not key:
            messagebox.showwarning("Warning", "Please enter a license key.")
            return
            
        success, msg = self.license_manager.activate_license(key)
        
        if success:
            messagebox.showinfo("Success", msg)
            for widget in self.winfo_children():
                widget.destroy()
            self.show_main_scanner_ui("Activated")
        else:
            messagebox.showerror("Error", msg)

    def show_main_scanner_ui(self, status):
        # Top Bar
        top_frame = ctk.CTkFrame(self)
        top_frame.pack(fill="x", padx=10, pady=10)

        title = ctk.CTkLabel(top_frame, text="Unick Scanner", font=("Arial", 20, "bold"))
        title.pack(side="left", padx=10)

        trial_text = f"Trial Days Left: {status}" if isinstance(status, int) else "License: ACTIVE"
        trial_label = ctk.CTkLabel(top_frame, text=trial_text, text_color="green" if isinstance(status, str) else "orange")
        trial_label.pack(side="right", padx=10)

        # Left Panel (Scan Controls)
        left_frame = ctk.CTkFrame(self, width=200)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)

        btn_detect = ctk.CTkButton(left_frame, text="Detect Scanner", command=self.detect_scanners)
        btn_detect.pack(pady=20, padx=20)

        btn_scan = ctk.CTkButton(left_frame, text="Start Scan", fg_color="green", command=self.start_scan)
        btn_scan.pack(pady=10, padx=20)

        btn_save = ctk.CTkButton(left_frame, text="Save to PDF", command=self.save_pdf)
        btn_save.pack(pady=30, padx=20)

        # Right Panel (Preview & Edit)
        right_frame = ctk.CTkFrame(self)
        right_frame.pack(side="right", expand=True, fill="both", padx=10, pady=10)
        
        self.preview_label = ctk.CTkLabel(right_frame, text="Preview Area", text_color="gray")
        self.preview_label.pack(expand=True, pady=10)

        # Edit Tools Panel (Under Preview)
        edit_frame = ctk.CTkFrame(right_frame)
        edit_frame.pack(fill="x", padx=10, pady=10)

        btn_rotate = ctk.CTkButton(edit_frame, text="Rotate", width=80, command=self.rotate_current)
        btn_rotate.pack(side="left", padx=5)

        btn_bw = ctk.CTkButton(edit_frame, text="B&W", width=80, command=self.bw_current)
        btn_bw.pack(side="left", padx=5)

        btn_gray = ctk.CTkButton(edit_frame, text="Grayscale", width=80, command=self.gray_current)
        btn_gray.pack(side="left", padx=5)
        
        btn_bright = ctk.CTkButton(edit_frame, text="Brightness+", width=80, command=self.bright_current)
        btn_bright.pack(side="left", padx=5)

        btn_delete = ctk.CTkButton(edit_frame, text="Remove Page", width=80, fg_color="red", command=self.delete_current)
        btn_delete.pack(side="right", padx=5)

    # --- Scanner & PDF Functions ---
    def detect_scanners(self):
        scanners = self.scanner.get_scanners()
        if scanners:
            messagebox.showinfo("Scanner Detected", f"Available Scanners:\n{', '.join(scanners)}")
        else:
            messagebox.showwarning("No Scanner", "No scanner found. Please check connection.")

    def start_scan(self):
        save_path = f"scan_page_{len(self.scanned_images) + 1}.jpg"
        success, result = self.scanner.scan_document(save_path)
        
        if success:
            self.scanned_images.append(result)
            self.current_image_index = len(self.scanned_images) - 1
            self.update_preview()
        else:
            messagebox.showerror("Scan Error", result)

    def save_pdf(self):
        if not self.scanned_images:
            messagebox.showwarning("Warning", "No scanned pages to save.")
            return
            
        pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if pdf_path:
            if self.processor.save_to_pdf(self.scanned_images, pdf_path):
                messagebox.showinfo("Success", "PDF saved successfully!")
                self.scanned_images.clear()
                self.current_image_index = -1
                self.preview_label.configure(image=None, text="Ready for next scan")
            else:
                messagebox.showerror("Error", "Failed to save PDF.")

    # --- Editing Functions ---
    def rotate_current(self):
        if self.current_image_index >= 0:
            img_path = self.scanned_images[self.current_image_index]
            self.processor.rotate_image(img_path, angle=-90)
            self.update_preview()

    def bw_current(self):
        if self.current_image_index >= 0:
            img_path = self.scanned_images[self.current_image_index]
            self.processor.apply_bw(img_path)
            self.update_preview()

    def gray_current(self):
        if self.current_image_index >= 0:
            img_path = self.scanned_images[self.current_image_index]
            self.processor.apply_grayscale(img_path)
            self.update_preview()

    def bright_current(self):
        if self.current_image_index >= 0:
            img_path = self.scanned_images[self.current_image_index]
            self.processor.adjust_brightness(img_path, factor=1.2)
            self.update_preview()

    def delete_current(self):
        if self.current_image_index >= 0:
            img_path = self.scanned_images[self.current_image_index]
            if os.path.exists(img_path):
                os.remove(img_path)
            self.scanned_images.pop(self.current_image_index)
            if self.scanned_images:
                self.current_image_index = len(self.scanned_images) - 1
                self.update_preview()
            else:
                self.current_image_index = -1
                self.preview_label.configure(image=None, text="Preview Area")

    def update_preview(self):
        if self.current_image_index >= 0:
            img_path = self.scanned_images[self.current_image_index]
            try:
                pil_image = Image.open(img_path)
                pil_image.thumbnail((500, 650))
                ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=pil_image.size)
                
                self.preview_label.configure(image=ctk_image, text="")
                self.preview_label.image = ctk_image
            except Exception as e:
                print("Preview Error:", e)

if __name__ == "__main__":
    app = UnickScannerApp()
    app.mainloop()