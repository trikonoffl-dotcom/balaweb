import fitz
import os
import datetime
from PIL import Image
from utils.settings_manager import load_settings, resolve_asset_path

# Global font cache for the session
_CACHED_FONTS = {}

def _get_fonts(doc):
    """Registers and returns font map for the document."""
    possible_font_dirs = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts", "Rubik", "static"),
        os.path.join(os.getcwd(), "fonts", "Rubik", "static")
    ]
    font_dir = next((d for d in possible_font_dirs if os.path.exists(d)), None)
    
    fonts_map = {
        "ru-bold": "Rubik-Bold.ttf",
        "ru-reg": "Rubik-Regular.ttf",
        "ru-semi": "Rubik-SemiBold.ttf",
        "ru-italic": "Rubik-Italic.ttf",
        "ru-light": "Rubik-Light.ttf"
    }
    
    loaded = []
    if font_dir:
        for name, filename in fonts_map.items():
            path = os.path.join(font_dir, filename)
            if os.path.exists(path):
                try:
                    for page in doc:
                        page.insert_font(fontname=name, fontfile=path)
                    loaded.append(name)
                except:
                    pass
    return loaded

def generate_id_card_pdf(
    first_name, last_name, title, id_number, doj, 
    photo_bytes, emergency_no, blood_group, office_address,
    scale=1.0, x_offset=0, y_offset=0
):
    """Generates an ID Card PDF and returns bytes."""
    try:
        settings = load_settings().get("id_card", {})
        template_val = settings.get("template_path", "Name_Trikon.pdf")
        
        template_path = resolve_asset_path(template_val, category="template")
        if not template_path: 
            # Fallback to relative if resolution fails
            template_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Templates", "Name_Trikon.pdf")
            
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found: {template_val}")

        doc = fitz.open(template_path)
        loaded_fonts = _get_fonts(doc)
        
        def get_font(desired, fallback="helv"):
            return desired if desired in loaded_fonts else fallback

        blue_text = (18/255, 34/255, 66/255)
        white_text = (1, 1, 1)
        
        settings = load_settings().get("id_card", {})
        
        # Front Side
        page0 = doc[0]
        page0.insert_text(settings.get("first_name_pos", (14.8, 148)), first_name.upper(), fontsize=15, fontname=get_font("ru-bold"), color=blue_text)
        page0.insert_text(settings.get("last_name_pos", (15.0, 163)), last_name.upper(), fontsize=11, fontname=get_font("ru-light"), color=blue_text)
        page0.insert_text(settings.get("title_pos", (15.5, 183)), title, fontsize=8, fontname=get_font("ru-reg"), color=blue_text)
        
        date_str = doj if isinstance(doj, str) else doj.strftime("%d-%m-%Y")
             
        page0.insert_text(settings.get("doj_pos", (15.1, 196)), f"D.O.J:  {date_str}", fontsize=8, fontname=get_font("ru-bold"), color=blue_text)
        page0.insert_text(settings.get("id_number_pos", (15.6, 226)), f"ID Number: {id_number}", fontsize=10, fontname=get_font("ru-reg"), color=white_text)
        
        # Photo
        base_pos = settings.get("photo_pos", (11, 35.2))
        base_size = settings.get("photo_size", (95, 98))
        
        base_x, base_y = base_pos[0] + x_offset, base_pos[1] + y_offset
        base_w, base_h = base_size[0] * scale, base_size[1] * scale
        adj_x = base_x - (base_w - base_size[0]) / 2
        adj_y = base_y - (base_h - base_size[1]) / 2
        photo_rect = fitz.Rect(adj_x, adj_y, adj_x + base_w, adj_y + base_h)
        page0.insert_image(photo_rect, stream=photo_bytes)
        
        # Back Side
        if len(doc) > 1:
            page1 = doc[1]
            page1.insert_text((20, 93), f"Emergency Number: {emergency_no}", fontsize=7, fontname=get_font("ru-reg"), color=white_text)
            page1.insert_text((49, 106), f"Blood Group: {blood_group}", fontsize=7, fontname=get_font("ru-reg"), color=white_text)
            addr_rect = fitz.Rect(0, 174, page1.rect.width, page1.rect.height)
            page1.insert_textbox(addr_rect, office_address, fontsize=6.5, fontname=get_font("ru-reg"), color=white_text, align=1)
            
        return doc.write()

    except Exception as e:
        print(f"PDF Generation Error: {e}")
        return None

def generate_id_card_preview(
    first_name, last_name, title, id_number, doj, 
    photo_bytes, emergency_no, blood_group, office_address,
    scale=1.0, x_offset=0, y_offset=0
):
    """Generates an ID Card Preview (Front PNG) directly without full PDF write."""
    try:
        settings = load_settings().get("id_card", {})
        template_val = settings.get("template_path", "Name_Trikon.pdf")
        
        template_path = resolve_asset_path(template_val, category="template")
        if not template_path: 
            template_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Templates", "Name_Trikon.pdf")
            
        if not os.path.exists(template_path): 
            return None

        doc = fitz.open(template_path)
        loaded_fonts = _get_fonts(doc)
        
        def get_font(desired, fallback="helv"):
            return desired if desired in loaded_fonts else fallback

        blue_text = (18/255, 34/255, 66/255)
        white_text = (1, 1, 1)
        
        settings = load_settings().get("id_card", {})
        
        page = doc[0]
        page.insert_text(settings.get("first_name_pos", (14.8, 148)), first_name.upper(), fontsize=15, fontname=get_font("ru-bold"), color=blue_text)
        page.insert_text(settings.get("last_name_pos", (15.0, 163)), last_name.upper(), fontsize=11, fontname=get_font("ru-light"), color=blue_text)
        page.insert_text(settings.get("title_pos", (15.5, 183)), title, fontsize=8, fontname=get_font("ru-reg"), color=blue_text)
        
        date_str = doj if isinstance(doj, str) else doj.strftime("%d-%m-%Y")
        page.insert_text(settings.get("doj_pos", (15.1, 196)), f"D.O.J:  {date_str}", fontsize=8, fontname=get_font("ru-bold"), color=blue_text)
        page.insert_text(settings.get("id_number_pos", (15.6, 226)), f"ID Number: {id_number}", fontsize=10, fontname=get_font("ru-reg"), color=white_text)
        
        base_pos = settings.get("photo_pos", (11, 35.2))
        base_size = settings.get("photo_size", (95, 98))
        
        base_x, base_y = base_pos[0] + x_offset, base_pos[1] + y_offset
        base_w, base_h = base_size[0] * scale, base_size[1] * scale
        adj_x = base_x - (base_w - base_size[0]) / 2
        adj_y = base_y - (base_h - base_size[1]) / 2
        photo_rect = fitz.Rect(adj_x, adj_y, adj_x + base_w, adj_y + base_h)
        page.insert_image(photo_rect, stream=photo_bytes)
        
        # KEY OPTIMIZATION: Render pixmap directly from the modified document model 
        # without calling doc.write() or re-opening.
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) 
        return pix.tobytes("png")

    except Exception as e:
        print(f"Preview Generation Error: {e}")
        return None
