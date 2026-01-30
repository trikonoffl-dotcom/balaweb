import fitz
import os
import datetime
from PIL import Image

def generate_id_card_pdf(
    first_name, last_name, title, id_number, doj, 
    photo_bytes, emergency_no, blood_group, office_address,
    scale=1.0, x_offset=0, y_offset=0
):
    """Generates an ID Card PDF and returns bytes."""
    try:
        # Locate Template
        possible_paths = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Templates", "idcard", "id_card_empty.pdf"),
            os.path.join(os.getcwd(), "Templates", "idcard", "id_card_empty.pdf"),
            r"C:\Users\pabal\Documents\Businesscard\Templates\idcard\id_card_empty.pdf"
        ]
        template_path = next((p for p in possible_paths if os.path.exists(p)), None)
        
        if not template_path:
            raise FileNotFoundError("ID Card Template not found.")

        doc = fitz.open(template_path)
        
        # --- FONT REGISTRATION ---
        possible_font_dirs = [
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts", "Rubik", "static"),
            os.path.join(os.getcwd(), "fonts", "Rubik", "static"),
            r"C:\Users\pabal\Documents\Businesscard\fonts\Rubik\static"
        ]
        font_dir = next((d for d in possible_font_dirs if os.path.exists(d)), None)
        
        fonts_map = {
            "ru-bold": "Rubik-Bold.ttf",
            "ru-reg": "Rubik-Regular.ttf",
            "ru-semi": "Rubik-SemiBold.ttf",
            "ru-italic": "Rubik-Italic.ttf",
            "ru-light": "Rubik-Light.ttf"
        }
        
        loaded_fonts = []
        if font_dir:
            for name, filename in fonts_map.items():
                path = os.path.join(font_dir, filename)
                if os.path.exists(path):
                    try:
                        for page in doc:
                            page.insert_font(fontname=name, fontfile=path)
                        loaded_fonts.append(name)
                    except:
                        pass
        
        def get_font(desired, fallback="helv"):
            return desired if desired in loaded_fonts else fallback

        blue_text = (18/255, 34/255, 66/255)
        white_text = (1, 1, 1)
        
        # Front Text
        page0 = doc[0]
        page0.insert_text((14.8, 148), first_name.upper(), fontsize=15, fontname=get_font("ru-bold"), color=blue_text)
        page0.insert_text((15.0, 168), last_name.upper(), fontsize=11, fontname=get_font("ru-light"), color=blue_text)
        page0.insert_text((15.5, 183), title, fontsize=8, fontname=get_font("ru-reg"), color=blue_text)
        
        # Handling Date object vs string
        if isinstance(doj, str):
             # Try parsing if string, or just use it
             date_str = doj
        else:
             date_str = doj.strftime("%d-%m-%Y")
             
        page0.insert_text((15.1, 196), f"D.O.J:  {date_str}", fontsize=8, fontname=get_font("ru-bold"), color=blue_text)
        page0.insert_text((15.6, 226), f"ID Number: {id_number}", fontsize=10, fontname=get_font("ru-reg"), color=white_text)
        
        # Photo Placement
        base_x, base_y = 11 + x_offset, 28.5 + y_offset
        base_w, base_h = 95 * scale, 98 * scale
        
        adj_x = base_x - (base_w - 95) / 2
        adj_y = base_y - (base_h - 98) / 2
        
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
    """Generates an ID Card Preview (Front Side PNG) and returns bytes."""
    try:
        # Reuse the logic or refactor. For safety, let's copy the needed parts 
        # or better: refactor the common drawing logic into `_draw_id_card(doc, ...)`
        # But to minimize regression risk during migration, I'll replicate the drawing steps for now
        # or just call generate_id_card_pdf but return pixmap.
        
        # Strategy: Use the same PDF gen, but load page 0 and get pixmap.
        # This is slightly inefficient (generating full PDF then rendering) but safe.
        
        pdf_bytes = generate_id_card_pdf(
             first_name, last_name, title, id_number, doj, 
             photo_bytes, emergency_no, blood_group, office_address,
             scale, x_offset, y_offset
        )
        
        if not pdf_bytes:
             return None
             
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page = doc[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # 2x Zoom for clear preview
        return pix.tobytes("png")

    except Exception as e:
        print(f"Preview Generation Error: {e}")
        return None
