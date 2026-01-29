import tools.business_card
import tools.welcome_aboard
import tools.dashboard

st.set_page_config(layout="wide", page_title="Business Card Generator")

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
