import fitz
import os
import io
import datetime
from PIL import Image, ImageDraw, ImageOps
from utils.settings_manager import load_settings, resolve_asset_path

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
        
        settings = load_settings().get("welcome_aboard", {})
        
        # Locate Template
        template_val = settings.get("template_path", "welcome aboard - Without name.pdf")
        template_path = resolve_asset_path(template_val, category="template")
        
        if not template_path:
            template_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Templates", "welcome aboard - Without name.pdf")
            
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Welcome Template not found: {template_val}")

        doc = fitz.open(template_path)
        page = doc[0]
        
        # Font Setup - Use Rubik as Poppins is missing or problematic
        font_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts", "Rubik", "static")
        
        font_bold = os.path.join(font_dir, "Rubik-Bold.ttf")
        font_light = os.path.join(font_dir, "Rubik-Light.ttf")
        font_reg = os.path.join(font_dir, "Rubik-Regular.ttf")

        if os.path.exists(font_bold):
            page.insert_font(fontname="pop-bold", fontfile=font_bold)
            page.insert_font(fontname="pop-light", fontfile=font_light)
            page.insert_font(fontname="pop-reg", fontfile=font_reg)
        else:
             pass
        
        text_color = (1, 1, 1)

        # Photo
        p_settings = settings.get("photo_rect", [71, 340, 421.978, 502.045, 28.492])
        user_x, user_y = p_settings[0], p_settings[1]
        user_w, user_h = p_settings[2], p_settings[3]
        user_r = p_settings[4] if len(p_settings) > 4 else 28.492
        
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
        light_font = "pop-light" if os.path.exists(font_light) else "helv"
        reg_font = "pop-reg" if os.path.exists(font_reg) else "helv"

        page.insert_text(settings.get("first_name_pos", (563, 500)), first_name, fontsize=77, fontname=bold_font, color=text_color)
        page.insert_text(settings.get("last_name_pos", (563, 580)), last_name, fontsize=77, fontname=light_font, color=text_color)
        page.insert_text(settings.get("title_pos", (563, 640)), title, fontsize=25, fontname=reg_font, color=text_color)
        page.insert_text(settings.get("date_pos", (563, 700)), date_str, fontsize=26, fontname=bold_font, color=text_color)
        
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        return pix.tobytes("jpg")

    except Exception as e:
        print(f"Welcome Gen Error: {e}")
        return None
