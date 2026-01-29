import streamlit as st
import pandas as pd
from utils.db import get_supabase
from utils.auth import hash_password, get_current_user

def render():
    user = get_current_user()
    if not user or user.get("role") != "admin":
        st.error("Access Denied: You do not have permission to view this page.")
        return

    st.title("Admin Settings")
    st.markdown("<p style='color: #6B7280; font-size: 1.15rem; font-weight: 400;'>Manage users, roles, and tool access across the Trikon Ecosystem.</p>", unsafe_allow_html=True)

    tabs = st.tabs(["👥 User Management", "⚙️ System Config"])

    with tabs[0]:
        st.markdown("<h4 style='font-weight: 600; font-size: 1.25rem; margin-bottom: 1.5rem;'>User Accounts</h4>", unsafe_allow_html=True)
        
        try:
            supabase = get_supabase()
            response = supabase.table("users").select("*").execute()
            users_data = response.data

            if users_data:
                df = pd.DataFrame(users_data)
                st.dataframe(df[["email", "role", "allowed_tools", "created_at"]], use_container_width=True)
            
            with st.expander("➕ Add New User", expanded=False):
                with st.form("add_user_form"):
                    new_email = st.text_input("User Email")
                    new_password = st.text_input("Temporary Password", type="password")
                    new_role = st.selectbox("Role", ["member", "admin"])
                    
                    available_tools = ["Dashboard", "Business Card", "Welcome Aboard", "ID Card", "Settings"]
                    selected_tools = st.multiselect("Allow Access To:", available_tools, default=["Dashboard"])
                    
                    submit = st.form_submit_button("Create User")
                    
                    if submit:
                        if new_email and new_password:
                            payload = {
                                "email": new_email,
                                "password_hash": hash_password(new_password),
                                "role": new_role,
                                "allowed_tools": selected_tools
                            }
                            supabase.table("users").insert(payload).execute()
                            st.success(f"User {new_email} created successfully!")
                            st.rerun()
                        else:
                            st.error("Please fill in all fields.")
                            
        except Exception as e:
            st.error(f"Failed to load user management: {e}")

    with tabs[1]:
        st.info("System-wide configurations and API key management will be available here in future updates.")
