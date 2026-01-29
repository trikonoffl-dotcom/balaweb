import streamlit as st
import generator
import os
import fitz # PyMuPDF

def render():
    st.title("Business Card Generator")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Card Details")
        template = st.selectbox("Select Template", ["Trikon", "Metaweb"])
        
        first_name = st.text_input("First Name", "John")
        last_name = st.text_input("Last Name", "Doe")
        title = st.text_input("Job Title", "General Manager")
        
        phone_mobile = st.text_input("Mobile Phone", "0400 000 000")
        phone_office = st.text_input("Office Phone", "1300 000 000")
        email = st.text_input("Email", "john.doe@example.com")
        website = st.text_input("Website", "www.example.com")
        
        address_line1 = st.text_input("Address Line 1", "Level 1, 123 Example St")
        address_line2 = st.text_input("Address Line 2", "Sydney NSW 2000")

        data = {
            "first_name": first_name,
            "last_name": last_name,
            "title": title,
            "phone_mobile": phone_mobile,
            "phone_office": phone_office,
            "email": email,
            "website": website,
            "address": f"{address_line1}, {address_line2}", # For vCard
            "address_line1": address_line1,
            "address_line2": address_line2
        }

        generate_btn = st.button("Generate Card")

    with col2:
        st.subheader("Preview")
        if generate_btn:
            # Determine Path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            templates_dir = os.path.join(current_dir, "..", "Templates")
            
            if template == "Trikon":
                pdf_path = os.path.join(templates_dir, "Name_Trikon.pdf")
            else:
                pdf_path = os.path.join(templates_dir, "Name_MetaWeb.pdf")
            
            # Absolute fallback for local user path if relative fails during development
            if not os.path.exists(pdf_path):
                 local_fixed_path = r"C:\Users\pabal\Documents\Businesscard\Templates"
                 if template == "Trikon":
                    pdf_path = os.path.join(local_fixed_path, "Name_Trikon.pdf")
                 else:
                    pdf_path = os.path.join(local_fixed_path, "Name_MetaWeb.pdf")
            
            if os.path.exists(pdf_path):
                try:
                    pdf_bytes = generator.generate_card(pdf_path, data, style=template)
                    
                    # Display Preview using PyMuPDF
                    doc = fitz.open("pdf", pdf_bytes)
                    page = doc[1] # Using Page 2 as per original logic (index 1)
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                    img_bytes = pix.tobytes("png")
                    
                    st.image(img_bytes, caption="Card Preview", use_column_width=True)
                    
                    st.download_button(
                        label="Download PDF",
                        data=pdf_bytes,
                        file_name="business_card.pdf",
                        mime="application/pdf"
                    )
                    
                    st.success("PDF Generated! Click Download to view.")
                    
                except Exception as e:
                    st.error(f"Error generating PDF: {e}")
            else:
                st.error(f"Template not found at: {pdf_path}")
