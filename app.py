import streamlit as st
import os
import tools.business_card
import tools.welcome_aboard
import tools.dashboard
from streamlit_option_menu import option_menu

st.set_page_config(layout="wide", page_title="Trikon Dashboard", page_icon="⚙️")

# Global CSS Injection
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --primary: #000000;
        --accent: #0071E3;
        --bg: #FFFFFF; /* Brighter background */
        --sidebar-bg: #F5F5F7; /* Grey sidebar like macOS */
        --card-bg: #FFFFFF;
        --text: #1D1D1F;
        --text-secondary: #86868B;
        --border: #D2D2D7;
    }

    /* Main App Background */
    .stApp {
        background-color: var(--bg);
        color: var(--text);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Typography */
    h1, h2, h3, .stHeader {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        color: var(--text) !important;
        letter-spacing: -0.022em !important;
    }

    /* Sidebar Customization */
    section[data-testid="stSidebar"] {
        background-color: var(--sidebar-bg) !important;
        border-right: 1px solid var(--border) !important;
    }
    
    section[data-testid="stSidebar"] > div {
        background-color: var(--sidebar-bg) !important;
    }

    /* Logo Container */
    .logo-container {
        padding: 1rem 0.5rem;
        display: flex;
        justify-content: center;
        margin-bottom: 1rem;
    }
    
    .logo-container img {
        width: 100px !important; /* Fixed smaller logo size */
        height: auto;
    }

    /* Metric Cards Redesign */
    .stMetric {
        background: white !important;
        padding: 24px !important;
        border-radius: 16px !important;
        border: 1px solid #E5E5E7 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
    }

    /* Fix visibility of text in forms */
    .stTextInput label, .stSelectbox label {
        font-weight: 500 !important;
        color: var(--text) !important;
        font-size: 0.9rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar with Logo and Styled Menu
with st.sidebar:
    logo_path = r"images/trikon_logo.png"
    if os.path.exists(logo_path):
        st.image(logo_path, width=150) # Increased width
    else:
        st.title("Trikon")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # option_menu for professional app-style navigation
    selected = option_menu(
        menu_title=None,
        options=["Dashboard", "Business Card", "Welcome Aboard", "Settings"],
        icons=["house", "person-badge", "person-plus", "gear"], # Bootstrap icons used by option_menu
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#86868B", "font-size": "1.1rem"}, 
            "nav-link": {
                "font-size": "0.95rem", 
                "text-align": "left", 
                "margin": "4px", 
                "border-radius": "10px",
                "color": "#1D1D1F",
                "font-weight": "500"
            },
            "nav-link-selected": {"background-color": "#0071E3", "color": "white"},
        }
    )

# Routing
if selected == "Dashboard":
    tools.dashboard.render()
elif selected == "Business Card":
    tools.business_card.render()
elif selected == "Welcome Aboard":
    tools.welcome_aboard.render()
elif selected == "Settings":
    st.title("Settings")
    st.write("Settings and preferences will be added here.")
