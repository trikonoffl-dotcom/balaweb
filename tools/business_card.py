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
        
        # Style-Specific Defaults
        if template == "Trikon":
            default_website = "www.trikon.com.au"
            default_office = "1300 TRIKON (874 566)"
        else:
            default_website = "metaweb.com.au"
            default_office = "1300 262 987"

        first_name = st.text_input("First Name", "John")
        last_name = st.text_input("Last Name", "Doe")
        title = st.text_input("Job Title", "General Manager")
        
        phone_mobile = st.text_input("Mobile Phone", "0400 000 000")
        phone_office = st.text_input("Office Phone", default_office)
        email = st.text_input("Email", "john.doe@example.com")
        website = st.text_input("Website", default_website)
        
        addresses = [
            "3/7 Meridian Place, Bella Vista NSW 2153, Australia",
            "Suite 208, 111 Overton Rd, Williams Landing VIC 3030, Australia",
            "Unit 3, 304 Montague Road, West End QLD 4101, Australia",
            "Suite 2, 161 Maitland Road, Mayfield NSW 2304, Australia",
            "Level 5, Suite 5, 221-229 Crown St, Wollongong NSW, Australia",
            "Level 5, Suite 5, 221-229 Crown St, Wollongong NSW 2500, Australia (Business Hub)",
            "Shop 4, 285 Windsor St, Richmond NSW 2753, Australia (Hawkesbury Business Hub)"
        ]
        
        selected_address = st.selectbox("Select Address", addresses)
        
        # Split address for PDF (Simple split by first comma or keeping it smart)
        addr_parts = selected_address.split(", ", 1)
        address_line1 = addr_parts[0]
        address_line2 = addr_parts[1] if len(addr_parts) > 1 else ""

        data = {
            "first_name": first_name,
            "last_name": last_name,
            "title": title,
            "phone_mobile": phone_mobile,
            "phone_office": phone_office,
            "email": email,
            "website": website,
            "address": selected_address, # For vCard
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
