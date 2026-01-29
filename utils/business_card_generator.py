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

def generate_business_card_pdf(template_style, data):
    """
    Generates a Business Card PDF.
    template_style: "Trikon" or "Metaweb"
    data: dict containing user details
    """
    try:
        # Resolve Template Path
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        templates_dir = os.path.join(base_dir, "Templates")
        
        if template_style == "Trikon":
            pdf_path = os.path.join(templates_dir, "Name_Trikon.pdf")
        else:
            pdf_path = os.path.join(templates_dir, "Name_MetaWeb.pdf")
            
        # Fallback to hardcoded absolute path (legacy support)
        if not os.path.exists(pdf_path):
             local_fixed_path = r"C:\Users\pabal\Documents\Businesscard\Templates"
             if template_style == "Trikon":
                pdf_path = os.path.join(local_fixed_path, "Name_Trikon.pdf")
             else:
                pdf_path = os.path.join(local_fixed_path, "Name_MetaWeb.pdf")

        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Template not found at: {pdf_path}")

        doc = fitz.open(pdf_path)
        page = doc[1]  # Page 2 has the details
        
        text_color = (0, 0, 0)
        
        # Font Paths - Resolve relative to project root
        font_base = r"C:\Users\pabal\Documents\Businesscard"
        if not os.path.exists(os.path.join(font_base, "fonts")):
             font_base = base_dir # Fallback to relative parent

        if template_style == "Trikon":
            font_reg = os.path.join(font_base, "fonts", "Poppins", "Poppins-Regular.ttf")
            font_bold = os.path.join(font_base, "fonts", "Poppins", "Poppins-Bold.ttf")
            font_med = os.path.join(font_base, "fonts", "Poppins", "Poppins-Medium.ttf")
            
            # Load Fonts
            try:
                 with open(font_reg, "rb") as f: fb_reg = f.read()
                 ret = page.insert_font(fontname="pop-reg", fontbuffer=fb_reg)
                 t_reg_name = ret if isinstance(ret, str) else "pop-reg"
                 
                 with open(font_bold, "rb") as f: fb_bold = f.read()
                 ret = page.insert_font(fontname="pop-bold", fontbuffer=fb_bold)
                 t_bold_name = ret if isinstance(ret, str) else "pop-bold"
                 
                 with open(font_med, "rb") as f: fb_med = f.read()
                 ret = page.insert_font(fontname="pop-med", fontbuffer=fb_med)
                 t_med_name = ret if isinstance(ret, str) else "pop-med"
            except Exception as e:
                # Fallback to helv if fonts missing
                t_reg_name = "helv"
                t_bold_name = "helv"
                t_med_name = "helv"

            # Insert Text
            page.insert_text((21.15, 26), f"{data['first_name']} {data['last_name']}".upper(), fontsize=11, fontname=t_bold_name, color=text_color)
            page.insert_text((21.15, 36), data['title'], fontsize=6, fontname=t_reg_name, color=text_color)
            
            page.insert_text((34, 56), data['address_line1'], fontsize=6, fontname=t_med_name, color=text_color)
            page.insert_text((34, 64), data['address_line2'], fontsize=6, fontname=t_med_name, color=text_color)
            
            start_y = 75
            gap = 11
            page.insert_text((34, start_y), data['phone_mobile'], fontsize=6, fontname=t_med_name, color=text_color)
            page.insert_text((34, start_y + gap), data['email'], fontsize=6, fontname=t_med_name, color=text_color)
            page.insert_text((34, start_y + 2*gap), data['phone_office'], fontsize=6, fontname=t_med_name, color=text_color)
            page.insert_text((34, start_y + 3*gap), data['website'], fontsize=6, fontname=t_med_name, color=text_color)

            # QR Code
            qr_x, qr_y = 160.62, 39.29
            qr_s = 82.32
            qr_rect = fitz.Rect(qr_x, qr_y, qr_x + qr_s, qr_y + qr_s)
            page.insert_image(qr_rect, stream=create_vcard_qr(data))
        
        elif template_style == "Metaweb":
            font_reg = os.path.join(font_base, "fonts", "Montserrat", "static", "Montserrat-Regular.ttf")
            font_bold = os.path.join(font_base, "fonts", "Montserrat", "static", "Montserrat-Bold.ttf")
            font_semi = os.path.join(font_base, "fonts", "Montserrat", "static", "Montserrat-SemiBold.ttf")

            try:
                ret = page.insert_font(fontname="mont-reg", fontfile=font_reg)
                f_reg_name = ret if isinstance(ret, str) else "mont-reg"
                
                ret = page.insert_font(fontname="mont-bold", fontfile=font_bold)
                f_bold_name = ret if isinstance(ret, str) else "mont-bold"
                
                # Manual width calc fallback if font obj fails
                firstname_width = len(data['first_name']) * 7 # approx
                
            except:
                f_reg_name = "helv"
                f_bold_name = "helv"
                firstname_width = len(data['first_name']) * 7

            page.insert_text((18, 38), f"{data['first_name']}", fontsize=12, fontname=f_bold_name, color=text_color) 
            page.insert_text((18 + firstname_width + 4, 38), f"{data['last_name']}", fontsize=12, fontname=f_reg_name, color=text_color)
            
            page.insert_text((19, 50), data['title'], fontsize=6, fontname=f_reg_name, color=text_color)
            
            page.insert_text((30, 74), data['phone_mobile'], fontsize=5, fontname=f_reg_name, color=text_color)
            page.insert_text((30, 88), data['phone_office'], fontsize=5, fontname=f_reg_name, color=text_color)
            page.insert_text((30, 103), data['email'], fontsize=5, fontname=f_reg_name, color=text_color)
            page.insert_text((30, 116), data['website'], fontsize=5, fontname=f_reg_name, color=text_color)
            page.insert_text((30, 129), data['address_line1'], fontsize=5, fontname=f_reg_name, color=text_color)
            page.insert_text((30, 137), data['address_line2'], fontsize=5, fontname=f_reg_name, color=text_color)

            # QR Code
            qr_x, qr_y = 179.18, 74.31
            qr_s = 67.00
            qr_rect = fitz.Rect(qr_x, qr_y, qr_x + qr_s, qr_y + qr_s)
            page.insert_image(qr_rect, stream=create_vcard_qr(data))

        return doc.write()

    except Exception as e:
        print(f"Business Card Gen Error: {e}")
        return None

def generate_business_card_preview(template_style, data):
    """Returns PNG preview of the card."""
    pdf_bytes = generate_business_card_pdf(template_style, data)
    if not pdf_bytes:
        return None
        
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[1] # Preview the back side (details side)
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    return pix.tobytes("png")
