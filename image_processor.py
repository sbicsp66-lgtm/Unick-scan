from PIL import Image, ImageOps, ImageEnhance
from fpdf import FPDF
import os

class ImageProcessor:
    def __init__(self):
        pass

    def apply_bw(self, img_path):
        img = Image.open(img_path)
        # Black & white conversion
        bw = img.convert('L').point(lambda x: 0 if x < 128 else 255, '1')
        bw.save(img_path)
        return img_path

    def apply_grayscale(self, img_path):
        img = Image.open(img_path)
        gray = ImageOps.grayscale(img)
        gray.save(img_path)
        return img_path

    def rotate_image(self, img_path, angle=90):
        img = Image.open(img_path)
        rotated = img.rotate(angle, expand=True)
        rotated.save(img_path)
        return img_path

    def adjust_brightness(self, img_path, factor=1.2):
        img = Image.open(img_path)
        enhancer = ImageEnhance.Brightness(img)
        enhanced = enhancer.enhance(factor) # 1.0 means original, >1 means brighter
        enhanced.save(img_path)
        return img_path

    def save_to_pdf(self, image_paths, pdf_name="Scanned_Document.pdf"):
        if not image_paths:
            return False
            
        pdf = FPDF()
        for img_path in image_paths:
            img = Image.open(img_path)
            
            # Convert to RGB if not already (PDF doesn't support some modes directly)
            if img.mode != 'RGB':
                img = img.convert('RGB')
                temp_rgb = "temp_pdf_img.jpg"
                img.save(temp_rgb)
                img_to_add = temp_rgb
            else:
                img_to_add = img_path
                
            width, height = img.size
            w_mm = width * 0.264583
            h_mm = height * 0.264583
            
            pdf.add_page(format=(w_mm, h_mm))
            pdf.image(img_to_add, 0, 0, w_mm, h_mm)
            
            if img.mode != 'RGB' and os.path.exists(temp_rgb):
                os.remove(temp_rgb)
                
        pdf.output(pdf_name, "F")
        return True