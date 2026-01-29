import streamlit as st
import os
import tools.business_card
import tools.welcome_aboard
import tools.dashboard
import tools.id_card
import tools.settings
import utils.auth as auth
from streamlit_option_menu import option_menu

st.set_page_config(layout="wide", page_title="Trikon Dashboard", page_icon="⚙️")

# Global CSS Injection
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --primary: #000000;
        --accent: #0071E3;
        --bg: #F9FAFB;
        --sidebar-bg: #FFFFFF;
        --card-bg: #FFFFFF;
        --text: #111827;
        --text-secondary: #6B7280;
        --border: #E5E7EB;
        --radius: 12px;
    }

    .stApp {
        background-color: var(--bg);
        color: var(--text);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    section[data-testid="stSidebar"] {
        background-color: var(--sidebar-bg) !important;
        border-right: 1px solid var(--border) !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
        padding-top: 0rem !important;
    }
    
    [data-testid="stSidebarHeader"] {
        display: none !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"] > div {
        background: var(--card-bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        padding: 2rem !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
        margin-bottom: 1.5rem !important;
    }

    [data-testid="stMetric"] {
        background: var(--card-bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        padding: 1.5rem !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
    }

    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background-color: white !important;
        border-radius: 8px !important;
        border: 1px solid var(--border) !important;
        padding: 0.5rem 0.75rem !important;
    }
    
    .stButton>button {
        background: var(--primary) !important;
        color: white !important;
        border-radius: 8px !important;
        border: 1px solid var(--primary) !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }

    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 50px !important;
    }

    header[data-testid="stHeader"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Authentication Gateway
if not auth.is_logged_in():
    # Centered Login Container with Logo
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        with st.container(border=True):
            # Header
            st.markdown("""
                <div style="text-align: center; padding-top: 10px; padding-bottom: 20px;">
                    <div style="margin-bottom: 20px;">
                        <!-- Embed Logo -->
                        <img src="https://trikon.com/wp-content/uploads/2023/10/logo.png" width="160" alt="Trikon Logo" style="opacity: 0.9;">
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Local fallback for logo if internet is disconnected, but using URL for better resolution often
            # If you want local only:
            # logo_path = "images/trikon_logo.png"
            # if os.path.exists(logo_path):
            #     st.image(logo_path, use_column_width=False, width=150)
            
            st.markdown("""
                <div style="text-align: center; margin-bottom: 2rem;">
                    <h2 style="margin: 0; font-size: 1.5rem; font-weight: 600; letter-spacing: -0.03em;">Welcome Back</h2>
                    <p style="color: #6B7280; font-size: 0.9rem; margin-top: 0.5rem;">Enter your credentials to access the dashboard</p>
                </div>
            """, unsafe_allow_html=True)
            
            email = st.text_input("Email Address", placeholder="name@trikon.com", key="login_email")
            password = st.text_input("Password", type="password", placeholder="••••••••", key="login_pwd")
            
            st.markdown("<br>", unsafe_allow_html=True)
            login_btn = st.button("Sign In", use_container_width=True, type="primary")
            
            if login_btn:
                if auth.verify_login(email, password):
                    st.success("Successfully Authenticated")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please contact your admin.")
            
            st.markdown("""
                <div style="text-align: center; margin-top: 1.5rem;">
                    <p style="font-size: 0.75rem; color: #9CA3AF;">© 2024 Trikon. All rights reserved.</p>
                </div>
            """, unsafe_allow_html=True)
            
    st.stop()

# --- LOGGED IN AREA ---
user = auth.get_current_user()

with st.sidebar:
    logo_path = r"images/trikon_logo.png"
    if os.path.exists(logo_path):
        st.markdown('<div style="display: flex; justify-content: center; padding: 20px 0;">', unsafe_allow_html=True)
        st.image(logo_path, width=180) 
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.title("Trikon Dashboard")
        
    st.markdown(f"""
        <div style="padding: 10px; margin: 10px; background: #F9FAFB; border-radius: 10px; border: 1px solid #E5E7EB;">
            <p style="margin:0; font-size: 0.75rem; color: #6B7280; text-transform: uppercase; font-weight: 600;">Signed in as</p>
            <p style="margin:0; font-size: 0.9rem; font-weight: 500; color: #111827;">{user['email']}</p>
            <p style="margin:0; font-size: 0.7rem; color: #0071E3; font-weight: 600;">{user['role'].upper()}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Filter tools based on user permissions
    all_mapping = {
        "Dashboard": {"icon": "house", "render": tools.dashboard.render},
        "Business Card": {"icon": "person-badge", "render": tools.business_card.render},
        "Welcome Aboard": {"icon": "person-plus", "render": tools.welcome_aboard.render},
        "ID Card": {"icon": "person-vcard", "render": tools.id_card.render},
        "Settings": {"icon": "gear", "render": tools.settings.render}
    }
    
    allowed = user.get("allowed_tools", ["Dashboard"])
    visible_tools = [t for t in all_mapping.keys() if t in allowed]
    visible_icons = [all_mapping[t]["icon"] for t in visible_tools]
    
    selected = option_menu(
        menu_title=None,
        options=visible_tools,
        icons=visible_icons,
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"font-size": "1.1rem"},
            "nav-link": {
                "font-size": "0.95rem", "text-align": "left", "margin": "4px", "border-radius": "10px",
                "color": "#1D1D1F", "font-weight": "500"
            },
            "nav-link-selected": {"background-color": "#0071E3", "color": "white !important"},
        }
    )
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("Logout", icon="🔒", use_container_width=True):
        auth.logout()

# Render selected tool
if selected in all_mapping:
    all_mapping[selected]["render"]()
