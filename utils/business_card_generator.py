import fitz
import qrcode
from PIL import Image
import io
import os

def create_vcard_qr(data):
    vcard_data = f"""BEGIN:VCARD
VERSION:3.0
N:{data['last_name']};{data['first_name']};;;
FN:{data['first_name']} {data['last_name']}
ORG:
TITLE:{data['title']}
TEL;TYPE=WORK,VOICE:{data['phone_office']}
TEL;TYPE=CELL,VOICE:{data['phone_mobile']}
EMAIL;TYPE=PREF,INTERNET:{data['email']}
URL:{data['website']}
ADR;TYPE=WORK:;;{data['address']};;;;
END:VCARD"""
    
    qr = qrcode.QRCode(box_size=10, border=1)
    qr.add_data(vcard_data)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    
    # Convert to bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr.getvalue()

def _draw_business_card_details(page, template_style, data, font_base):
    """Internal helper to draw details onto a page."""
    text_color = (0, 0, 0)
    
    if template_style == "Trikon":
        font_reg = os.path.join(font_base, "Poppins", "Poppins-Regular.ttf")
        font_bold = os.path.join(font_base, "Poppins", "Poppins-Bold.ttf")
        font_med = os.path.join(font_base, "Poppins", "Poppins-Medium.ttf")
        font_light = os.path.join(font_base, "Poppins", "Poppins-Light.ttf")
        
        try:
             with open(font_reg, "rb") as f: fb_reg = f.read()
             page.insert_font(fontname="pop-reg", fontbuffer=fb_reg)
             with open(font_bold, "rb") as f: fb_bold = f.read()
             page.insert_font(fontname="pop-bold", fontbuffer=fb_bold)
             with open(font_med, "rb") as f: fb_med = f.read()
             page.insert_font(fontname="pop-med", fontbuffer=fb_med)
             with open(font_light, "rb") as f: fb_light = f.read()
             page.insert_font(fontname="pop-light", fontbuffer=fb_light)
             t_bold_name, t_light_name, t_reg_name, t_med_name = "pop-bold", "pop-light", "pop-reg", "pop-med"
        except:
            t_bold_name = t_light_name = t_reg_name = t_med_name = "helv"

        first_name_upper = data['first_name'].upper()
        last_name_upper = data['last_name'].upper()
        f_size = 11
        first_w = fitz.get_text_length(first_name_upper + " ", fontname=t_bold_name, fontsize=f_size)
        
        page.insert_text((21.15, 26), first_name_upper, fontsize=f_size, fontname=t_bold_name, color=text_color)
        page.insert_text((21.15 + first_w, 26), last_name_upper, fontsize=f_size, fontname=t_light_name, color=text_color)
        page.insert_text((21.15, 36), data['title'], fontsize=6, fontname=t_reg_name, color=text_color)
        page.insert_text((34, 56), data['address_line1'], fontsize=6, fontname=t_med_name, color=text_color)
        page.insert_text((34, 64), data['address_line2'], fontsize=6, fontname=t_med_name, color=text_color)
        
        start_y = 75
        gap = 11
        page.insert_text((34, start_y), data['phone_mobile'], fontsize=6, fontname=t_med_name, color=text_color)
        page.insert_text((34, start_y + gap), data['email'], fontsize=6, fontname=t_med_name, color=text_color)
        page.insert_text((34, start_y + 2*gap), data['phone_office'], fontsize=6, fontname=t_med_name, color=text_color)
        page.insert_text((34, start_y + 3*gap), data['website'], fontsize=6, fontname=t_med_name, color=text_color)
        qr_rect = fitz.Rect(160.62, 39.29, 160.62 + 82.32, 39.29 + 82.32)
        page.insert_image(qr_rect, stream=create_vcard_qr(data))
    
    elif template_style == "Metaweb":
        font_reg = os.path.join(font_base, "Montserrat", "static", "Montserrat-Regular.ttf")
        font_bold = os.path.join(font_base, "Montserrat", "static", "Montserrat-Bold.ttf")
        font_light = os.path.join(font_base, "Montserrat", "static", "Montserrat-Light.ttf")

        try:
            page.insert_font(fontname="mont-reg", fontfile=font_reg)
            page.insert_font(fontname="mont-bold", fontfile=font_bold)
            page.insert_font(fontname="mont-light", fontfile=font_light)
            f_bold_name, f_light_name, f_reg_name = "mont-bold", "mont-light", "mont-reg"
            fn_width = fitz.get_text_length(data['first_name'] + " ", fontname=f_bold_name, fontsize=12)
        except:
            f_bold_name = f_light_name = f_reg_name = "helv"
            fn_width = len(data['first_name']) * 7

        page.insert_text((18, 38), f"{data['first_name']}", fontsize=12, fontname=f_bold_name, color=text_color) 
        page.insert_text((18 + fn_width, 38), f"{data['last_name']}", fontsize=12, fontname=f_light_name, color=text_color)
        page.insert_text((19, 50), data['title'], fontsize=6, fontname=f_reg_name, color=text_color)
        page.insert_text((30, 74), data['phone_mobile'], fontsize=5, fontname=f_reg_name, color=text_color)
        page.insert_text((30, 88), data['phone_office'], fontsize=5, fontname=f_reg_name, color=text_color)
        page.insert_text((30, 103), data['email'], fontsize=5, fontname=f_reg_name, color=text_color)
        page.insert_text((30, 116), data['website'], fontsize=5, fontname=f_reg_name, color=text_color)
        page.insert_text((30, 129), data['address_line1'], fontsize=5, fontname=f_reg_name, color=text_color)
        page.insert_text((30, 137), data['address_line2'], fontsize=5, fontname=f_reg_name, color=text_color)
        qr_rect = fitz.Rect(179.18, 74.31, 179.18 + 67.00, 74.31 + 67.00)
        page.insert_image(qr_rect, stream=create_vcard_qr(data))

def generate_business_card_pdf(template_style, data):
    """Generates a Business Card PDF."""
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        templates_dir = os.path.join(base_dir, "Templates")
        pdf_name = "Name_Trikon.pdf" if template_style == "Trikon" else "Name_MetaWeb.pdf"
        pdf_path = os.path.join(templates_dir, pdf_name)
        
        if not os.path.exists(pdf_path):
             pdf_path = os.path.join(templates_dir, pdf_name)
        if not os.path.exists(pdf_path): raise FileNotFoundError(f"Template missing: {pdf_path}")

        doc = fitz.open(pdf_path)
        font_base = base_dir
        
        _draw_business_card_details(doc[1], template_style, data, font_base)
        return doc.write()
    except Exception as e:
        print(f"Business Card Gen Error: {e}")
        return None

def generate_business_card_preview(template_style, data):
    """Returns PNG preview of the card - optimized directly from doc."""
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        templates_dir = os.path.join(base_dir, "Templates")
        pdf_name = "Name_Trikon.pdf" if template_style == "Trikon" else "Name_MetaWeb.pdf"
        pdf_path = os.path.join(templates_dir, pdf_name)
        
        if not os.path.exists(pdf_path):
             pdf_path = os.path.join(templates_dir, pdf_name)
        if not os.path.exists(pdf_path): return None

        doc = fitz.open(pdf_path)
        font_base = base_dir
        
        page = doc[1]
        _draw_business_card_details(page, template_style, data, font_base)
        
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        return pix.tobytes("png")
    except Exception as e:
        print(f"Business Card Preview Error: {e}")
        return None
