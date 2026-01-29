import streamlit as st
import os
import requests
import io
import fitz
import datetime
from PIL import Image, ImageOps

# Photoroom API Key (Live)
PHOTOROOM_API_KEY = "sk_pr_default_badcd4bd9dd67dee9a1bbc4912c109f6d21a7cb1"

def remove_background(image_bytes):
    """Call Photoroom API to remove background."""
    url = "https://sdk.photoroom.com/v1/segment"
    headers = {
        "x-api-key": PHOTOROOM_API_KEY,
        "Accept": "image/png"
    }
    files = {
        "image_file": ("image.jpg", image_bytes, "image/jpeg")
    }
    
    response = requests.post(url, headers=headers, files=files)
    
    if response.status_code == 200:
        return response.content
    else:
        st.error(f"Background removal failed: {response.status_code} - {response.text}")
        return None

def render():
    st.title("AI ID Card Generator")
    st.markdown("<p style='color: #6B7280; font-size: 1.15rem; font-weight: 400; letter-spacing: -0.01em;'>AI-powered ID cards with automatic background removal.</p>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1.2], gap="large")

    with col1:
        st.markdown("<h4 style='font-weight: 600; font-size: 1.25rem; margin-bottom: 1.5rem;'>Employee Details</h4>", unsafe_allow_html=True)
        
        with st.container(border=True):
            st.markdown("<p style='font-weight: 500; font-size: 0.75rem; color: #6B7280; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 1rem;'>Basic Identity</p>", unsafe_allow_html=True)
            first_name = st.text_input("First Name", "Bragadeesh")
            last_name = st.text_input("Last Name", "Sundararajan")
            title = st.text_input("Job Title", "AI Prompt Engineer")
        
        with st.container(border=True):
            st.markdown("<p style='font-weight: 500; font-size: 0.75rem; color: #6B7280; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 1rem;'>System Info</p>", unsafe_allow_html=True)
            id_number = st.text_input("ID Number", "TRC00049")
            doj = st.date_input("Joining Date", datetime.date(2025, 11, 17))
        
        with st.container(border=True):
            st.markdown("<p style='font-weight: 500; font-size: 0.75rem; color: #6B7280; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 1rem;'>Profile Media</p>", unsafe_allow_html=True)
            photo_file = st.file_uploader("Upload Portrait Photo", type=["jpg", "jpeg", "png"])
            remove_bg = st.checkbox("AI Background Removal (Photoroom)", value=True)

        generate_btn = st.button("Generate ID Card", use_container_width=True)

    with col2:
        st.markdown("<h4 style='font-weight: 600; font-size: 1.25rem; margin-bottom: 1.5rem;'>Live Preview</h4>")
        
        if not (generate_btn and photo_file):
             with st.container(border=True):
                st.info("Upload a photo and fill in the details to see the preview.", icon="🪪")

        if generate_btn and photo_file:
            # Process Background Removal
            photo_bytes = photo_file.read()
            
            with st.spinner("AI is removing background and aligning..."):
                if remove_bg:
                    processed_photo = remove_background(photo_bytes)
                else:
                    processed_photo = photo_bytes
                
            if processed_photo:
                try:
                    # Determine Path
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    template_path = os.path.join(current_dir, "..", "Templates", "idcard", "id card empty.pdf")
                    
                    if not os.path.exists(template_path):
                         template_path = r"C:\Users\pabal\Documents\Businesscard\Templates\idcard\id card empty.pdf"
                    
                    if os.path.exists(template_path):
                        doc = fitz.open(template_path)
                        page = doc[0]
                        
                        # Font Setup
                        # Note: We'll use standard fonts as Poppins might not be available in 
                        # the specific format needed for all systems without complex registration.
                        # Rubik-Bold/Regular were used in the sample.
                        
                        blue_text = (18/255, 34/255, 66/255) # Dark Blue
                        white_text = (1, 1, 1)
                        
                        # Text Insertion (Coordinates from sample analysis)
                        # Name - Using slightly smaller fonts to avoid overflow
                        page.insert_text((14.8, 147.6), first_name.upper(), fontsize=15, fontname="helv-bold", color=blue_text)
                        page.insert_text((15.0, 168.7), last_name.upper(), fontsize=15, fontname="helv", color=blue_text)
                        
                        # Title
                        page.insert_text((15.5, 183.8), title, fontsize=8, fontname="helv", color=blue_text)
                        
                        # DOI
                        date_str = doj.strftime("%d-%m-%Y")
                        page.insert_text((15.1, 197.3), f"D.O.J:  {date_str}", fontsize=8, fontname="helv", color=blue_text)
                        
                        # ID Number (Bottom White Text)
                        page.insert_text((15.6, 226.3), f"ID Number: {id_number}", fontsize=10, fontname="helv", color=white_text)
                        
                        # Photo Placement
                        # Target BBox: [-20, 30, 120, 180] (estimated center-left)
                        # We'll use a safer visible bbox
                        photo_rect = fitz.Rect(-2.16, 39.49, 101.6, 195.23)
                        
                        # Process image to ensure it fills the space correctly (Center-Crop)
                        img = Image.open(io.BytesIO(processed_photo))
                        # Identify face/subject bbox (Photoroom already removed background, so bbox is the subject)
                        sub_bbox = img.getbbox() # (left, top, right, bottom)
                        if sub_bbox:
                            # Crop to subject only (adds focus)
                            img = img.crop(sub_bbox)
                        
                        # Fit to the target aspect ratio
                        target_w = photo_rect.width
                        target_h = photo_rect.height
                        
                        # Create a high-res version for the PDF
                        # We want to maintain aspect ratio but fill the height primarily as it's a portrait card
                        img_byte_arr = io.BytesIO()
                        img.save(img_byte_arr, format='PNG')
                        final_photo_bytes = img_byte_arr.getvalue()

                        page.insert_image(photo_rect, stream=final_photo_bytes)
                        
                        # Log to Supabase
                        import utils.db as db
                        db.log_generation(
                            tool="ID Card",
                            name=f"{first_name} {last_name}",
                            metadata={"id": id_number, "bg_removed": remove_bg}
                        )

                        # Preview
                        pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))
                        img_bytes = pix.tobytes("png")
                        st.image(img_bytes, caption="ID Card Preview", use_column_width=True)
                        
                        pdf_bytes = doc.write()
                        st.download_button(
                            label="Download ID Card PDF",
                            data=pdf_bytes,
                            file_name=f"ID_Card_{id_number}.pdf",
                            mime="application/pdf"
                        )
                        
                        doc.close()
                    else:
                        st.error("Template not found.")
                except Exception as e:
                    st.error(f"Error: {e}")
