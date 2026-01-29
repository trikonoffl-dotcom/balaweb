import streamlit as st
import generator
import os
import fitz # PyMuPDF

def render():
    st.title("Business Card Generator")
    st.markdown("<p style='color: #64748B; font-size: 1.1rem;'>Professional, high-quality business cards in seconds.</p>", unsafe_allow_html=True)
    st.divider()

    col1, col2 = st.columns([1, 1.2], gap="large")

    with col1:
        st.subheader("Card Configuration")
        template = st.selectbox("Select Template", ["Trikon", "Metaweb"])
        
        # Style-Specific Defaults
        if template == "Trikon":
            default_website = "www.trikon.com.au"
            default_office = "1300 TRIKON (874 566)"
        else:
            default_website = "metaweb.com.au"
            default_office = "1300 262 987"

        with st.container():
            st.markdown("##### Employee Info")
            c1, c2 = st.columns(2)
            with c1:
                first_name = st.text_input("First Name", "John")
            with c2:
                last_name = st.text_input("Last Name", "Doe")
            title = st.text_input("Job Title", "General Manager")
        
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container():
            st.markdown("##### Contact Details")
            c1, c2 = st.columns(2)
            with c1:
                phone_mobile = st.text_input("Mobile Phone", "0400 000 000")
            with c2:
                phone_office = st.text_input("Office Phone", default_office)
            
            c1, c2 = st.columns(2)
            with c1:
                email = st.text_input("Email", "john.doe@example.com")
            with c2:
                website = st.text_input("Website", default_website)
        
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container():
            st.markdown("##### Office Location")
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
            
            # Smart split for better balance
            parts = selected_address.split(", ")
            # If the first part is short (like "Suite 208"), combine it with the second part
            if len(parts) > 2 and (len(parts[0]) < 12 or any(x in parts[0].lower() for x in ['suite', 'unit', 'level', 'shop'])):
                default_addr1 = f"{parts[0]}, {parts[1]}"
                default_addr2 = ", ".join(parts[2:])
            else:
                default_addr1 = parts[0]
                default_addr2 = ", ".join(parts[1:])
                
            # Allow user to manually refine the lines
            address_line1 = st.text_input("Refine Address Line 1", default_addr1)
            address_line2 = st.text_input("Refine Address Line 2", default_addr2)

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
                    import generator
                    pdf_bytes = generator.generate_card(pdf_path, data, style=template)
                    
                    # Log to Supabase
                    import utils.db as db
                    db.log_generation(
                        tool="Business Card",
                        name=f"{data['first_name']} {data['last_name']}",
                        metadata={"style": template, "company": data.get("company", "Trikon/Metaweb")}
                    )
                    
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
