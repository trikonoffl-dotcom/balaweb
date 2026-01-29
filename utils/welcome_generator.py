import fitz
import os
import io
import datetime
from PIL import Image, ImageDraw, ImageOps

def get_date_suffix(day):
    if 4 <= day <= 20 or 24 <= day <= 30:
        return "th"
    else:
        return ["st", "nd", "rd"][day % 10 - 1]

def make_rounded(image, width, height, radius):
    image = ImageOps.fit(image, (int(width), int(height)), method=Image.Resampling.LANCZOS)
    mask = Image.new('L', (int(width), int(height)), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), (int(width), int(height))], radius=radius, fill=255)
    rounded_img = Image.new('RGBA', (int(width), int(height)), (0, 0, 0, 0))
    rounded_img.paste(image, (0, 0), mask)
    return rounded_img

def generate_welcome_image(
    first_name, last_name, title, doj_date, photo_bytes
):
    """Generates Welcome Aboard JPG bytes."""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Locate Template
        possible_paths = [
            os.path.join(current_dir, "..", "Templates", "welcome aboard - Without name.pdf"),
            r"C:\Users\pabal\Documents\Businesscard\Templates\welcome aboard - Without name.pdf"
        ]
        template_path = next((p for p in possible_paths if os.path.exists(p)), None)
        
        if not template_path:
            raise FileNotFoundError("Welcome Template not found.")

        doc = fitz.open(template_path)
        page = doc[0]
        
        # Font Setup
        font_base = os.path.join(current_dir, "..")
        if not os.path.exists(os.path.join(font_base, "fonts", "Poppins")):
            # Try alt path
            font_base = r"C:\Users\pabal\Documents\Businesscard"
            
        font_bold = os.path.join(font_base, "fonts", "Poppins", "Poppins-Bold.ttf")
        font_reg = os.path.join(font_base, "fonts", "Poppins", "Poppins-Regular.ttf")
        
        # Fallback to absolute if relative fails
        if not os.path.exists(font_bold):
             font_bold = r"C:\Users\pabal\Documents\Businesscard\fonts\Poppins\Poppins-Bold.ttf"
             font_reg = r"C:\Users\pabal\Documents\Businesscard\fonts\Poppins\Poppins-Regular.ttf"

        if os.path.exists(font_bold):
            page.insert_font(fontname="pop-bold", fontfile=font_bold)
            page.insert_font(fontname="pop-reg", fontfile=font_reg)
        else:
             # Just use default if missing
             pass
        
        text_color = (1, 1, 1)

        # Photo
        user_x, user_y = 71, 340
        user_w, user_h = 421.978, 502.045
        user_r = 28.492
        
        original_img = Image.open(io.BytesIO(photo_bytes))
        rounded_img = make_rounded(original_img, user_w, user_h, user_r)
        
        img_byte_arr = io.BytesIO()
        rounded_img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        photo_rect = fitz.Rect(user_x, user_y, user_x + user_w, user_y + user_h)
        page.insert_image(photo_rect, stream=img_byte_arr)
        
        # Text
        suffix = get_date_suffix(doj_date.day)
        date_str = f"{doj_date.day}{suffix} {doj_date.strftime('%b %Y')}"
        
        # Use simple fonts if custom failed
        bold_font = "pop-bold" if os.path.exists(font_bold) else "helv"
        reg_font = "pop-reg" if os.path.exists(font_reg) else "helv"

        page.insert_text((563, 500), first_name, fontsize=77, fontname=bold_font, color=text_color)
        page.insert_text((563, 580), last_name, fontsize=77, fontname=bold_font, color=text_color)
        page.insert_text((563, 640), title, fontsize=25, fontname=reg_font, color=text_color)
        page.insert_text((563, 700), date_str, fontsize=26, fontname=bold_font, color=text_color)
        
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        return pix.tobytes("jpg")

    except Exception as e:
        print(f"Welcome Gen Error: {e}")
        return None
