import streamlit as st
import os
import tools.business_card
import tools.welcome_aboard
import tools.dashboard
import tools.id_card
from streamlit_option_menu import option_menu

st.set_page_config(layout="wide", page_title="Trikon Dashboard", page_icon="⚙️")

# Global CSS Injection
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --primary: #000000;
        --accent: #0071E3;
        --bg: #F9FAFB; /* Linear Neutral Background */
        --sidebar-bg: #FFFFFF;
        --card-bg: #FFFFFF;
        --text: #111827;
        --text-secondary: #6B7280;
        --border: #E5E7EB; /* Crisp Thin Border */
        --radius: 12px;
    }

    /* Modern Minimalist Background */
    .stApp {
        background-color: var(--bg);
        color: var(--text);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Sidebar - Crisp & Clean */
    section[data-testid="stSidebar"] {
        background-color: var(--sidebar-bg) !important;
        border-right: 1px solid var(--border) !important;
    }
    
    section[data-testid="stSidebar"] > div {
        background-color: transparent !important;
    }

    /* Remove Sidebar Top Padding & Empty Header */
    [data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
        padding-top: 0rem !important;
    }
    
    [data-testid="stSidebarHeader"] {
        display: none !important;
    }

    /* Bento Grid System - Crisp White Cards */
    [data-testid="stVerticalBlockBorderWrapper"] > div {
        background: var(--card-bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        padding: 2rem !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
        margin-bottom: 1.5rem !important;
    }

    /* Metric Cards - Minimalist Pro */
    [data-testid="stMetric"] {
        background: var(--card-bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        padding: 1.5rem !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
    }

    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        font-size: 0.75rem !important;
    }

    [data-testid="stMetricValue"] {
        color: var(--text) !important;
        font-weight: 700 !important;
        letter-spacing: -0.03em !important;
    }

    /* Typography */
    h1, h2, h3, .stHeader {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        color: var(--text) !important;
        letter-spacing: -0.04em !important;
    }

    /* Re-styling Inputs for "Linear" Look */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background-color: white !important;
        border-radius: 8px !important;
        border: 1px solid var(--border) !important;
        padding: 0.5rem 0.75rem !important;
        font-size: 0.95rem !important;
        color: var(--text) !important;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px rgba(0, 113, 227, 0.1) !important;
    }

    /* Precision Button Style */
    .stButton>button {
        background: var(--primary) !important;
        color: white !important;
        border-radius: 8px !important;
        border: 1px solid var(--primary) !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
    }

    .stButton>button:hover {
        background: #1F2937 !important;
        border-color: #1F2937 !important;
    }

    /* Adjust Padding of Main Content */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 50px !important;
    }

    /* Hide Streamlit Header gap */
    header[data-testid="stHeader"] {
        display: none !important;
    }

    /* Navigation Menu Style - Standard Professional */
    .nav-link-selected {
        background-color: #F3F4F6 !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Header with Logo
with st.sidebar:
    logo_path = r"images/trikon_logo.png"
    if os.path.exists(logo_path):
        # Center the logo with high-end padding
        st.markdown('<div style="display: flex; justify-content: center; padding: 20px 0;">', unsafe_allow_html=True)
        st.image(logo_path, width=200) 
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.title("Trikon")
    
    # option_menu for professional app-style navigation
    selected = option_menu(
        menu_title=None,
        options=["Dashboard", "Business Card", "Welcome Aboard", "ID Card", "Settings"],
        icons=["house", "person-badge", "person-plus", "person-vcard", "gear"], # Bootstrap icons used by option_menu
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"font-size": "1.1rem"}, # Removed specific color to allow inheritance
            "nav-link": {
                "font-size": "0.95rem", 
                "text-align": "left", 
                "margin": "4px", 
                "border-radius": "10px",
                "color": "#1D1D1F",
                "font-weight": "500"
            },
            "nav-link-selected": {"background-color": "#0071E3", "color": "white !important"},
        }
    )

# Routing
if selected == "Dashboard":
    tools.dashboard.render()
elif selected == "Business Card":
    tools.business_card.render()
elif selected == "Welcome Aboard":
    tools.welcome_aboard.render()
elif selected == "ID Card":
    tools.id_card.render()
elif selected == "Settings":
    st.title("Settings")
    st.write("Settings and preferences will be added here.")
