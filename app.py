import streamlit as st
import tools.business_card
import tools.welcome_aboard
import tools.dashboard

st.set_page_config(layout="wide", page_title="Trikon Dashboard")

# Global CSS Injection
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600&family=Poppins:wght@600;700&display=swap');

    :root {
        --primary: #6366F1;
        --secondary: #818CF8;
        --cta: #10B981;
        --bg: #F5F3FF;
        --text: #1E1B4B;
    }

    /* Main App Background */
    .stApp {
        background-color: var(--bg);
        color: var(--text);
        font-family: 'Open Sans', sans-serif;
    }

    /* Typography */
    h1, h2, h3, .stHeader {
        font-family: 'Poppins', sans-serif !important;
        font-weight: 700 !important;
        color: var(--text) !important;
    }

    /* Buttons */
    .stButton>button {
        background-color: var(--cta) !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }

    .stButton>button:hover {
        opacity: 0.9 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2) !important;
    }

    /* Sidebar Customization */
    section[data-testid="stSidebar"] {
        background-color: white !important;
        border-right: 1px solid #E2E8F0 !important;
    }

    section[data-testid="stSidebar"] .stRadio > label {
        color: var(--text) !important;
        font-weight: 600 !important;
    }

    /* Input Fields */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        border-radius: 8px !important;
        border: 1px solid #E2E8F0 !important;
    }

    .stTextInput>div>div>input:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
    }
</style>
""", unsafe_allow_html=True)

# Navigation
st.sidebar.title("Navigation")
tool = st.sidebar.radio("Select Tool", ["Dashboard", "Business Card Generator", "Welcome Aboard Generator", "Coming Soon"])

if tool == "Dashboard":
    tools.dashboard.render()
elif tool == "Business Card Generator":
    tools.business_card.render()
elif tool == "Welcome Aboard Generator":
    tools.welcome_aboard.render()
elif tool == "Coming Soon":
    st.title("Coming Soon")
    st.write("More tools will be added here.")
