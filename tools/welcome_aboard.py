import streamlit as st
import fitz
import os
import io
from PIL import Image, ImageDraw, ImageOps
import datetime

def get_date_suffix(day):
    if 4 <= day <= 20 or 24 <= day <= 30:
        return "th"
    else:
        return ["st", "nd", "rd"][day % 10 - 1]

def make_rounded(image, width, height, radius):
    # Resize image to fill the box (cover)
    image = ImageOps.fit(image, (int(width), int(height)), method=Image.Resampling.LANCZOS)
    
    # Create mask
    mask = Image.new('L', (int(width), int(height)), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), (int(width), int(height))], radius=radius, fill=255)
    
    # Apply mask
    rounded_img = Image.new('RGBA', (int(width), int(height)), (0, 0, 0, 0))
    rounded_img.paste(image, (0, 0), mask)
    return rounded_img

def render():
    st.title("Welcome Aboard Generator")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Employee Details")
        
        first_name = st.text_input("First Name", "Suresh")
        last_name = st.text_input("Last Name", "Kumar")
        title = st.text_input("Job Title", "Technical Support Executive")
        
        # Date Picker
        date_obj = st.date_input("Date", datetime.date(2026, 1, 12))
        suffix = get_date_suffix(date_obj.day)
        # Safest cross-platform way for day without zero padding + suffix:
        date_str = f"{date_obj.day}{suffix} {date_obj.strftime('%b %Y')}"
        
        photo_file = st.file_uploader("Upload Photo", type=["jpg", "jpeg", "png"])
        
        generate_btn = st.button("Generate Welcome Image")

    with col2:
        st.subheader("Preview")
        if generate_btn and photo_file:
            # Relative path for Cloud and Local
            current_dir = os.path.dirname(os.path.abspath(__file__))
            templates_dir = os.path.join(current_dir, "..", "Templates")
            template_path = os.path.join(templates_dir, "welcome aboard - Without name.pdf")
            
            # Fallback for local dev if relative fails
            if not os.path.exists(template_path):
                template_path = r"C:\Users\pabal\Documents\Businesscard\Templates\welcome aboard - Without name.pdf"
            
            if os.path.exists(template_path):
                try:
                    # Load PDF
                    doc = fitz.open(template_path)
                    page = doc[0]
                    
                    # Font Setup
                    font_base = os.path.join(current_dir, "..")
                    if not os.path.exists(os.path.join(font_base, "Poppins")):
                        font_base = r"C:\Users\pabal\Documents\Businesscard"
                    font_bold = os.path.join(font_base, "Poppins", "Poppins-Bold.ttf")
                    font_reg = os.path.join(font_base, "Poppins", "Poppins-Regular.ttf") 
                    
                    page.insert_font(fontname="pop-bold", fontfile=font_bold)
                    page.insert_font(fontname="pop-reg", fontfile=font_reg)
                    
                    text_color = (1, 1, 1) # White
                    
                    # Coordinates for White Box position (Top-Left)
                    # Centering Adjustment (X=71, Y=340)
                    user_x = 71 
                    user_y = 340
                    
                    # Size from User (Non-square)
                    # W: 421.978, H: 502.045
                    user_w = 421.978
                    user_h = 502.045
                    
                    user_r = 28.492 # Keeping user's radius preference
                    
                    # Process Photo
                    photo_bytes = photo_file.read()
                    original_img = Image.open(io.BytesIO(photo_bytes))
                    
                    # Create Rounded Image
                    rounded_img = make_rounded(original_img, user_w, user_h, user_r)
                    
                    # Convert back to bytes for PyMuPDF
                    # Note: Since PyMuPDF insert_image using stream needs a file-like object or bytes.
                    # As of recent versions, it supports PNG memory buffer.
                    img_byte_arr = io.BytesIO()
                    rounded_img.save(img_byte_arr, format='PNG')
                    img_byte_arr = img_byte_arr.getvalue()
                    
                    # Insert Photo
                    # Rect takes (x0, y0, x1, y1)
                    photo_rect = fitz.Rect(user_x, user_y, user_x + user_w, user_y + user_h)
                    
                    # NOTE: PyMuPDF inserts images as opaque rectangles by default (no alpha usually unless handled specifically).
                    # However, inserting a PNG with alpha channel usually works but might have a black background if not supported.
                    # Overlaying on a PDF usually respects alpha.
                    page.insert_image(photo_rect, stream=img_byte_arr)
                    
                    # Insert Text
                    # Name: Left aligned at 563
                    # First Name
                    page.insert_text((563, 500), first_name, fontsize=77, fontname="pop-bold", color=text_color)
                    # Last Name
                    page.insert_text((563, 580), last_name, fontsize=77, fontname="pop-bold", color=text_color)
                    
                    # Title
                    page.insert_text((563, 640), title, fontsize=25, fontname="pop-reg", color=text_color)
                    
                    # Date
                    page.insert_text((563, 700), date_str, fontsize=26, fontname="pop-bold", color=text_color)
                    
                    # Log to Supabase
                    import utils.db as db
                    db.log_generation(
                        tool="Welcome Aboard",
                        name=f"{first_name} {last_name}",
                        metadata={"title": title, "date": date_str}
                    )

                    # Export to JPG
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # Higher resolution
                    img_bytes = pix.tobytes("jpg")
                    
                    st.image(img_bytes, caption="Generated Welcome Image", use_column_width=True)
                    
                    st.download_button(
                        label="Download JPG",
                        data=img_bytes,
                        file_name=f"welcome_{first_name}_{last_name}.jpg",
                        mime="image/jpeg"
                    )
                    
                except Exception as e:
                    st.error(f"Error generating image: {e}")
            else:
                st.error(f"Template not found at: {template_path}")
        elif generate_btn and not photo_file:
            st.warning("Please upload a photo.")
