import streamlit as st
import os
import requests
import io
import fitz
import datetime
from PIL import Image, ImageOps
from rembg import remove

def remove_background(image_bytes):
    """Local background removal using rembg."""
    try:
        return remove(image_bytes)
    except Exception as e:
        st.error(f"Local background removal failed: {e}")
        return None

def render():
    st.title("AI ID Card Generator")
    st.markdown("<p style='color: #6B7280; font-size: 1.15rem; font-weight: 400; letter-spacing: -0.01em;'>AI-powered ID cards with local background removal and precision alignment tools.</p>", unsafe_allow_html=True)

    # Office Addresses
    offices = {
        "Chennai": "Centre Point 3 , 7th Floor\n2/4 Mount Ponnamallee High Road\nManapakkam, Porur, Chennai 600089",
        "Ahmedabad": "COLONNADE-2, 1105, 11th Floor\nbehind Rajpath Rangoli Road\nBodakdev, Ahmedabad, Gujarat 380059"
    }

    col1, col2 = st.columns([1, 1.2], gap="large")

    with col1:
        st.markdown("<h4 style='font-weight: 600; font-size: 1.25rem; margin-bottom: 1.5rem;'>Front Side Details</h4>", unsafe_allow_html=True)
        
        with st.container(border=True):
            st.markdown("<p style='font-weight: 500; font-size: 0.75rem; color: #6B7280; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 1rem;'>Basic Identity</p>", unsafe_allow_html=True)
            first_name = st.text_input("First Name", "Bragadeesh")
            last_name = st.text_input("Last Name", "Sundararajan")
            title = st.text_input("Job Title", "AI Prompt Engineer")
        
        with st.container(border=True):
            st.markdown("<p style='font-weight: 500; font-size: 0.75rem; color: #6B7280; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 1rem;'>System Info</p>", unsafe_allow_html=True)
            id_number = st.text_input("ID Number", "TRC00049")
            doj = st.date_input("Joining Date", datetime.date(2025, 11, 17))
        
        st.markdown("<h4 style='font-weight: 600; font-size: 1.25rem; margin-top: 2rem; margin-bottom: 1.5rem;'>Photo & Adjustments</h4>", unsafe_allow_html=True)
        with st.container(border=True):
            photo_file = st.file_uploader("Upload Portrait Photo", type=["jpg", "jpeg", "png"])
            use_ai_removal = st.checkbox("Local AI Background Removal (Free)", value=True)
            
            st.markdown("<p style='font-weight: 500; font-size: 0.75rem; color: #6B7280; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 1rem; margin-bottom: 0.5rem;'>Precision Placement</p>", unsafe_allow_html=True)
            scale = st.slider("Photo Scale", 0.5, 3.0, 1.0, 0.05)
            x_offset = st.slider("Horizontal Move (X)", -100, 100, 0, 1)
            y_offset = st.slider("Vertical Move (Y)", -100, 100, 0, 1)

        st.markdown("<h4 style='font-weight: 600; font-size: 1.25rem; margin-top: 2rem; margin-bottom: 1.5rem;'>Back Side Details</h4>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("<p style='font-weight: 500; font-size: 0.75rem; color: #6B7280; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 1rem;'>Emergency & Health</p>", unsafe_allow_html=True)
            emergency_no = st.text_input("Emergency Number", "9566191956")
            blood_group = st.selectbox("Blood Group", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"], index=0)
            
            st.markdown("<p style='font-weight: 500; font-size: 0.75rem; color: #6B7280; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 1rem; margin-bottom: 0.5rem;'>Office Address</p>", unsafe_allow_html=True)
            office_choice = st.selectbox("Select Office", list(offices.keys()))
            office_address = st.text_area("Edit Address", offices[office_choice], height=100)

        generate_btn = st.button("Generate ID Card", use_container_width=True)

    with col2:
        st.markdown("<h4 style='font-weight: 600; font-size: 1.25rem; margin-bottom: 1.5rem;'>Final Preview</h4>")
        
        if not (generate_btn and photo_file):
             with st.container(border=True):
                st.info("Upload a photo and tweak the sliders to see the preview.", icon="🪪")

        if generate_btn and photo_file:
            photo_bytes = photo_file.read()
            
            with st.spinner("AI is processing image..."):
                if use_ai_removal:
                    processed_photo = remove_background(photo_bytes)
                else:
                    processed_photo = photo_bytes
                
            if processed_photo:
                try:
                    possible_paths = [
                        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Templates", "idcard", "id_card_empty.pdf"),
                        os.path.join(os.getcwd(), "Templates", "idcard", "id_card_empty.pdf"),
                        r"C:\Users\pabal\Documents\Businesscard\Templates\idcard\id_card_empty.pdf"
                    ]
                    
                    template_path = next((p for p in possible_paths if os.path.exists(p)), None)
                    
                    if template_path:
                        doc = fitz.open(template_path)
                        
                        # --- FONT REGISTRATION ---
                        # Strategy: Try to find the font directory using multiple anchors
                        possible_font_dirs = [
                            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts", "Rubik", "static"), # ../fonts/Rubik/static
                            os.path.join(os.getcwd(), "fonts", "Rubik", "static"), # ./fonts/Rubik/static
                            r"C:\Users\pabal\Documents\Businesscard\fonts\Rubik\static" # Local absolute fallback
                        ]
                        
                        font_dir = next((d for d in possible_font_dirs if os.path.exists(d)), None)
                        
                        # Define font mapping
                        fonts_map = {
                            "ru-bold": "Rubik-Bold.ttf",
                            "ru-reg": "Rubik-Regular.ttf",
                            "ru-semi": "Rubik-SemiBold.ttf",
                            "ru-italic": "Rubik-Italic.ttf"
                        }
                        
                        loaded_fonts = []
                        if font_dir:
                            for name, filename in fonts_map.items():
                                path = os.path.join(font_dir, filename)
                                if os.path.exists(path):
                                    try:
                                        # Register on ALL pages in the doc
                                        for page in doc:
                                            page.insert_font(fontname=name, fontfile=path)
                                        loaded_fonts.append(name)
                                    except Exception as e:
                                        st.warning(f"Failed to load font {name}: {e}")
                        
                        # Fallback Function
                        def get_font(desired_font, fallback="helv"):
                            return desired_font if desired_font in loaded_fonts else fallback

                        blue_text = (18/255, 34/255, 66/255)
                        white_text = (1, 1, 1)
                        
                        # Front Text
                        page0.insert_text((14.8, 148), first_name.upper(), fontsize=15, fontname=get_font("ru-bold"), color=blue_text)
                        page0.insert_text((15.0, 168), last_name.upper(), fontsize=11, fontname=get_font("ru-reg"), color=blue_text)
                        page0.insert_text((15.5, 183), title, fontsize=8, fontname=get_font("ru-reg"), color=blue_text)
                        
                        date_str = doj.strftime("%d-%m-%Y")
                        page0.insert_text((15.1, 196), f"D.O.J:  {date_str}", fontsize=8, fontname=get_font("ru-bold"), color=blue_text)
                        page0.insert_text((15.6, 226), f"ID Number: {id_number}", fontsize=10, fontname=get_font("ru-reg"), color=white_text)
                        
                        # --- DYNAMIC PHOTO PLACEMENT ---
                        # Base coordinates from previous refinement
                        # Base rect: (15, 28, 110, 126) -> width: 95, height: 98
                        base_x, base_y = 15 + x_offset, 28 + y_offset
                        base_w, base_h = 95 * scale, 98 * scale
                        
                        # Center the scaled image within the movement
                        # Adjust base_x/y to keep it centered when scaling
                        adj_x = base_x - (base_w - 95) / 2
                        adj_y = base_y - (base_h - 98) / 2
                        
                        photo_rect = fitz.Rect(adj_x, adj_y, adj_x + base_w, adj_y + base_h)
                        page0.insert_image(photo_rect, stream=processed_photo)
                        
                        # BACK PAGE (Index 1)
                        if len(doc) > 1:
                            page1 = doc[1]
                            
                            page1.insert_text((20, 93), f"Emergency Number: {emergency_no}", fontsize=7, fontname=get_font("ru-reg"), color=white_text)
                            page1.insert_text((49, 106), f"Blood Group: {blood_group}", fontsize=7, fontname=get_font("ru-reg"), color=white_text)
                            page1.insert_text((20, 167), "Trikon Telesoft Private Limited", fontsize=7, fontname=get_font("ru-semi"), color=white_text)
                            
                            addr_lines = office_address.split("\n")
                            y_start = 173
                            for line in addr_lines:
                                page1.insert_text((15, y_start), line.strip(), fontsize=6.5, fontname=get_font("ru-reg"), color=white_text)
                                y_start += 8.5
                        
                        # Preview
                        st.markdown("### Front Side")
                        pix0 = page0.get_pixmap(matrix=fitz.Matrix(3, 3))
                        st.image(pix0.tobytes("png"), use_column_width=True)
                        
                        if len(doc) > 1:
                            st.markdown("### Back Side")
                            pix1 = doc[1].get_pixmap(matrix=fitz.Matrix(3, 3))
                            st.image(pix1.tobytes("png"), use_column_width=True)
                        
                        pdf_bytes = doc.write()
                        st.download_button(
                            label="Download Full ID Card (2 Pages)",
                            set_page_config=False,
                            data=pdf_bytes,
                            file_name=f"ID_Card_{id_number}.pdf",
                            mime="application/pdf"
                        )
                        doc.close()
                    else:
                        st.error(f"Template not found.")
                except Exception as e:
                    st.error(f"Error: {e}")
